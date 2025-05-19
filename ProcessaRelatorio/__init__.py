import logging
import os
import pdfplumber
import pandas as pd
import azure.functions as func

def extrair_tabelas_pdf(pdf_path, pagina=0):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[pagina]
        tables_raw = page.extract_tables()
        tabelas = [pd.DataFrame(t[1:], columns=t[0]) for t in tables_raw]
        return tabelas

def gerar_html(df):
    return df.to_html(index=False)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Função Azure chamada com sucesso.')

    pdf_path = req.params.get('pdf_path')
    if not pdf_path:
        return func.HttpResponse("Parâmetro 'pdf_path' não fornecido.", status_code=400)

    if not os.path.exists(pdf_path):
        return func.HttpResponse(f"Arquivo não encontrado: {pdf_path}", status_code=404)

    try:
        tabelas = extrair_tabelas_pdf(pdf_path)
        if not tabelas:
            return func.HttpResponse("Nenhuma tabela encontrada no PDF.", status_code=204)

        html = gerar_html(tabelas[0])
        return func.HttpResponse(html, mimetype="text/html")

    except Exception as e:
        logging.error(f"Erro ao processar o PDF: {str(e)}")
        return func.HttpResponse("Erro ao processar o PDF.", status_code=500)


#http://localhost:7071/api/ProcessaRelatorio?pdf_path=C:\power_automate\relatorios\relatorio_1.pdf