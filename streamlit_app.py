"""
Módulo para geração de arquivos Excel a partir de dados de editais públicos.

Este módulo contém funções utilitárias que transformam dados estruturados
(geralmente em formato JSON) extraídos de editais de pregão em arquivos
Excel formatados para download. O objetivo é facilitar a consulta e o
gerenciamento das informações processadas.

Funções:
---------
- `gerar_excel_resumo(dados_para_excel)`:
    Gera um arquivo Excel com um resumo completo do edital.
    Args:
        dados_para_excel (dict): Dicionário contendo as informações resumidas do edital.
    Returns:
        io.BytesIO: Objeto de arquivo em memória contendo o arquivo Excel gerado.

- `gerar_excel_credenciamento(dados_para_excel)`:
    Cria um arquivo Excel listando todos os documentos necessários para o
    credenciamento, incluindo o nome do documento, exigência, localização
    no edital e observações relevantes.
    Args:
        dados_para_excel (dict): Dicionário com os dados de credenciamento.
    Returns:
        io.BytesIO: Objeto de arquivo em memória.

- `gerar_excel_habilitacao(dados_para_excel)`:
    Produz um arquivo Excel detalhando os documentos exigidos para a
    habilitação no processo licitatório, com informações sobre a exigência,
    localização e observações.
    Args:
        dados_para_excel (dict): Dicionário com os dados de habilitação.
    Returns:
        io.BytesIO: Objeto de arquivo em memória.

- `gerar_excel_extras(dados_para_excel)`:
    Elabora um arquivo Excel focado em documentos adicionais ou específicos
    identificados pela IA que não se enquadram nas categorias padrão
    de credenciamento ou habilitação.
    Args:
        dados_para_excel (dict): Dicionário com os dados dos documentos extras.
    Returns:
        io.BytesIO: Objeto de arquivo em memória.

Dependências:
--------------
- `pandas`: Biblioteca essencial para a criação e manipulação eficiente
    de planilhas de dados e para a exportação final para o formato Excel.
- `io.BytesIO`: Fornece uma interface de buffer de E/S em memória, permitindo
    que os arquivos Excel sejam criados e manipulados na RAM sem a necessidade
    de salvá-los temporariamente no disco.
- `streamlit`: Usada na aplicação principal para gerenciar a interface,
    especificamente para exibir os botões de download e mensagens de feedback.

Uso:
-----
As funções deste módulo são integradas a um aplicativo Streamlit que lê
editais em PDF. Após a extração e o processamento dos dados por uma IA,
as funções são chamadas para gerar planilhas Excel que podem ser baixadas
diretamente pelo usuário.

Exemplo de uso:
----------------
```python
# Supondo que 'dados_processados' seja um dicionário com os dados extraídos
dados_processados = {"Resumo do Edital": {...}}

# Chama a função para gerar o arquivo Excel
arquivo_excel_resumo = gerar_excel_resumo(dados_processados)

if arquivo_excel_resumo:
    # Cria um botão de download no Streamlit para o arquivo
    st.download_button(
        label="Baixar Planilha Resumo",
        data=arquivo_excel_resumo,
        file_name="resumo_do_edital.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
"""
# import os
import json

import streamlit as st
# from dotenv import load_dotenv
from openai import OpenAI
import bcrypt

# extrair_texto_pdf
from utils.pdf_utils import extrair_texto_pdf
from utils.admin_utils import add_user_page
from credentials import USERS_HASHES


# gerar_excel_resumo, gerar_excel_habilitacao, gerar_excel_credenciamento
from utils.excel_utils import (
    gerar_excel_resumo,
    gerar_excel_habilitacao,
    gerar_excel_credenciamento,
    gerar_excel_extras
    )


# SECTION LOGIN ----------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


def mostra_login():
    """ Função para gerar tela de acesso do usuários"""
    st.title("🔒 Acesso Restrito")
    st.image("assets/holy dragon logo.png", width=600)
    st.markdown("---")

    username = st.text_input("Usuário")
    password = st.text_input("senha", type="password")

    if st.button("Entrar"):
        if username in USERS_HASHES:
            hashed_senha_armazenada = USERS_HASHES[username].encode('utf-8')
            senha_digitada = password.encode('utf-8')

            if bcrypt.checkpw(senha_digitada, hashed_senha_armazenada):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Bem-vindo, {username}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        else:
            st.error("Usuário ou senha incorretos.")


