"""Contrats textuels PDF ; la recette visuelle reste dans tools/run_pdf_review.py."""
from decimal import Decimal
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
from unittest import skipUnless
from django.test import SimpleTestCase
from .pdf import document_response


@skipUnless(importlib.util.find_spec('reportlab') and shutil.which('pdftotext'), 'ReportLab et pdftotext requis')
class PdfContentTests(SimpleTestCase):
    def extract(self, response):
        with tempfile.TemporaryDirectory() as directory:
            pdf=Path(directory)/'test.pdf'
            pdf.write_bytes(b''.join(response.streaming_content));response.close()
            return subprocess.run(['pdftotext','-layout',str(pdf),'-'],check=True,capture_output=True,text=True).stdout.replace('\u00a0',' ').replace('\u202f',' ')

    def test_reference_line_and_french_total(self):
        text=self.extract(document_response('Reçu VEN-TEST',['Médicament','Qté','P.U. (Ar)','Total (Ar)'],[['Produit accentué',1,Decimal('15000'),Decimal('15000')]],Decimal('15000')))
        for fragment in ['VEN-TEST','Produit accentué','15 000,00','Total : 15 000,00 Ar']:
            self.assertIn(fragment,text)
        self.assertNotIn('15,000.00',text)

    def test_english_metadata_amount_is_presented_in_french(self):
        text=self.extract(document_response('Rapport',['Vente'],[['VEN-TEST']],meta=['Remboursements cumulés : 1,500.00 Ar']))
        self.assertIn('Remboursements cumulés : 1 500,00 Ar',text)

    def test_all_rows_and_repeated_headers_on_multiple_pages(self):
        rows=[[f'Produit accentué {i:03d}',1,Decimal('15000')] for i in range(80)]
        text=self.extract(document_response('Contrôle long',['Médicament','Qté','Total (Ar)'],rows))
        pages=[page for page in text.split('\f') if page.strip()]
        self.assertGreater(len(pages),1)
        for i in range(80):self.assertEqual(text.count(f'Produit accentué {i:03d}'),1)
        for page in pages:self.assertIn('Médicament',page)
