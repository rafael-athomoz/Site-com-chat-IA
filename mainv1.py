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
print("Chave da API da OpenAI carregada com sucesso.", api_key)  # Para depuração, remova em produção

if not api_key:
    st.error("Erro: A chave da API da OpenAI não foi encontrada. Certifique-se de que OPENAI_API_KEY está definida no seu arquivo .env.")
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


def gerar_excel_documentos(dados_completos):  
    """Gera um arquivo Excel com múltiplas abas a partir de dados completos."""
    if not dados_completos:
        return None
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Pasta de trabalho 1: Documentação (conforme o Passo 1 solicitado)
            resumo_data = dados_completos.get("Resumo do Edital", {})
            
            # Prepare data for the "Documentação" sheet in the desired row format
            documentacao_list = []
                    
            documentacao_list.append({"Tipo do Documento": "Objeto?", "Nome do documento": resumo_data.get("Objeto", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Modalidade do Pregão?", "Nome do documento": resumo_data.get("Modalidade do Pregão", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Tipo de Julgamento?", "Nome do documento": resumo_data.get("Tipo de Julgamento", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Data e Horário de Abertura?", "Nome do documento": resumo_data.get("Data e Horário de Abertura", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Plataforma do Pregão?", "Nome do documento": resumo_data.get("Plataforma do Pregão", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Valor Estimado Total?", "Nome do documento": resumo_data.get("Valor Estimado Total", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Endereço de Entrega?", "Nome do documento": resumo_data.get("Endereço de Entrega", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Critérios de Avaliação?", "Nome do documento": resumo_data.get("Critérios de Avaliação", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Validade dos Documentos Solicitados?", "Nome do documento": resumo_data.get("Validade dos Documentos Solicitados", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Período de Envio dos Documentos?", "Nome do documento": resumo_data.get("Período de Envio dos Documentos", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Prazo de Envio da Proposta Readequada?", "Nome do documento": resumo_data.get("Prazo de Envio da Proposta Readequada", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Exige Catálogo e Período de Apresentação?", "Nome do documento": resumo_data.get("Exige Catálogo e Período de Apresentação", "Não informado"), "Localização da informação": "Não informado"})
            documentacao_list.append({"Tipo do Documento": "Exigência de Atestado do Objeto ou Quantitativo e Sua Porcentagem?", "Nome do documento": resumo_data.get("Exigência de Atestado do Objeto ou Quantitativo e Sua Porcentagem", "Não informado"), "Localização da informação": "Não informado"})
            
            df_documentacao_resumo = pd.DataFrame(documentacao_list)
            df_documentacao_resumo.to_excel(writer, sheet_name="Documentação", index=False)
            
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

if st.session_state["contexto_pdf"]:
    if st.button("📊 Analisar PDF e gerar planilha completa do edital"):
        with st.spinner("Analisando o edital e gerando a planilha..."):
            # --- NOVO PROMPT ALTAMENTE ESPECÍFICO PARA EXTRAÇÃO COMPLETA ---
            prompt_completo_edital = f"""
            Você é um especialista em leitura técnica e detalhada de editais públicos de pregão.
            Sua tarefa é extrair **todas as informações essenciais e documentos exigidos** do edital fornecido, organizando-as em um **objeto JSON complexo** com as seguintes chaves e estruturas exatas:

            {{
                "Resumo do Edital": {{
                    "Objeto": "Descrição concisa do objeto do edital.",
                    "Modalidade do Pregão": "Ex: Pregão Eletrônico, Presencial.",
                    "Tipo de Julgamento": "Ex: Menor Preço, Técnica e Preço, Melhor Técnica.",
                    "Data e Horário de Abertura": "Data e hora exatas da sessão pública (DD/MM/AAAA HH:MM).",
                    "Plataforma do Pregão": "Endereço eletrônico da plataforma onde ocorrerá o pregão (URL).",
                    "Valor Estimado Total": "Valor total estimado para o edital (em moeda local, ex: R$ 1.000.000,00). Se não encontrado, deixe em branco ou 'Não informado'.",
                    "Endereço de Entrega": "Endereço completo para entrega de bens/serviços, se aplicável.",
                    "Critérios de Avaliação": "Descrição dos critérios de avaliação da proposta ou habilitação.",
                    "Validade dos Documentos Solicitados": "Período de validade exigido para os documentos, se especificado (Ex: 'Válidos por 6 meses', 'Conforme legislação').",
                    "Período de Envio dos Documentos": "Prazo ou período para envio da documentação de habilitação/proposta.",
                    "Prazo de Envio da Proposta Readequada": "Prazo para envio de propostas readequadas, se houver.",
                    "Exige Catálogo e Período de Apresentação": "Sim/Não e, se sim, qual o período para apresentação do catálogo.",
                    "Exigência de Atestado do Objeto ou Quantitativo e Sua Porcentagem": "Sim/Não e, se sim, qual a porcentagem do quantitativo ou descrição do atestado exigido."
                }},
            }}

            **Instruções Cruciais:**
            1.  **Analise todo o edital com extrema atenção** para não perder nenhum detalhe.
            2.  **Preencha TODOS os campos** no objeto "Resumo do Edital". Se a informação não for encontrada, indique explicitamente "Não informado" ou deixe em branco, mas não omita o campo.
            3.  Para as listas de documentos (Habilitação, Credenciamento) e Garantias, inclua **TODOS os itens encontrados no edital**, mesmo que pareçam óbvios ou genéricos.
            4.  Para cada documento, detalhe o "Tipo do Documento", "Nome do Documento", se é "Obrigatório" ou "Opcional", a "Localização da Informação" (Item/Cláusula) e quaisquer "Observações" pertinentes (prazos de emissão, requisitos de autenticação, etc.).
            5.  **Não inclua URLs de coleta externa** (JUCESP, Receita Federal, etc.) na saída JSON. Sua tarefa é extrair *apenas* as informações do edital. As URLs de coleta serão tratadas por outra função no código Python, se necessário.
            6.  **A saída DEVE ser um JSON válido e completo**, com todas as chaves solicitadas, mesmo que as listas (Garantias, Habilitação, Credenciamento) estejam vazias se nenhuma informação for encontrada para elas no edital.

            **Conteúdo do Edital:**
            \"\"\"
            {st.session_state["contexto_pdf"][:10000]}
            \"\"\"
            """
            # --- FIM DO NOVO PROMPT ---

            try:
                resposta = client.chat.completions.create(
                    model="gpt-4o",  # Usar o modelo mais capaz para extração detalhada
                    response_format={"type": "json_object"}, # Garantir que a saída seja JSON
                    messages=[{"role": "user", "content": prompt_completo_edital}]
                )
                
                resposta_json_str = resposta.choices[0].message.content.strip()
                dados_completos = json.loads(resposta_json_str)

                if dados_completos:
                    arquivo_excel = gerar_excel_documentos(dados_completos)
                    if arquivo_excel:
                        st.success("📥 Planilha completa do edital gerada com sucesso!")
                        st.download_button(
                            label="⬇️ Baixar planilha completa do edital",
                            data=arquivo_excel,
                            file_name="analise_edital_completa.xlsx",
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
                model="gpt-3.5-turbo",
                messages=mensagens_para_ia
            )
            resposta_ia = resposta_modelo.choices[0].message.content.strip()

            st.session_state["lista_mensagens"].append({"role": "assistant", "content": resposta_ia})
            with st.chat_message("assistant"):
                st.write(resposta_ia)
        except Exception as e:
            st.error(f"Erro ao se comunicar com a IA: {e}")
            st.session_state["lista_mensagens"].append({"role": "assistant", "content": "Desculpe, não consegui processar sua solicitação no momento."})
            with st.chat_message("assistant"):
                st.write("Desculpe, não consegui processar sua solicitação no momento.")