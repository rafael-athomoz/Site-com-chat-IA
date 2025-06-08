# Titilo
# Input Chat
# -> a cada mensagem enviada:
# Vai mostrar a mensagem que o usuário enviou no chat
# envia a mensagem para a IA que analisa a mensagem afim de responder
# a IA responde na tela a mensagem


# streamlit - Frontend e Backend


import streamlit as st
from openai import OpenAI


modelo = OpenAI(
    api_key="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"
)
st.write("# ChatBot com IA")

# session_state  é a memória do aplicativo

if not "lista_mensagem" in st.session_state:
    st.session_state["lista_mensagens"] = []

# exibir o histórico de mensagem
for historico_mensagem in st.session_state["lista_mensagens"]:
    role = historico_mensagem["role"]
    content = historico_mensagem["content"]
    st.chat_message(role).write(content)

mensagens_usuario = st.chat_input("Escreva mensagem para o Rafael IA Responder ")
# role =  quem envia a mensagem = "função"
# content = texto da mensagem = "conteúdo"

if mensagens_usuario:
    # integra a IA
    st.chat_message("user").write(mensagens_usuario)
    mensagem = {"role": "user", "content": mensagens_usuario}
    st.session_state["lista_mensagens"].append(mensagem)

    # resposta da IA
    resposta_modelo = modelo.chat.completions.create(
        messages=st.session_state["lista_mensagens"], model="gpt-3.5-turbo"
    )

    print(resposta_modelo)
    resposta_ia = resposta_modelo.choices[0].message

    # exibi a resposta na tela
    st.chat_message("assistant").write(resposta_ia)
    mensagem_ia = {"role": "assistant", "content": resposta_ia}
    st.session_state["lista_mensagens"].append(mensagem_ia)

    # print(st.session_state["lista_mensagens"])
