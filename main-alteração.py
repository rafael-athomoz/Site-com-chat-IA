import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF
import pandas as pd
from io import BytesIO
import json

# Carrega variáveis de ambiente
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("Erro: A chave da API da OpenAI não foi encontrada.")
    st.stop()

client = OpenAI(api_key=api_key)

@st.cache_data
def extrair_texto_pdf(uploaded_file):
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        texto = "".join([p.get_text() for p in doc])
        return texto
    except Exception as e:
        st.error(f"Erro ao extrair texto do PDF: {e}")
        return None

def gerar_excel_documentos(dados_completos):
    output = BytesIO()
    try:
        # Resumo do edital
        df_resumo = pd.json_normalize([dados_completos.get("Resumo do Edital", {})])

        # Documentos de habilitação, credenciamento e garantias
        df_hab = pd.json_normalize(dados_completos.get("Documentos de Habilitacao", []))
        df_cred = pd.json_normalize(dados_completos.get("Documentos de Credenciamento", []))
        df_gar = pd.json_normalize(dados_completos.get("Garantias Exigidas", []))

        # Reordena colunas e preenche ausentes
        cols_docs = ["Tipo do Documento", "Nome do Documento", "Obrigatoriedade",
                     "Localização da Informação", "Observacoes"]
        df_hab = df_hab.reindex(columns=cols_docs, fill_value="")
        df_cred = df_cred.reindex(columns=cols_docs, fill_value="")

        cols_gar = ["Tipo de Garantia", "Nome da Garantia", "Valor ou Porcentagem",
                    "Localização da Informação"]
        df_gar = df_gar.reindex(columns=cols_gar, fill_value="")

        # Grava em abas no Excel
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_resumo.to_excel(writer, sheet_name="Resumo do Edital", index=False)
            df_hab.to_excel(writer, sheet_name="Documentos de Habilitacao", index=False)
            df_cred.to_excel(writer, sheet_name="Documentos de Credenciamento", index=False)
            df_gar.to_excel(writer, sheet_name="Garantias", index=False)

        output.seek(0)
        return output

    except Exception as e:
        st.error(f"Erro ao gerar Excel: {e}")
        return None

# Interface Streamlit
st.image("assets/holy dragon logo.png", width=600)
st.title("📑 Leitor de Edital 1.0")

arquivo_pdf = st.file_uploader("📤 Envie um PDF de edital para análise", type="pdf")
if "contexto_pdf" not in st.session_state:
    st.session_state["contexto_pdf"] = ""

if arquivo_pdf:
    texto = extrair_texto_pdf(arquivo_pdf)
    if texto:
        st.session_state["contexto_pdf"] = texto
        st.success("✅ Texto extraído com sucesso.")

if st.session_state["contexto_pdf"]:
    if st.button("📊 Analisar PDF e gerar planilha completa do edital"):
        with st.spinner("Analisando o edital..."):
            prompt = f"""... mesmo prompt detalhado ... "{st.session_state['contexto_pdf'][:10000]}" """
            resposta = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type":"json_object"},
                messages=[{"role":"user","content":prompt}]
            )
            dados = json.loads(resposta.choices[0].message.content)
            excel = gerar_excel_documentos(dados)
            if excel:
                st.success("📥 Planilha gerada!")
                st.download_button(
                    "⬇️ Baixar planilha completa do edital",
                    data=excel,
                    file_name="analise_edital.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("Erro ao gerar planilha.")

# Chat UI permanece igual ao seu
