from fastapi.responses import FileResponse, StreamingResponse
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import tempfile
from io import BytesIO

def genera_html(dati_json: dict) -> str:
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("scheda.html")
    return template.render(dati_json)

'''
def genera_pdf(dati_json, report_id):
    html_str = genera_html(dati_json)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pisa.CreatePDF(html_str, dest=open(tmp.name, "wb"))
        return FileResponse(tmp.name, media_type="application/pdf", filename=f"report_{report_id}.pdf")
'''

def genera_pdf(dati_json, report_id):
    html_str = genera_html(dati_json)
    pdf_bytes = BytesIO()  # crea un buffer in memoria
    pisa.CreatePDF(html_str, dest=pdf_bytes)
    pdf_bytes.seek(0)  # riporta il cursore all'inizio per la lettura

    headers = {
        "Content-Disposition": f'attachment; filename="report_{report_id}.pdf"'
    }

    return StreamingResponse(
        pdf_bytes,
        media_type="application/pdf",
        headers=headers
    )