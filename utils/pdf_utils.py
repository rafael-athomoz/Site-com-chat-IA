"""
Módulo para extração de texto a partir de arquivos PDF usando PyMuPDF (fitz).

Funções:
---------
- extrair_texto_pdf(uploaded_file):
    Lê um arquivo PDF enviado (via upload), extrai todo o texto de cada página
    e retorna uma string única com o conteúdo completo.

Dependências:
--------------
- fitz (PyMuPDF): Para abrir e processar PDFs.
- streamlit (opcional): Para exibição de mensagens de erro.

Uso:
-----
texto = extrair_texto_pdf(arquivo_upload)
if texto:
    print("Texto extraído com sucesso!")
"""

import streamlit as st
import fitz


@st.cache_data
def extrair_texto_pdf(uploaded_file):
    """
    Extrai texto de um arquivo PDF enviado pelo usuário.

    Parâmetros:
    ------------
    uploaded_file : UploadedFile
        Objeto de arquivo carregado (ex: st.file_uploader).

    Retorna:
    ---------
    str | None
        Texto completo extraído do PDF ou None em caso de erro.
    """
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        texto = ""
        for pagina in doc:
            texto += pagina.get_text()

        return texto

    except Exception as e:
        st.error(f"Erro ao extrair texto do PDF: {e}")
        return None
