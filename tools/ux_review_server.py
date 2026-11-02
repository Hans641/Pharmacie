"""Serveurs de recette comparables et traces HTTP sans en-têtes ni corps."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
import threading
import time
from urllib.parse import urlsplit, parse_qs
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler


class RequestJournal:
    def __init__(self, path):
        self.path = Path(path)
        self.lock = threading.RLock()
        self.events = []
        self.path.write_text('')

    def record(self, event, **fields):
        with self.lock:
            item = dict(seq=len(self.events) + 1,
                        utc=datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                        monotonic=time.monotonic(), event=event,
                        thread=threading.current_thread().name, **fields)
            self.events.append(item)
            with self.path.open('a') as stream:
                stream.write(json.dumps(item, ensure_ascii=False) + '\n')

    def summary(self):
        with self.lock:
            counts = Counter(item['event'] for item in self.events)
            requests = [item for item in self.events if item['event'] == 'http_received']
            return dict(counts=dict(counts), requests_received=len(requests),
                        responses_completed=counts['response_end'], timeline=requests)


def safe_path(raw):
    parts = urlsplit(raw)
    # Seules les dates de la période sont utiles au diagnostic. Ni q ni token.
    query = parse_qs(parts.query)
    dates = {key: value for key, values in query.items() if key in ['start', 'end']
             for value in values[:1] if len(value) == 10 and all(c in '0123456789-' for c in value)}
    return parts.path, dates


def create_server(app, mode, journal):
    from django.core.servers.basehttp import ThreadedWSGIServer

    class Transport:
        def get_request(self):
            connection, address = super().get_request()
            with self.registry_lock:
                self.next_connection += 1
                self.clients[connection] = self.next_connection
                number = self.next_connection
            journal.record('connection_accepted', connection=number)
            return connection, address

        def close_request(self, connection):
            try:
                super().close_request(connection)
            finally:
                with self.registry_lock:
                    number = self.clients.pop(connection, None)
                if number is not None:
                    journal.record('connection_closed', connection=number)

        def close_clients(self):
            # Nettoyage uniquement après la fin de Chrome : ne pas masquer le blocage.
            with self.registry_lock:
                clients = list(self.clients)
            for connection in clients:
                try:
                    connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                connection.close()

    class SingleServer(Transport, WSGIServer):
        pass

    class ThreadServer(Transport, ThreadedWSGIServer):
        # Même taille de file et même handler HTTP/1.0 : seule la concurrence change.
        request_queue_size = WSGIServer.request_queue_size

    class Handler(WSGIRequestHandler):
        def handle(self):
            with self.server.registry_lock:
                self.connection_number = self.server.clients.get(self.request)
            journal.record('handler_started', connection=self.connection_number)
            super().handle()

        def parse_request(self):
            result = super().parse_request()
            if result:
                path, dates = safe_path(self.path)
                journal.record('headers_received', connection=self.connection_number,
                               method=self.command, path=path, dates=dates)
            return result

        def get_environ(self):
            environ = super().get_environ()
            environ['ux.connection'] = self.connection_number
            return environ

        def log_message(self, *args):
            pass

    def logged_app(environ, start_response):
        path, dates = safe_path(environ.get('PATH_INFO', '') + '?' + environ.get('QUERY_STRING', ''))
        fields = dict(connection=environ.get('ux.connection'), method=environ.get('REQUEST_METHOD'), path=path, dates=dates)
        journal.record('http_received', **fields)
        status = None
        response = None

        def start(status_line, headers, exc_info=None):
            nonlocal status
            status = int(status_line.split()[0])
            journal.record('response_start', status=status, **fields)
            return start_response(status_line, headers, exc_info)

        try:
            response = app(environ, start)
            yield from response
            journal.record('response_end', status=status, **fields)
        except Exception as error:
            journal.record('response_error', error_type=type(error).__name__, **fields)
            raise
        finally:
            if response is not None and hasattr(response, 'close'):
                response.close()

    journal.record('server_requested', mode=mode)
    server = make_server('127.0.0.1', 0, logged_app,
                         server_class=SingleServer if mode == 'single' else ThreadServer,
                         handler_class=Handler)
    server.clients = {}
    server.next_connection = 0
    server.registry_lock = threading.Lock()
    journal.record('server_listening', mode=mode, port=server.server_port)
    return server
