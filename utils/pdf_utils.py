"""
Módulo para extração de texto a partir de arquivos PDF.

Este módulo contém a funcionalidade principal para processar um arquivo PDF
e extrair todo o seu conteúdo de texto, consolidando-o em uma única string.
A extração é realizada utilizando a biblioteca PyMuPDF.

Funções:
---------
- `extrair_texto_pdf(uploaded_file)`:
    Processa um arquivo PDF fornecido (geralmente via upload em um aplicativo
    web) e extrai todo o texto de todas as suas páginas. O texto é concatenado
    e retornado como uma única string.

    Args:
        uploaded_file (streamlit.runtime.uploaded_file_manager.UploadedFile):
            O objeto de arquivo PDF enviado via upload pelo Streamlit.

    Returns:
        str: Uma string contendo o texto extraído de todas as páginas do PDF.
            Retorna uma string vazia se ocorrer um erro durante a leitura.

Dependências:
--------------
- `fitz` (PyMuPDF): A biblioteca principal utilizada para abrir, ler e extrair
    o conteúdo de texto de arquivos PDF.
- `streamlit`: (Contextual) A biblioteca de UI usada na aplicação principal
    que fornece o objeto `UploadedFile` como entrada para esta função. É
    também utilizada para exibir mensagens de erro ao usuário.

Uso:
-----
A função `extrair_texto_pdf` é projetada para ser chamada a partir da
aplicação principal, recebendo um arquivo PDF carregado pelo usuário.
O texto retornado pode ser usado para processamento posterior, como
análise por modelos de IA.

Exemplo de uso em um script Streamlit:
--------------------------------------
```python
import streamlit as st
from utils.pdf_utils import extrair_texto_pdf

uploaded_file = st.file_uploader("Carregar PDF", type="pdf")

if uploaded_file is not None:
    texto_do_pdf = extrair_texto_pdf(uploaded_file)
    if texto_do_pdf:
        st.success("Texto extraído com sucesso! Pronto para análise.")
        # Exemplo de como usar o texto extraído
        # st.text_area("Conteúdo do PDF", value=texto_do_pdf)
    else:
        st.error("Falha ao extrair o texto do arquivo PDF.")
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
