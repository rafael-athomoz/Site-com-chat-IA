import os
import json
from io import BytesIO

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import fitz  # PyMuPDF
from openai import OpenAI

# Carrega variáveis de ambiente
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print("Chave da API da OpenAI carregada com sucesso.", api_key)  # Para depuração, remova em produção

if not api_key:
    st.error("""
            Erro: A chave da API da OpenAI não foi encontrada. Certifique-se de que
            OPENAI_API_KEY está definida no seu arquivo .env.""")
    st.stop()

client = OpenAI(api_key=api_key)


@st.cache_data
def extrair_texto_pdf(uploaded_file):
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


def gerar_excel_resumo(dados_para_excel):

    """Gera um arquivo Excel Resumo do edital."""
    if not dados_para_excel:
        return None
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Processa resumo do edital ------------------------------------------------------------
            resumo = dados_para_excel.get("Resumo do Edital", {})
            resumo_convertido = []

            # Percorre todos os campos do resumo e estrutura no novo formato
            for chave, valor in resumo.items():
                if isinstance(valor, dict):
                    descricao = valor.get("Descrição", "Não informado")
                    localizacao = valor.get("Localização da Informação", "Não informado")
                else:
                    descricao = valor
                    localizacao = "Não informado"
                resumo_convertido.append({
                    "Solicitação": chave,
                    "Descrição": descricao,
                    "Localização da Solicitação": localizacao
                })
            df_resumo = pd.DataFrame(resumo_convertido)
            df_resumo.to_excel(writer, sheet_name="Resumo do Edital", index=False)

        output.seek(0)
        return output

    except Exception as e:
        st.error(f"Erro ao gerar o arquivo Excel: {e}")
        return None


def gerar_excel_habilitacao(dados_para_excel):
    """Gera um arquivo Excel de Habilitação do Edital."""
    if not dados_para_excel:
        return None
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Processa documentos de habilitação ------------------------------------------------------------

            habilitacao = dados_para_excel.get("Habilitação do Edital", {})
            habilitacao_convertido = []

            # Percorre todos os campos do resumo e estrutura no novo formato
            for chave, valor in habilitacao.items():
                if isinstance(valor, dict):
                    obrigatoriedade = valor.get("obrigatoriedade do documento", "Não informado")
                    localizacao_doc = valor.get("Localização da informação do documento", "Não informado")
                else:
                    obrigatoriedade = valor
                    localizacao_doc = "Não informado"
                habilitacao_convertido.append({
                    "Documento": chave,
                    "Obrigatoriedade": obrigatoriedade,
                    "Localização da informação do documento": localizacao_doc
                })

            df_habilitacao = pd.DataFrame(habilitacao_convertido)
            df_habilitacao.to_excel(writer, sheet_name="Habilitação do Edital", index=False)

        output.seek(0)
        return output

    except Exception as e:
        st.error(f"Erro ao gerar o arquivo Excel: {e}")
        return None


st.image("assets/holy dragon logo.png", width=600)
st.title("📑 Leitor de Edital 1.0")

arquivo_pdf = st.file_uploader("📤 Envie um PDF de edital para análise", type="pdf")

if "lista_mensagens" not in st.session_state:
    st.session_state["lista_mensagens"] = []
if "contexto_pdf" not in st.session_state:
    st.session_state["contexto_pdf"] = ""
if "pdf_carregado_nome" not in st.session_state:
    st.session_state["pdf_carregado_nome"] = None

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

if st.session_state["contexto_pdf"]:  # resumo edital
    if st.button("📊 Analisar PDF e gerar com Resumo do edital"):
        with st.spinner("Analisando o edital e gerando a planilha..."):
            # --- NOVO PROMPT ALTAMENTE ESPECÍFICO PARA EXTRAÇÃO COMPLETA ---
            PROMPT_COMPLETO_RESUMO = f"""
            Você é um especialista em leitura técnica e detalhada de editais públicos de pregão.
            Sua tarefa é extrair **todas as informações essenciais e documentos exigidos** do edital fornecido, 
            organizando-as em um **objeto JSON complexo** com as seguintes chaves e estruturas exatas:

            "Resumo do Edital": {{
                "Objeto": {{
                    "Descrição": "Descrição concisa do objeto do edital.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Modalidade do Pregão": {{
                    "Descrição": "Ex: Pregão Eletrônico, Presencial.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Modo de Disputa": {{
                    "Descrição": "Ex: Aberto, Fechado, Livre.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Tipo de Julgamento": {{
                    "Tipo de Julgamento do objeto licitado": "Ex: Menor Preço, Melhor Técnica.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Data e Horário de Abertura": {{
                    "Descrição": "Data e hora exatas da abertura do pregão.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Endereço de entrega do objeto": {{
                    "Descrição": "Endereço completo para entrega do objeto.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Critérios de Avaliação": {{
                    "Descrição": "Critérios utilizados para avaliação das propostas.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Valor estimado total": {{
                    "Descrição": "Valor total estimado do objeto licitado.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Plataforma onde ocorrerá o pregão": {{
                    "Descrição": "Plataforma eletrônica onde o pregão será realizado.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Validade dos Documentos de Habilitação ": {{
                    "Descrição": "Validade dos documentos exigidos para habilitação econômico/financeira.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Período de envio dos documentos de Habilitação": {{
                    "Descrição": "Período para envio dos documentos de habilitação.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Modelos de garantias exigidas": {{
                    "Descrição": "Modelos de garantias exigidas, modelo de garantia on-site ou por item, se houver.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Prazo de envio da Proposta readequada": {{
                    "Descrição": "Prazo para envio de propostas readequadas, se aplicável.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Exige catálogo e qual o período de apresentação": {{
                    "Descrição": "Exigência de catálogo e o período de apresentação, se houver.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }},
                "Exigência de atestado do Objeto ou quantitativo e sua porcentagem": {{
                    "Descrição": "Exigência de atestado de capacidade técnica e porcentagem mínima.",
                    "Localização da Informação": "Item/Cláusula/título no edital"
                }}
            }},
            **Instruções Cruciais:**
            1.  **Analise todo o edital com extrema atenção** para não perder nenhum detalhe.
            2.  **Preencha TODOS os campos** no objeto "Resumo do Edital". Se a informação não for encontrada,
            indique explicitamente "Não informado" ou deixe em branco, mas não omita o campo.
            3.  Para as listas de documentos (Habilitação, Credenciamento) e Garantias, inclua **TODOS os itens
            encontrados no edital**, mesmo que pareçam óbvios ou genéricos.
            4.  Para cada documento, detalhe se é "Obrigatório", a "Localização da Informação" (Item/Cláusula) e
            quaisquer "Observações" pertinentes (prazos de emissão, requisitos de autenticação, etc.).
            5.  **Não inclua URLs de coleta externa** (JUCESP, Receita Federal, etc.) na saída JSON. Sua tarefa é
            extrair *apenas* as informações do edital.
            6.  **A saída DEVE ser um JSON válido e completo**, com todas as chaves solicitadas, mesmo que as listas
            estejam vazias se nenhuma informação for encontrada.

            **Conteúdo do Edital:**
            \"\"\"
            {st.session_state["contexto_pdf"][:10000]}
            \"\"\"
            """

            # --- FIM DO NOVO PROMPT ---

            try:
                resposta = client.chat.completions.create(
                    model="gpt-4o",  # Usar o modelo mais capaz para extração detalhada
                    response_format={"type": "json_object"},  # Garantir que a saída seja JSON
                    messages=[{"role": "user", "content": PROMPT_COMPLETO_RESUMO}])

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


