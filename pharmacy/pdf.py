"""Documents ReportLab ; moteur PDF texte de secours pour une installation hors ligne."""
from io import BytesIO
from html import escape
import textwrap
from django.conf import settings
from django.http import FileResponse
from django.utils.text import slugify


def document_response(title,headers,rows,total=None,meta=()):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    except ImportError:
        data=_plain_pdf(title,headers,rows,total,meta)
    else:
        data=BytesIO();styles=getSampleStyleSheet()
        story=[Paragraph(escape(settings.PHARMACY_NAME),styles['Title']),Paragraph(escape(settings.PHARMACY_ADDRESS),styles['Normal']),Spacer(1,16),Paragraph(escape(title),styles['Heading1'])]
        for line in meta: story.append(Paragraph(escape(str(line)),styles['Normal']))
        story.append(Spacer(1,16))
        table=Table([[Paragraph(escape(str(c)),styles['Normal']) for c in row] for row in [headers]+list(rows)],repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d8eee6')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#dce4e0'))]))
        story.append(table)
        if total is not None:story.extend([Spacer(1,16),Paragraph(f'Total : {total:,.2f} Ar',styles['Heading2'])])
        story.extend([Spacer(1,20),Paragraph(escape(settings.PHARMACY_LEGAL),styles['Normal'])])
        def footer(canvas,doc):
            canvas.setFont('Helvetica',8);canvas.drawRightString(800,20,f'Page {doc.page}')
        SimpleDocTemplate(data,pagesize=landscape(A4),title=title,author=settings.PHARMACY_NAME).build(story,onFirstPage=footer,onLaterPages=footer)
        data.seek(0)
    return FileResponse(data,content_type='application/pdf',as_attachment=True,filename=slugify(title)+'.pdf')


def _plain_pdf(title,headers,rows,total,meta):
    """PDF 1.4 multi-page, Helvetica WinAnsi ; aucun exécutable externe nécessaire."""
    lines=[settings.PHARMACY_NAME,settings.PHARMACY_ADDRESS,'',title,*map(str,meta),'',' | '.join(map(str,headers))]
    for row in rows:lines.extend(textwrap.wrap(' | '.join(map(str,row)),width=120) or [''])
    if total is not None:lines.extend(['',f'Total : {total:,.2f} Ar'])
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
