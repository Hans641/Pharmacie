"""Documents ReportLab ; moteur PDF texte de secours pour une installation hors ligne."""
from io import BytesIO
from html import escape
import textwrap
import re
from decimal import Decimal
from django.conf import settings
from django.http import FileResponse
from django.utils.text import slugify


def _amount(value):
    """Format de présentation, aucune modification du montant décimal."""
    return f'{Decimal(str(value)):,.2f}'.replace(',', ' ').replace('.', ',')


def _metadata(line):
    # Les vues existantes fournissent certains montants déjà formatés en anglais.
    return re.sub(r'(?<![\w.,])(-?(?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2}) Ar\b',
                  lambda match: _amount(match.group(1).replace(',', '')) + ' Ar', str(line))


def document_response(title,headers,rows,total=None,meta=()):
    money_columns = {i for i, header in enumerate(headers) if '(Ar)' in str(header)}
    numeric_columns = money_columns | {i for i, header in enumerate(headers) if str(header) in ['Qté', 'Stock', 'Reçu']}
    rows = [[_amount(cell) if i in money_columns else str(cell) for i,cell in enumerate(row)] for row in rows]
    meta = [_metadata(line) for line in meta]
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_RIGHT
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    except ImportError:
        data=_plain_pdf(title,headers,rows,total,meta)
    else:
        data=BytesIO();styles=getSampleStyleSheet()
        body=ParagraphStyle('CellBody',parent=styles['Normal'],fontSize=9,leading=12)
        number=ParagraphStyle('CellNumber',parent=body,alignment=TA_RIGHT)
        heading=ParagraphStyle('CellHeading',parent=body,fontName='Helvetica-Bold')
        numeric_heading=ParagraphStyle('NumericHeading',parent=heading,alignment=TA_RIGHT)
        doc=SimpleDocTemplate(data,pagesize=landscape(A4),leftMargin=36,rightMargin=36,topMargin=40,bottomMargin=48,title=title,author=settings.PHARMACY_NAME)
        story=[Paragraph(escape(settings.PHARMACY_NAME),styles['Title']),Paragraph(escape(settings.PHARMACY_ADDRESS),styles['Normal']),Spacer(1,10),Paragraph(escape(title),styles['Heading1'])]
        for line in meta: story.append(Paragraph(escape(line),styles['Normal']))
        story.append(Spacer(1,12))
        weights=[]
        for i,header in enumerate(headers):
            label=str(header)
            weights.append(3.8 if label=='Médicament' else 2.4 if label=='Fournisseur' else 1.5 if i in money_columns else .7 if i in numeric_columns else 1.5)
        widths=[doc.width*weight/sum(weights) for weight in weights]
        cells=[[Paragraph(escape(str(c)),numeric_heading if i in numeric_columns else heading) for i,c in enumerate(headers)]]
        cells += [[Paragraph(escape(c),number if i in numeric_columns else body) for i,c in enumerate(row)] for row in rows]
        table=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d8eee6')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#dce4e0'))]))
        story.append(table)
        if total is not None:
            total_style=ParagraphStyle('DocumentTotal',parent=styles['Heading2'],alignment=TA_RIGHT)
            story.extend([Spacer(1,12),Paragraph('Total : '+_amount(total)+' Ar',total_style)])
        def footer(canvas,document):
            canvas.saveState()
            if document.page>1:
                canvas.setFont('Helvetica',8)
                canvas.drawString(document.leftMargin,document.pagesize[1]-22,title)
            legal=Paragraph(escape(settings.PHARMACY_LEGAL),ParagraphStyle('LegalFooter',fontName='Helvetica',fontSize=7,leading=8))
            _,height=legal.wrap(document.width-65,32)
            legal.drawOn(canvas,document.leftMargin,16)
            canvas.setFont('Helvetica',8)
            canvas.drawRightString(document.pagesize[0]-document.rightMargin,16,f'Page {document.page}')
            canvas.restoreState()
        doc.build(story,onFirstPage=footer,onLaterPages=footer)
        data.seek(0)
    return FileResponse(data,content_type='application/pdf',as_attachment=True,filename=slugify(title)+'.pdf')


def _plain_pdf(title,headers,rows,total,meta):
    """PDF 1.4 multi-page, Helvetica WinAnsi ; aucun exécutable externe nécessaire."""
    lines=[settings.PHARMACY_NAME,settings.PHARMACY_ADDRESS,'',title,*map(str,meta),'',' | '.join(map(str,headers))]
    for row in rows:lines.extend(textwrap.wrap(' | '.join(map(str,row)),width=120) or [''])
    if total is not None:lines.extend(['','Total : '+_amount(total)+' Ar'])
    lines.extend(['',settings.PHARMACY_LEGAL])
    pages=[lines[i:i+43] for i in range(0,len(lines),43)]
    objects=[b'',b'',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>']
    kids=[]
    for index,chunk in enumerate(pages):
        page_id=len(objects)+1;content_id=page_id+1;kids.append(f'{page_id} 0 R')
        objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 842 595] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>'.encode())
        commands=['BT /F1 10 Tf 35 560 Td 12 TL']
        for line in chunk+[f'Page {index+1}/{len(pages)}']:
            escaped=str(line).replace('\\','\\\\').replace('(','\\(').replace(')','\\)').replace('\n',' ')
            commands.append(f'({escaped}) Tj T*')
        stream=('\n'.join(commands)+'\nET').encode('cp1252',errors='replace')
        objects.append(f'<< /Length {len(stream)} >>\nstream\n'.encode()+stream+b'\nendstream')
    objects[0]=b'<< /Type /Catalog /Pages 2 0 R >>'
    objects[1]=('<< /Type /Pages /Count '+str(len(pages))+' /Kids ['+' '.join(kids)+'] >>').encode()
    buf=BytesIO();buf.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n');offsets=[0]
    for i,obj in enumerate(objects,1):offsets.append(buf.tell());buf.write(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
    xref=buf.tell();buf.write(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
    for off in offsets[1:]:buf.write(f'{off:010d} 00000 n \n'.encode())
    buf.write(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF'.encode());buf.seek(0)
    return buf
