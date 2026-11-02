"""Contrats de journalisation et de comparabilité, sans socket réseau."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import patch
from tools.ux_review_server import RequestJournal, create_server


class JournalTests(TestCase):
    def test_concurrent_records_remain_complete_and_ordered(self):
        with TemporaryDirectory() as work:
            journal = RequestJournal(Path(work) / 'requests.jsonl')
            with ThreadPoolExecutor(max_workers=5) as pool:
                list(pool.map(lambda index: journal.record('sample', index=index), range(50)))
            rows = [json.loads(line) for line in journal.path.read_text().splitlines()]
            self.assertEqual([row['seq'] for row in rows], list(range(1, 51)))
            self.assertEqual({row['index'] for row in rows}, set(range(50)))
            self.assertTrue(all(row['utc'].endswith('+00:00') for row in rows))

    def test_request_counts_and_safe_timeline(self):
        with TemporaryDirectory() as work:
            journal = RequestJournal(Path(work) / 'requests.jsonl')
            def app(environ, start):
                start('200 OK', [('Content-Type', 'text/plain')])
                return [b'ok']
            with patch('tools.ux_review_server.make_server', return_value=SimpleNamespace(server_port=8000)) as factory:
                create_server(app, 'single', journal)
                wrapped = factory.call_args.args[2]
                response = wrapped({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/', 'QUERY_STRING': 'start=2000-01-01&token=do-not-log-me', 'HTTP_COOKIE': 'session=do-not-log-me'}, lambda status, headers, exc=None: None)
                self.assertEqual(list(response), [b'ok'])
            result = journal.summary()
            self.assertEqual(result['requests_received'], 1)
            self.assertEqual(result['responses_completed'], 1)
            self.assertEqual(result['timeline'][0]['dates'], {'start': '2000-01-01'})
            self.assertNotIn('do-not-log-me', journal.path.read_text())

    def test_server_modes_share_handler_and_queue(self):
        from django.core.servers.basehttp import ThreadedWSGIServer
        with TemporaryDirectory() as work:
            journal = RequestJournal(Path(work) / 'requests.jsonl')
            classes = []
            handlers = []
            for mode in ['single', 'threaded']:
                with patch('tools.ux_review_server.make_server', return_value=SimpleNamespace(server_port=8000)) as factory:
                    create_server(lambda env, start: [], mode, journal)
                    classes.append(factory.call_args.kwargs['server_class'])
                    handlers.append(factory.call_args.kwargs['handler_class'])
            self.assertFalse(issubclass(classes[0], ThreadedWSGIServer))
            self.assertTrue(issubclass(classes[1], ThreadedWSGIServer))
            self.assertEqual(classes[0].request_queue_size, classes[1].request_queue_size)
            self.assertEqual(handlers[0].__bases__, handlers[1].__bases__)


if __name__ == '__main__':
    main()
