# Titilo
# Input Chat
# -> a cada mensagem enviada:
# Vai mostrar a mensagem que o usuário enviou no chat
# envia a mensagem para a IA que analisa a mensagem afim de responder
# a IA responde na tela a mensagem


# streamlit - Frontend e Backend

import streamlit as st
from openai import OpenAI

# Cria cliente OpenAI
client = OpenAI(
    api_key="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"
)

# Título da página
st.write("# ChatBot com IA")

# Inicializa memória
if "lista_mensagens" not in st.session_state:
    st.session_state["lista_mensagens"] = []

# Exibe histórico
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
    st.chat_message("assistant").write(resposta_ia)
    mensagem_ia = {"role": "assistant", "content": resposta_ia}
    st.session_state["lista_mensagens"].append(mensagem_ia)
