import streamlit as st
import fitz


@st.cache_data
def extrair_texto_pdf(uploaded_file):
    """
    Extrai o texto de um arquivo PDF carregado via Streamlit.

    Parâmetros:
    - uploaded_file: Arquivo PDF carregado via Streamlit (st.file_uploader)

    Retorno:
    - String com todo o texto extraído do PDF.
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