if st.session_state["contexto_pdf"]:  # habilitação edital
    if st.button("📊 Analisar PDF e gerar planilha de habilitação do edital"):
        with st.spinner("Analisando o edital e gerando a planilha..."):
            # --- NOVO PROMPT ALTAMENTE ESPECÍFICO PARA EXTRAÇÃO COMPLETA ---
            PROMPT_COMPLETO_HABILITACAO = f"""
            Você é um especialista em leitura técnica e detalhada de editais públicos de pregão.
            Sua tarefa é extrair **todos dos documentos exigidos para participação** do edital fornecido, 
            organizando-as em um **objeto JSON complexo** com as seguintes chaves e estruturas exatas:

            "Habilitação do Edital": {{
                "Ato constitutivo, estatuto ou contrato social em vigor, devidamente registrado na Junta Comercial": {{
                    "obrigatoriedade do documento": "É obrigatório?",
                    "Localização da informação do documento": "Item/Cláusula/Título no edital"
                }},
                "Documento de Identidade do sócio RG e CPF": {{
                    "obrigatoriedade do documento": "É obrigatório",
                    "Localização da informação do documento": "Item/Cláusula/Título no edital"
                }},
                "Exigência de certidão simplificada da JUCESP (ou da junta comercial de qualquer estado)": {{
                    "obrigatoriedade do documento": "É obrigatório",
                    "Localização da informação do documento": "Item/Cláusula/Título no edital"
                }},
                "Documento de Optante pelo Simples Nacional": {{
                    "obrigatoriedade do documento": "É obrigatório",
                    "Localização da informação do documento": "Item/Cláusula/Título no edital"
                }},
                "Procuração de Representante Legal": {{
                    "obrigatoriedade do documento": "É obrigatório",
                    "Localização da informação do documento": "Item/Cláusula/Título no edital"
                }}
            }}

            **Instruções Cruciais:**
            1.  **Analise todo o edital com extrema atenção** para não perder nenhum detalhe.
            2.  **Preencha TODOS os campos** no objeto "Resumo do Edital". Se a informação não for encontrada,
            indique explicitamente "Não informado" ou deixe em branco, mas não omita o campo.
            3.  Para as listas de documentos (Habilitação, Credenciamento) e Garantias, inclua **TODOS os itens
            encontrados no edital**, mesmo que pareçam óbvios ou genéricos.
            4.  Para cada documento, detalhe se é "Obrigatório", a "Localização da Informação" (Item/Cláusula) e
            quaisquer "Observações" pertinentes (prazos de emissão, requisitos de autenticação, etc.).
            5.  **Não inclua URLs de coleta externa** (JUCESP, Receita Federal, etc.) na saída JSON. Sua tarefa é
            extrair *apenas* as informações do edital.
            6.  **A saída DEVE ser um JSON válido e completo**, com todas as chaves solicitadas, mesmo que as listas
            estejam vazias se nenhuma informação for encontrada.

            **Conteúdo do Edital:**
            \"\"\"
            {st.session_state["contexto_pdf"][:10000]}
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
                            file_name=st.session_state["pdf_carregado_nome"].replace(".pdf", "_habilitacao.xlsx"),
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
                "Você é um assistente especializado em análise de editais públicos. "
                "Sua função é responder a perguntas sobre o edital fornecido, "
                "extraindo informações relevantes do texto. Mantenha as respostas concisas e diretas."
            )
        }
    ]

    if st.session_state["contexto_pdf"]:
        mensagens_para_ia.append({
            "role": "system",
            "content": f"Conteúdo do edital para consulta:\n{st.session_state['contexto_pdf'][:5000]}"
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
            st.session_state["lista_mensagens"].append(
                {"role": "assistant", "content": "Desculpe, não consegui processar sua solicitação no momento."})
            with st.chat_message("assistant"):
                st.write("Desculpe, não consegui processar sua solicitação no momento.")