# Verifica se o usuário está logado
if not st.session_state.get("logged_in"):
    mostra_login()
else:
    # Carrega variáveis de ambiente
    api_key = st.secrets["OPENAI_API_KEY"]

    # Apenas para ambiente de desenvolvimento
    # load_dotenv()

    if not api_key:
        st.error("""Erro: A chave da API da OpenAI não foi encontrada.
                    Certifique-se de que OPENAI_API_KEY está definida no seu arquivo .env.""")
        st.stop()

    client = OpenAI(api_key=api_key)

    col1, col2 = st.columns([10, 1])
    with col1:
        st.image("assets/holy dragon logo.png", width=600)
        st.title("📑 Leitor de Edital 1.0")

    with col2:
        if st.button("Sair"):
            st.session_state["logged_in"] = False
            del st.session_state["username"]
            st.rerun()

    if st.session_state["username"] == "Rafael Fortunato":
        if st.button("Gerenciar Usuários", key="admin_button"):
            # Alterna para Mostrar a pagina de administração
            st.session_state["show_admin"] = not st.session_state.get("show_admin", False)

        if st.session_state.get("show_admin"):
            add_user_page()
            # impede a execução do restante do script se a pagina admin estiver carregada
            st.stop()

    # SECTION UPLOAD PDF ---------------------------------------------------------------
    arquivo_pdf = st.file_uploader("📤 Envie um PDF de edital para análise", type="pdf")

    if "lista_mensagens" not in st.session_state:
        st.session_state["lista_mensagens"] = []
    if "contexto_pdf" not in st.session_state:
        st.session_state["contexto_pdf"] = ""
    if "pdf_carregado_nome" not in st.session_state:
        st.session_state["pdf_carregado_nome"] = None

    # SECTION PDF PROCESSING ------------------------------------------------------------
    if arquivo_pdf and arquivo_pdf.name != st.session_state["pdf_carregado_nome"]:
        st.session_state["pdf_carregado_nome"] = arquivo_pdf.name
        with st.spinner("Extraindo texto do PDF..."):
            texto_extraido = extrair_texto_pdf(arquivo_pdf)
            if texto_extraido:
                st.session_state["contexto_pdf"] = texto_extraido
                st.success("✅ PDF carregado e texto extraído com sucesso.")
                st.session_state["lista_mensagens"] = []
            else:
                st.session_state["contexto_pdf"] = ""

    # SECTION PROMPTS ---------------------------------------------------------------------
    if st.session_state["contexto_pdf"]:  # resumo edital prompt
        if st.button("📊 Analisar PDF e gerar planilha com Resumo do edital"):
            with st.spinner("Analisando o edital e gerando a planilha..."):
                # --- NOVO PROMPT ALTAMENTE ESPECÍFICO PARA EXTRAÇÃO COMPLETA ---
                PROMPT_COMPLETO_RESUMO = f"""
                Você é um especialista em leitura técnica e detalhada de editais públicos de pregão.
                Sua tarefa é extrair **todas as informações essenciais e documentos exigidos** mantendo
                a exatidão da informação do edital fornecido, organizando-as em um
                **objeto JSON complexo** com as seguintes chaves e estruturas exatas:

                "Resumo do Edital": {{
                    "Objeto": {{
                        "Descrição": "Descrição concisa do objeto do edital.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Modalidade do Pregão": {{
                        "Descrição": "Ex: Pregão Eletrônico, Presencial.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Modo de Disputa": {{
                        "Descrição": "Ex: Aberto, Fechado, Livre.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Tipo de Julgamento": {{
                        "Tipo de Julgamento do objeto licitado": "Ex: Menor Preço, Melhor Técnica.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Data e Horário de Abertura": {{
                        "Descrição": "Data e hora exatas da abertura do pregão.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Endereço de entrega do objeto": {{
                        "Descrição": "Endereço completo para entrega do objeto.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Critérios de Avaliação": {{
                        "Descrição": "Critérios utilizados para avaliação das propostas.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Valor estimado total": {{
                        "Descrição": "Valor total estimado do objeto licitado.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Plataforma onde ocorrerá o pregão": {{
                        "Descrição": "Plataforma eletrônica onde o pregão será realizado.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Validade dos Documentos de Habilitação ": {{
                        "Descrição": "Validade dos documentos exigidos para habilitação econômico/financeira.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Período de envio dos documentos de Habilitação": {{
                        "Descrição": "Período para envio dos documentos de habilitação.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Modelos de garantias exigidas": {{
                        "Descrição": "Modelos de garantias exigidas, modelo de garantia on-site ou por item, se houver.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Prazo de envio da Proposta readequada": {{
                        "Descrição": "Prazo para envio de propostas readequadas, se aplicável.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Pede apresentação de catálogo": {{
                        "Descrição": "Exigência de apresentação de catálogo.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Qual o período de apresentação do Catálogo": {{
                        "Descrição": "Apresentação quando solicitado ou na apresentação da proposta",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Exigência de atestado do Objeto ou quantitativo e sua porcentagem": {{
                        "Descrição": "Exigência de atestado de capacidade técnica e porcentagem mínima.",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }},
                    "Contatos para informações": {{
                        "Descrição": "E-mail ou telefone de contato",
                        "Localização da Informação": "Item/Cláusula/Título no edital"
                    }}
                }},
                **Instruções Cruciais:**
                1.  **Analise todo o edital com extrema atenção** para não perder nenhum detalhe.
                2.  **Preencha TODOS os campos** no objeto "Resumo do Edital". Se a informação não for encontrada,
                indique explicitamente "Não informado" ou deixe em branco, mas não omita o campo.
                4.  Para cada documento, detalhe se é "Obrigatório", a "Localização da Informação" (Item/Cláusula) e
                    quaisquer "Observações" pertinentes (prazos de emissão, requisitos de autenticação, etc.).
                6.  **A saída DEVE ser um JSON válido e completo**, com todas as chaves solicitadas, mesmo que as listas
                    estejam vazias se nenhuma informação for encontrada.

                **Conteúdo do Edital:**
                \"\"\"
                {st.session_state["contexto_pdf"][:50000]}
                \"\"\"
                """

                # --- FIM DO NOVO PROMPT ---

                try:
                    resposta = client.chat.completions.create(
                        model="gpt-4o",  # Usar o modelo mais capaz para extração detalhada
                        response_format={"type": "json_object"},  # Garantir que a saída seja JSON
                        messages=[{"role": "user", "content": PROMPT_COMPLETO_RESUMO}]
                    )
                    resposta_json_str = resposta.choices[0].message.content.strip()
                    dados_completos = json.loads(resposta_json_str)

                    if dados_completos:
                        arquivo_excel = gerar_excel_resumo(dados_completos)
                        if arquivo_excel:
                            st.success("📥 Planilha completa do edital gerada com sucesso!")
                            st.download_button(
                                label="⬇️ Baixar planilha Resumo do edital",
                                data=arquivo_excel,
                                file_name=st.session_state["pdf_carregado_nome"].replace(".pdf", "_resumo.xlsx"),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            st.warning("Nenhuma informação foi gerada ou houve um erro na criação do Excel.")
                    else:
                        st.warning("A IA não retornou um JSON de análise completo. Verifique o prompt ou o edital.")
                        st.code(resposta_json_str)
                except json.JSONDecodeError as e:
                    st.error(f"Erro ao decodificar JSON da IA. O formato de saída pode estar incorreto: {e}")
                    st.code(resposta_json_str)
                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar a solicitação: {e}")

        st.markdown("---")

    if st.session_state["contexto_pdf"]:  # Credenciamento edital prompt
        if st.button("📊 Analisar PDF e gerar planilha de Credenciamento do edital"):
            with st.spinner("Analisando o edital e gerando a planilha..."):
                # --- NOVO PROMPT ALTAMENTE ESPECÍFICO PARA EXTRAÇÃO COMPLETA ---
                PROMPT_COMPLETO_CREDENCIAMENTO = f"""
                Você é um especialista em leitura técnica de editais públicos de pregão. Sua tarefa é identificar e
                extrair informações sobre os documentos exigidos para credenciamento, mesmo que apresentados de
                formas variadas.
                Para cada documento encontrado, forneça as seguintes informações:

                -**Exigência**: Indique se o documento é "Obrigatório", "Opcional" ou "Não informado".
                -**Localização da Informação**: Informe o item, cláusula ou seção onde o documento é mencionado.
                -**Observações**: Quaisquer detalhes adicionais relevantes, como prazos de validade, requisitos
                específicos ou condições especiais.

                "Credenciamento do Edital": {{
                    "Contrato Social": {{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Documento de Identidade do sócio RG e CPF": {{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Certidão simplificada da JUCESP (ou da junta comercial de qualquer estado)": {{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Documento de Optante pelo Simples Nacional": {{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Procuração de Representante Legal": {{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }}
                }}

                **Instruções Cruciais:**
                1.  **Analise o arquivo carregado com foco na secção ou trecho de Credenciamento com extrema atenção**
                    para não perder nenhum detalhe.
                2.  **Preencha TODOS os campos** no objeto "Credenciamento do Edital". Se a informação não for
                encontrada, indique explicitamente "Não informado" ou deixe em branco, mas não omita o campo.
                3.  Para as listas de documentos (Credenciamento do Edital) , inclua **TODOS os itens
                    encontrados no edital**, mesmo que pareçam óbvios ou genéricos.
                4.  Para cada documento, detalhe se é "Obrigatório", a "Localização da Informação do documento"
                    (Item/Cláusula) e quaisquer "Observações" pertinentes (prazos de emissão, requisitos de
                    autenticação, etc.).
                5.  **A saída DEVE ser um JSON válido e completo**, com todas as chaves solicitadas, mesmo que as listas
                    estejam vazias se nenhuma informação for encontrada.

                **Conteúdo do Edital:**
                \"\"\"
                {st.session_state["contexto_pdf"][:30000]}
                \"\"\"
                """

                # --- FIM DO NOVO PROMPT ---

                try:
                    resposta = client.chat.completions.create(
                        model="gpt-4o",  # Usar o modelo mais capaz para extração detalhada
                        response_format={"type": "json_object"},  # Garantir que a saída seja JSON
                        messages=[{"role": "user", "content": PROMPT_COMPLETO_CREDENCIAMENTO}]
                    )
                    resposta_json_str = resposta.choices[0].message.content.strip()
                    # --- TESTE: visualizar a saída JSON no terminal ---
                    # print("\n===== JSON RETORNADO PELA IA (RAW) =====")
                    # print(resposta_json_str)
                    # print("========================================\n")
                    dados_completos = json.loads(resposta_json_str)
                    # print("\n===== JSON CARREGADO (DICT PYTHON) =====")
                    # print(json.dumps(dados_completos, indent=4, ensure_ascii=False))
                    # print("========================================\n")

                    if dados_completos:
                        arquivo_excel = gerar_excel_credenciamento(dados_completos)
                        if arquivo_excel:
                            st.success("📥 Planilha completa do edital gerada com sucesso!")
                            st.download_button(
                                label="⬇️ Baixar planilha Credenciamento do edital",
                                data=arquivo_excel,
                                file_name=st.session_state["pdf_carregado_nome"].replace(
                                    ".pdf", "_credenciamento.xlsx"),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            st.warning("Nenhuma informação foi gerada ou houve um erro na criação do Excel.")
                    else:
                        st.warning("A IA não retornou um JSON de análise completo. Verifique o prompt ou o edital.")
                        st.code(resposta_json_str)
                except json.JSONDecodeError as e:
                    st.error(f"Erro ao decodificar JSON da IA. O formato de saída pode estar incorreto: {e}")
                    st.code(resposta_json_str)
                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar a solicitação: {e}")

        st.markdown("---")

    if st.session_state["contexto_pdf"]:  # Habilitação edital prompt
        if st.button("📊 Analisar PDF e gerar planilha de Habilitação do edital"):
            with st.spinner("Analisando o edital e gerando a planilha..."):
                # --- NOVO PROMPT ALTAMENTE ESPECÍFICO PARA EXTRAÇÃO COMPLETA ---
                PROMPT_COMPLETO_HABILITACAO = f"""
                Você é um especialista em leitura técnica de editais públicos de pregão. Sua tarefa é identificar
                e extrair da **Seção ou Fase de Habilitação** informações sobre os documentos exigidos para
                habilitação, mesmo que apresentados de formas variadas.
                Para cada documento encontrado, forneça as seguintes informações:

                - **Exigência de apresentação**: Indique se o documento é "Obrigatório", "Opcional" ou "Não informado".
                - **Localização da Informação**: Informe o item, cláusula ou seção onde o documento é mencionado.
                - **Observações**: Quaisquer detalhes adicionais relevantes, como prazos de validade, requisitos
                específicos ou condições especiais.
                - **Outros Documentos Identificados**: Indique qualquer documento adicional que esteja na seção mas
                não tenha sido solicitado.

                Estruture a resposta em formato JSON com a seguinte estrutura:

                "Habilitação do Edital": {{
                    "**Contrato Social**": {{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Documento de Cédula de Identidade dos Sócios ou  Proprietário RG e CPF": {{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Prova de inscrição no Cadastro Nacional de Pessoas Jurídicas **Cartão CNPJ**": {{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "CADESP – Consulta Cadastral ICMS “Publica": {{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "CADESP – Consulta Cadastral ICMS Interna ou Adicional": {{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Certidão Negativa de Débitos do FGTS":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Certidão Negativa de Débitos da **Dívida Ativa Estadual** CND Estadual":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Certidão Negativa de Falência/Recuperação Judicial/Extrajudicial":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Certidão Negativa de Débitos Trabalhistas CNDT":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Certidão Conjunta de Débitos Relativos a Tributos Federais e à Dívida Ativa da União CND Federal":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Certidão Negativa de Débitos Imobiliários":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Alvará de Funcionamento":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Certidão de Débitos Tributários não inscritos na Dívida Ativa do Estado de SP":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Termo de Abertura e Encerramento do Livro Diário":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Balanço Patrimonial do último exercício social":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "DRE – Demonstrativo de Resultado do Exercício":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Comprovação da Situação Financeira":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Certidão Negativa de Débitos junto ao Tribunal de Contas TCE/TCU":{{
                        "Exigência": "É obrigatório, opcional ou não informado",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }}
                }}

                **Instruções Cruciais:**
                1.  **Analise o arquivo carregado com foco na secção ou trecho de Habilitação com extrema atenção**
                    para não perder nenhum detalhe.
                2.  **Preencha TODOS os campos** no objeto "Habilitação do Edital". Se a informação não for encontrada,
                    indique explicitamente "Não informado" ou deixe em branco, mas não omita o campo.
                3.  Para as listas de documentos (Habilitação do Edital) , inclua **TODOS os itens
                    encontrados no edital**, mesmo que pareçam óbvios ou genéricos.
                4.  Para cada documento, detalhe se é "Obrigatório", a "Localização da Informação do documento"
                    (Item/Cláusula) e quaisquer "Observações" pertinentes (prazos de emissão, requisitos de
                    autenticação, etc.).
                5.  **A saída DEVE ser um JSON válido e completo**, com todas as chaves solicitadas, mesmo que as listas
                    estejam vazias se nenhuma informação for encontrada.

                **Conteúdo do Edital:**
                \"\"\"
                {st.session_state["contexto_pdf"][:40000]}
                \"\"\"
                """

                # --- FIM DO NOVO PROMPT ---

                try:
                    resposta = client.chat.completions.create(
                        model="gpt-4o",  # Usar o modelo mais capaz para extração detalhada
                        response_format={"type": "json_object"},  # Garantir que a saída seja JSON
                        messages=[{"role": "user", "content": PROMPT_COMPLETO_HABILITACAO}]
                    )
                    resposta_json_str = resposta.choices[0].message.content.strip()
                    dados_completos = json.loads(resposta_json_str)

                    if dados_completos:
                        arquivo_excel = gerar_excel_habilitacao(dados_completos)
                        if arquivo_excel:
                            st.success("📥 Planilha completa do edital gerada com sucesso!")
                            st.download_button(
                                label="⬇️ Baixar planilha Habilitação do edital",
                                data=arquivo_excel,
                                file_name=st.session_state["pdf_carregado_nome"].replace(".pdf", "_habilitação.xlsx"),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            st.warning("Nenhuma informação foi gerada ou houve um erro na criação do Excel.")
                    else:
                        st.warning("A IA não retornou um JSON de análise completo. Verifique o prompt ou o edital.")
                        st.code(resposta_json_str)
                except json.JSONDecodeError as e:
                    st.error(f"Erro ao decodificar JSON da IA. O formato de saída pode estar incorreto: {e}")
                    st.code(resposta_json_str)
                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar a solicitação: {e}")

        st.markdown("---")

    if st.session_state["contexto_pdf"]:  # Documentos extras prompt
        if st.button("📊 Analisar PDF e gerar planilha de Documentos Extras"):
            with st.spinner("Analisando o edital e gerando a planilha..."):
                # --- NOVO PROMPT ALTAMENTE ESPECÍFICO PARA EXTRAÇÃO COMPLETA ---
                PROMPT_COMPLETO_EXTRA = f"""
                Você é um especialista em análise de editais de pregão. Sua tarefa é ler o edital a seguir e identificar
                **todos os documentos de habilitação solicitados que não constam na lista abaixo**. O objetivo é
                garantir que nenhum requisito seja perdido.

                **Lista de Documentos Conhecidos (Não Inclusos na Análise):**
                - Contrato Social
                - Documento de identificação do sócio (RG ou CNH)
                - Certidão Simplificada JUCESP
                - Documentação de Optante do Simples Nacional
                - Procuração do Representante Legal
                - Cartão CNPJ
                - CADESP – Consulta Cadastral ICMS (Consulta Pública)
                - CADESP – Consulta Cadastral ICMS (Consulta Interna ou Adicional)
                - Certidão Negativa de Débitos do FGTS
                - Certidão Negativa de Débitos da Dívida Ativa Estadual CND Estadual
                - Certidão de Falência, Recuperação Judicial ou Extrajudicial
                - Certidão Negativa de Débitos Trabalhistas (CNDT)
                - Certidão Conjunta de Débitos Relativos a Tributos Federais e à Dívida Ativa da União (CND Federal)
                - Certidão Negativa de Débitos Imobiliários
                - Certidão Negativa de Débitos Mobiliários
                - Alvará de Funcionamento
                - Certidão de Débitos Tributários não inscritos na Dívida Ativa do Estado de SP
                - Termo de Abertura e Encerramento do Livro Diário
                - Balanço Patrimonial do último exercício social
                - DRE – Demonstrativo de Resultado do Exercício
                - Comprovação da Situação Financeira
                - Certidão Negativa de Débitos junto ao Tribunal de Contas (TCE/TCU)
                Retorne a resposta EXCLUSIVAMENTE no seguinte formato JSON:

                "Documentos extras": {{
                    "Doc 1": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 2": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 3": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 4": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 5": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 6": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 7": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 8": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 9": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 10": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 11": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 12": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 13": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},
                    "Doc 14": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }},,
                    "Doc 15": {{
                        "Nome": "Nome, modelo ou tipo do documento",
                        "Localização da Informação": "Item/Cláusula/Título no edital",
                        "Observação": "Observações relevantes"
                    }}
                }}
                **Instruções para a Resposta:**
                1.  Leia o edital completo com atenção para garantir que nenhum documento seja omitido.
                2.  Para cada documento encontrado que não está na lista acima, extraia as seguintes informações:
                    -  **Nome do Documento**: O nome exato ou uma descrição clara do documento (ex: "Declaração
                    de Visita Técnica").
                    -   **Localização no Edital**: A seção, cláusula ou item onde o documento é mencionado
                    (ex: "Item 7.2.3").
                    -  **Observações Relevantes**: Qualquer detalhe importante, como prazos, formatos, requisitos
                    específicos ou condições de apresentação (ex: "válido por 60 dias" ou "modelo disponível
                    no Anexo III").
                3.  **A saída DEVE ser um JSON válido e completo**, onde cada objeto representa um documento extra. Se
                nenhum documento adicional for encontrado, retorne um objeto vazio.

                **Conteúdo do Edital:**
                \"\"\"
                {st.session_state["contexto_pdf"][:30000]}
                \"\"\"
                """

                # --- FIM DO NOVO PROMPT ---

                try:
                    resposta = client.chat.completions.create(
                        model="gpt-4o",  # Usar o modelo mais capaz para extração detalhada
                        response_format={"type": "json_object"},  # Garantir que a saída seja JSON
                        messages=[{"role": "user", "content": PROMPT_COMPLETO_EXTRA}]
                    )
                    resposta_json_str = resposta.choices[0].message.content.strip()
                    # --- TESTE: visualizar a saída JSON no terminal ---
                    # print("\n===== JSON RETORNADO PELA IA (RAW) =====")
                    # print(resposta_json_str)
                    # print("========================================\n")
                    dados_completos = json.loads(resposta_json_str)
                    # print("\n===== JSON CARREGADO (DICT PYTHON) =====")
                    # print(json.dumps(dados_completos, indent=4, ensure_ascii=False))
                    # print("========================================\n")

                    if dados_completos:
                        arquivo_excel = gerar_excel_extras(dados_completos)
                        if arquivo_excel:
                            st.success("📥 Planilha completa do edital gerada com sucesso!")
                            st.download_button(
                                label="⬇️ Baixar planilha Documentos Extras",
                                data=arquivo_excel,
                                file_name=st.session_state["pdf_carregado_nome"].replace(".pdf", "_extras.xlsx"),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            st.warning("Nenhuma informação foi gerada ou houve um erro na criação do Excel.")
                    else:
                        st.warning("A IA não retornou um JSON de análise completo. Verifique o prompt ou o edital.")
                        st.code(resposta_json_str)
                except json.JSONDecodeError as e:
                    st.error(f"Erro ao decodificar JSON da IA. O formato de saída pode estar incorreto: {e}")
                    st.code(resposta_json_str)
                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar a solicitação: {e}")

        st.markdown("---")

    st.subheader("💬 Chat com IA sobre o edital")

    # SECTION_CHAT --------------------------------------------------------------------------
    for historico_mensagem in st.session_state["lista_mensagens"]:
        with st.chat_message(historico_mensagem["role"]):
            st.write(historico_mensagem["content"])

    mensagem_usuario = st.chat_input("Escreva sua dúvida sobre o edital")

    if mensagem_usuario:
        st.session_state["lista_mensagens"].append({"role": "user", "content": mensagem_usuario})
        with st.chat_message("user"):
            st.write(mensagem_usuario)

        mensagens_para_ia = [
            {
                "role": "system",
                "content": (
                    "Você é um assistente especializado em análise de editais públicos."
                    "Sua função é responder a perguntas sobre o edital fornecido, "
                    "extraindo informações relevantes do texto. Mantenha as respostas"
                    "concisas e diretas."
                )
            }
        ]

        if st.session_state["contexto_pdf"]:
            mensagens_para_ia.append({
                "role": "system",
                "content": f"Conteúdo do edital para consulta:\n{st.session_state['contexto_pdf'][:40000]}"
            })
        mensagens_para_ia.extend(st.session_state["lista_mensagens"])

        with st.spinner("Pensando na resposta..."):
            try:
                resposta_modelo = client.chat.completions.create(
                    model="gpt-4o",
                    messages=mensagens_para_ia
                )
                resposta_ia = resposta_modelo.choices[0].message.content.strip()

                st.session_state["lista_mensagens"].append({"role": "assistant", "content": resposta_ia})
                with st.chat_message("assistant"):
                    st.write(resposta_ia)
            except Exception as e:
                st.error(f"Erro ao se comunicar com a IA: {e}")
                st.session_state["lista_mensagens"].append({
                    "role": "assistant",
                    "content": "Desculpe, não consegui processar sua solicitação no momento."
                    })

                with st.chat_message("assistant"):
                    st.write("Desculpe, não consegui processar sua solicitação no momento.")
