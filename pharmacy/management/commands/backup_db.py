import os,sqlite3
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand,CommandError
from django.db import connections

class Command(BaseCommand):
    help='Sauvegarde cohérente SQLite dans un fichier privé (photos à sauvegarder séparément).'
    def add_arguments(self,parser):parser.add_argument('destination')
    def handle(self,*args,**options):
        if settings.DATABASES['default']['ENGINE']!='django.db.backends.sqlite3':raise CommandError('Utilisez pg_dump pour PostgreSQL.')
        path=Path(options['destination']).resolve()
        if not path.parent.is_dir():raise CommandError('Le dossier de destination doit exister.')
        try:
            fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
        except FileExistsError:raise CommandError('Ce fichier existe déjà ; choisissez un nouveau nom.')
        try:
            db=connections['default'];db.ensure_connection();source=db.connection
            dest=sqlite3.connect(str(path))
            try:
                source.backup(dest)
                if dest.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise CommandError('Contrôle d’intégrité échoué.')
            finally:dest.close()
        except Exception:
            path.unlink(missing_ok=True);raise
        self.stdout.write(self.style.SUCCESS(f'Sauvegarde vérifiée : {path}'))
