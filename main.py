import os
import json

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# extrair_texto_pdf
from utils.pdf_utils import extrair_texto_pdf
# gerar_excel_resumo, gerar_excel_habilitacao, gerar_excel_credenciamento
from utils.excel_utils import gerar_excel_resumo
from utils.excel_utils import gerar_excel_habilitacao
from utils.excel_utils import gerar_excel_credenciamento
from utils.excel_utils import gerar_excel_extras


# Carrega variáveis de ambiente
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print("Chave da API da OpenAI carregada com sucesso.", api_key)  # Para depuração, remova em produção

if not api_key:
    st.error("""Erro: A chave da API da OpenAI não foi encontrada.
                Certifique-se de que OPENAI_API_KEY está definida no seu arquivo .env.""")
    st.stop()

client = OpenAI(api_key=api_key)

st.image("assets/holy dragon logo.png", width=600)
st.title("📑 Leitor de Edital 1.0")

# SECTION UPLOAD PDF -----------------------------------------------------------------------------------------------
arquivo_pdf = st.file_uploader("📤 Envie um PDF de edital para análise", type="pdf")

if "lista_mensagens" not in st.session_state:
    st.session_state["lista_mensagens"] = []
if "contexto_pdf" not in st.session_state:
    st.session_state["contexto_pdf"] = ""
if "pdf_carregado_nome" not in st.session_state:
    st.session_state["pdf_carregado_nome"] = None

# SECTION PDF PROCESSING --------------------------------------------------------------------------------------------
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

# SECTION PROMPTS ------------------------------------------------------------------------------------------
if st.session_state["contexto_pdf"]:  # resumo edital prompt
    if st.button("📊 Analisar PDF e gerar planilha com Resumo do edital"):
        with st.spinner("Analisando o edital e gerando a planilha..."):
            # --- NOVO PROMPT ALTAMENTE ESPECÍFICO PARA EXTRAÇÃO COMPLETA ---
            prompt_completo_resumo = f"""
            Você é um especialista em leitura técnica e detalhada de editais públicos de pregão.
            Sua tarefa é extrair **todas as informações essenciais e documentos exigidos** do edital fornecido,
            organizando-as em um **objeto JSON complexo** com as seguintes chaves e estruturas exatas:

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
                "Exige catálogo e qual o período de apresentação": {{
                    "Descrição": "Exigência de catálogo e o período de apresentação, se houver.",
                    "Localização da Informação": "Item/Cláusula/Título no edital"
                }},
                "Exigência de atestado do Objeto ou quantitativo e sua porcentagem": {{
                    "Descrição": "Exigência de atestado de capacidade técnica e porcentagem mínima.",
                    "Localização da Informação": "Item/Cláusula/Título no edital"
                }}
            }},
            **Instruções Cruciais:**
            1.  **Analise todo o edital com extrema atenção** para não perder nenhum detalhe.
            2.  **Preencha TODOS os campos** no objeto "Resumo do Edital". Se a informação não for encontrada, indique
                explicitamente "Não informado" ou deixe em branco, mas não omita o campo.
            4.  Para cada documento, detalhe se é "Obrigatório", a "Localização da Informação" (Item/Cláusula) e
                quaisquer "Observações" pertinentes (prazos de emissão, requisitos de autenticação, etc.).
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
                    messages=[{"role": "user", "content": prompt_completo_resumo}]
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
            prompt_completo_credenciamento = f"""
            Você é um especialista em leitura técnica de editais públicos de pregão. Sua tarefa é identificar e extrair
            informações sobre os documentos exigidos para credenciamento, mesmo que apresentados de formas variadas.
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
            2.  **Preencha TODOS os campos** no objeto "Credenciamento do Edital". Se a informação não for encontrada,
                indique explicitamente "Não informado" ou deixe em branco, mas não omita o campo.
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
                    messages=[{"role": "user", "content": prompt_completo_credenciamento}]
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
                            file_name=st.session_state["pdf_carregado_nome"].replace(".pdf", "_credenciamento.xlsx"),
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
            prompt_completo_habilitacao = f"""
            Você é um especialista em leitura técnica de editais públicos de pregão. Sua tarefa é identificar e extrair
            da **Seção ou Fase de Habilitação** informações sobre os documentos exigidos para habilitação, mesmo que
            apresentados de formas variadas.
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
                    messages=[{"role": "user", "content": prompt_completo_habilitacao}]
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
            prompt_completo_extra = f"""
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
                }}
            }}
            **Instruções para a Resposta:**
            1.  Leia o edital completo com atenção para garantir que nenhum documento seja omitido.
            2.  Para cada documento encontrado que não está na lista acima, extraia as seguintes informações:
                -   **Nome do Documento**: O nome exato ou uma descrição clara do documento (ex: "Declaração
                de Visita Técnica").
                -   **Localização no Edital**: A seção, cláusula ou item onde o documento é mencionado
                (ex: "Item 7.2.3").
                -   **Observações Relevantes**: Qualquer detalhe importante, como prazos, formatos, requisitos
                específicos ou condições de apresentação (ex: "válido por 60 dias" ou "modelo disponível no Anexo III").
            3.  Formate a resposta como um array de objetos JSON, onde cada objeto representa um documento extra. Se
            nenhum documento adicional for encontrado, retorne um array vazio.

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
                    messages=[{"role": "user", "content": prompt_completo_extra}]
                )
                resposta_json_str = resposta.choices[0].message.content.strip()
                # --- TESTE: visualizar a saída JSON no terminal ---
                print("\n===== JSON RETORNADO PELA IA (RAW) =====")
                print(resposta_json_str)
                print("========================================\n")
                dados_completos = json.loads(resposta_json_str)
                print("\n===== JSON CARREGADO (DICT PYTHON) =====")
                print(json.dumps(dados_completos, indent=4, ensure_ascii=False))
                print("========================================\n")

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

# SECTION_CHAT ----------------------------------------------------------------------------------------------
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
