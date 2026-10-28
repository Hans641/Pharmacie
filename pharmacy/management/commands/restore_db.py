import os,sqlite3,tempfile
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand,CommandError
from django.db import connections

class Command(BaseCommand):
    help='Restaure une sauvegarde SQLite vers un NOUVEAU fichier (ne remplace jamais la base active).'
    def add_arguments(self,parser):parser.add_argument('source');parser.add_argument('destination')
    def handle(self,*args,**options):
        src=Path(options['source']).resolve();dst=Path(options['destination']).resolve()
        if not src.is_file():raise CommandError('Sauvegarde introuvable.')
        if dst.exists():raise CommandError('La destination existe déjà ; restauration refusée.')
        if src==dst:raise CommandError('Source et destination identiques.')
        try:
            source=sqlite3.connect(src.as_uri()+'?mode=ro',uri=True)
            if source.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise CommandError('Sauvegarde corrompue.')
            tables={r[0] for r in source.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not {'django_migrations','pharmacy_medicine','auth_user'}<=tables:raise CommandError('Ce fichier n’est pas une base PharmaGest.')
            fd=os.open(dst,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
            try:
                target=sqlite3.connect(dst)
                try:
                    source.backup(target)
                    if target.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise CommandError('Restauration invalide.')
                    if target.execute('PRAGMA foreign_key_check').fetchone():raise CommandError('Relations incohérentes.')
                finally:target.close()
            except Exception:dst.unlink(missing_ok=True);raise
            finally:source.close()
        except sqlite3.DatabaseError as exc:raise CommandError('Sauvegarde SQLite illisible.') from exc
        self.stdout.write(self.style.SUCCESS(f'Base restaurée et vérifiée : {dst}. Serveur arrêté, définissez DATABASE_PATH vers ce fichier.'))
