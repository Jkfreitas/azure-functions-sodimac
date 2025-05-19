import logging
import azure.functions as func
import base64
import tempfile
import pdfplumber
import pandas as pd

def extrair_tabelas_pdf(pdf_path, pagina=0):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[pagina]
        tables_raw = page.extract_tables()
        tabelas = [pd.DataFrame(t[1:], columns=t[0]) for t in tables_raw]
        return tabelas

def gerar_html(df):
    return df.to_html(index=False)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Azure Function chamada com sucesso.')

    try:
        req_body = req.get_json()
        file_base64 = req_body.get('file_base64')

        if not file_base64:
            return func.HttpResponse("Campo 'file_base64' não fornecido.", status_code=400)

        # Salvar o conteúdo base64 como um arquivo temporário
        pdf_bytes = base64.b64decode(file_base64)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        tabelas = extrair_tabelas_pdf(tmp_file_path)
        if not tabelas:
            return func.HttpResponse("Nenhuma tabela encontrada no PDF.", status_code=204)

        html = gerar_html(tabelas[0])
        return func.HttpResponse(html, mimetype="text/html")

    except Exception as e:
        logging.error(f"Erro ao processar o PDF: {str(e)}")
        return func.HttpResponse("Erro interno ao processar o PDF.", status_code=500)



#http://localhost:7071/api/ProcessaRelatorio?pdf_path=C:\power_automate\relatorios\relatorio_1.pdf
