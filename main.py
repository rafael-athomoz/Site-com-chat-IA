# Titilo
# Input Chat
# -> a cada mensagem enviada:
# Vai mostrar a mensagem que o usuário enviou no chat
# envia a mensagem para a IA que analisa a mensagem afim de responder
# a IA responde na tela a mensagem


# streamlit - Frontend e Backend

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF para ler PDFs

# Carrega variáveis do .env
load_dotenv()

# Lê a API KEY
api_key = os.getenv("OPENAI_API_KEY")

# Cria cliente OpenAI
client = OpenAI(api_key=api_key)


# Título da página
st.write("# Análise de edital")

# Inicializa memória
if "lista_mensagens" not in st.session_state:
    st.session_state["lista_mensagens"] = []

# Exibe histórico
st.subheader("Chat bot da sua Empresa")
for historico_mensagem in st.session_state["lista_mensagens"]:
    role = historico_mensagem["role"]
    content = historico_mensagem["content"]
    st.chat_message(role).write(content)

# Entrada do usuário
mensagem_usuario = st.chat_input("Escreva mensagem para o Rafael IA responder")

if mensagem_usuario:
    # Mostra mensagem do usuário
    st.chat_message("user").write(mensagem_usuario)
    mensagem = {"role": "user", "content": mensagem_usuario}
    st.session_state["lista_mensagens"].append(mensagem)

    # Chamada nova para a API OpenAI
    resposta_modelo = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=st.session_state["lista_mensagens"]
    )

    resposta_ia = resposta_modelo.choices[0].message.content.strip()

    # Mostra resposta da IA
    with st.chat_message("assistant"):
        with st.expander("Expandir resposta"):
            st.write(resposta_ia)
    mensagem_ia = {"role": "assistant", "content": resposta_ia}
    st.session_state["lista_mensagens"].append(mensagem_ia)

# __________________
# Ler arquivo PDF
# _________________

st.subheader("Análise do arquivo PDF")
arquivo_pdf = st.file_uploader("Selecione o arquivo PDF", type=["pdf"])

if arquivo_pdf is not None:
    # Ler arquivo PDF
    arquivo_pdf = fitz.open(stream=arquivo_pdf.read(), filetype="pdf")
    texto_pdf = ""
    for pagina in arquivo_pdf:
        texto_pdf += pagina.get_text()

    st.write("## Texto do arquivo PDF")
    st.markdown(
        f"<div style='overflow-x:auto; overflow-y:auto; max-height:400px;'>{texto_pdf}</div>",
        unsafe_allow_html=True,
    )

    pergunta_pdf = st.text_input("Digite sa pergunta em relação ao PDF: ")

    if st.button("Enviar pergunta"):
        if pergunta_pdf.strip() != "":
            resposta_pdf = f"Com base no texto do PDF, a resposta é: \n\n {texto_pdf}"
            resposta_pdf = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": resposta_pdf}],
            )

            resposta_pdf_ia = resposta_pdf.choices[0].message.content.strip()

            with st.chat_message("assistant"):
                with st.expander("Expandir resposta"):
                    st.write(resposta_pdf_ia)
        else:
            st.warning("Digite uma pergunta!")
