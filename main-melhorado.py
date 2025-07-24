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
            # Pasta de trabalho 1: Documentação (Resumo e Garantias)
            # Combine Resumo do Edital e Garantias para a aba "Documentação"
            # Extract Resumo do Edital data
            resumo_data = dados_completos.get("Resumo do Edital", {})
            garantias_data = dados_completos.get("Garantias Exigidas", [])

            # Prepare data for "Documentação" sheet
            documentacao_list = []

            # Add Resumo do Edital items
            documentacao_list.append({"Item": "Objeto", "Descrição": resumo_data.get("Objeto", "")})
            documentacao_list.append({"Item": "Modalidade do Pregão", "Descrição": resumo_data.get("Modalidade do Pregão", "")})
            documentacao_list.append({"Item": "Tipo de Julgamento", "Descrição": resumo_data.get("Tipo de Julgamento", "")})
            documentacao_list.append({"Item": "Data e Horário de Abertura", "Descrição": resumo_data.get("Data e Horário de Abertura", "")})
            documentacao_list.append({"Item": "Plataforma do Pregão", "Descrição": resumo_data.get("Plataforma do Pregão", "")})
            documentacao_list.append({"Item": "Valor Estimado Total", "Descrição": resumo_data.get("Valor Estimado Total", "")})
            documentacao_list.append({"Item": "Endereço de Entrega", "Descrição": resumo_data.get("Endereço de Entrega", "")})
            documentacao_list.append({"Item": "Critérios de Avaliação", "Descrição": resumo_data.get("Critérios de Avaliação", "")})
            documentacao_list.append({"Item": "Validade dos Documentos Solicitados", "Descrição": resumo_data.get("Validade dos Documentos Solicitados", "")})
            documentacao_list.append({"Item": "Período de Envio dos Documentos", "Descrição": resumo_data.get("Período de Envio dos Documentos", "")})
            documentacao_list.append({"Item": "Prazo de Envio da Proposta Readequada", "Descrição": resumo_data.get("Prazo de Envio da Proposta Readequada", "")})
            documentacao_list.append({"Item": "Exige Catálogo e Período de Apresentação", "Descrição": resumo_data.get("Exige Catálogo e Período de Apresentação", "")})
            documentacao_list.append({"Item": "Exigência de Atestado do Objeto ou Quantitativo e Sua Porcentagem", "Descrição": resumo_data.get("Exigência de Atestado do Objeto ou Quantitativo e Sua Porcentagem", "")})         
            # Add Garantias Exigidas items
            if garantias_data:
                documentacao_list.append({"Item": "--- Garantias Exigidas ---", "Descrição": ""})
                for garantia in garantias_data:
                    documentacao_list.append({
                        "Item": f"Garantia: {garantia.get('Nome da Garantia', '')}",
                        "Descrição": f"Tipo: {garantia.get('Tipo de Garantia', '')}, Valor/Porcentagem: {garantia.get('Valor ou Porcentagem', '')}, Localização: {garantia.get('Localização da Informação', '')}"
                    })
            
            df_documentacao_geral = pd.DataFrame(documentacao_list)
            df_documentacao_geral.to_excel(writer, sheet_name="Documentação", index=False)

            # Pasta de trabalho 2: Habilitação
            df_habilitacao_raw = pd.DataFrame(dados_completos.get("Documentos de Habilitacao", []))
            
            # Dicionário com documentos esperados e suas URLs de coleta
            habilitacao_data = []
            doc_habilitacao_urls = {
                "Contrato Social": "http://endereco_de_coleta_do_documento",
                "Documento do sócio, proprietário (RG ou CNH)": "http://endereco_do_drive_do_documento",
                "Certidão Simplificada JUCESP": "https://www.jucesponline.sp.gov.br/Pesquisa.aspx?IDProduto=4",
                "Documentação de Optante do Simples Nacional": "https://www8.receita.fazenda.gov.br/simplesnacional/aplicacoes.aspx?id=21",
                "Procuração do Representante Legal": "http://endereco_do_drive_do_documento"
            }

            # Populate Habilitação sheet based on expected documents
            for doc_name, url in doc_habilitacao_urls.items():
                # Check if this document was found in the raw extraction
                found_doc = df_habilitacao_raw[df_habilitacao_raw["Nome do Documento"].str.contains(doc_name, case=False, na=False)] if not df_habilitacao_raw.empty else pd.DataFrame()
                
                if not found_doc.empty:
                    # If found, use extracted info and provided URL
                    for _, row in found_doc.iterrows():
                        habilitacao_data.append({
                            "Questionamentos": row["Nome do Documento"],
                            "Exigência": row["Obrigatoriedade"],
                            "Site de coleta de Documentos": url,
                            "Localização da Informação no Edital": row["Localização da Informação"],
                            "Observações do Edital": row["Observacoes"]
                        })
                else:
                    # If not found, just use the expected document name and URL
                    habilitacao_data.append({
                        "Questionamentos": doc_name,
                        "Exigência": "Verificar no edital", # Default if not found
                        "Site de coleta de Documentos": url,
                        "Localização da Informação no Edital": "Não encontrada",
                        "Observações do Edital": "Não encontrada"
                    })

            df_habilitacao = pd.DataFrame(habilitacao_data)
            df_habilitacao.to_excel(writer, sheet_name="Habilitação", index=False)

            # Pasta de trabalho 3: Credenciamento
            df_credenciamento_raw = pd.DataFrame(dados_completos.get("Documentos de Credenciamento", []))

            # Map required fields for Credenciamento and add default URLs
            credenciamento_data = []
            doc_credenciamento_urls = {
                "Contrato Social": "(no drive)",
                "Documento pessoal do proprietário": "(no drive)",
                "Cartão CNPJ": "https://solucoes.receita.fazenda.gov.br/servicos/cnpjreva/cnpjreva_solicitacao.asp",
                "CADESP – Consulta Cadastral ICMS “Publica”": "https://www.cadesp.fazenda.sp.gov.br/(S(aapmt4ggovwmaygquq3yv35e))/Pages/Cadastro/Consultas/ConsultaPublica/ConsultaPublica.aspx",
                "CADESP – Consulta Cadastral ICMS “Interna ou Adicional”": "https://www.cadesp.fazenda.sp.gov.br/(S(0hm22abogsrkvzgbvo02xxgt))/Pages/Login.aspx",
                "Certidão Negativa de Débitos do FGTS": "https://consultacrf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf",
                "Certidão Negativa de Débitos da Dívida Ativa Estadual CND Estadual": "https://www.dividaativa.pge.sp.gov.br/sc/pages/crda/emitirCrda.jsf?param=57416",
                "Certidão de Falência/Recuperação Judicial/Extrajudicial": "https://esaj.tjsp.jus.br/sco/abrirCadastro.do",
                "Certidão Negativa de Débitos Trabalhistas CNDT": "https://cndt-certidao.tst.jus.br/inicio.faces",
                "Certidão Conjunta de Débitos Relativos a Tributos Federais e à Dívida Ativa da União CND Federal": "https://solucoes.receita.fazenda.gov.br/servicos/certidaointernet/pj/emitir",
                "Certidão Negativa de Débitos Imobiliários": "https://serv42.limeira.sp.gov.br/CertidaoOnline/ctrrequerimento/?tipo=3",
                "Certidão Negativa de Débitos Mobiliários": "https://limeira.iibrasil.com.br/pub/pub_dashboard.php#pub_certidoes_mobiliarias$$MDFiZWRhNjQzZDhhYmEwMzc2Y2QzOThkNTc1NDQyMTZNREZpWldSaE5qUXpaRGhoWW1Fd016YzJZMlF6T1Roa05UYzFORFF5TVRZM09UZz0=$$li_798_3$$3",
                "Alvará de Funcionamento": "(no drive)",
                "Certidão de Débitos Tributários não inscritos na Dívida Ativa do Estado de SP": "https://www10.fazenda.sp.gov.br/CertidaoNegativaDeb/Pages/EmissaoCertidaoNegativa.aspx",
                "Termo de Abertura e Encerramento do Livro Diário": "(no drive)",
                "Balanço Patrimonial do último exercício social": "(no drive)",
                "DRE – Demonstrativo de Resultado do Exercício": "(no drive)",
                "Comprovação da Situação Financeira": "(no drive)",
                "Certidão Negativa de Débitos junto ao Tribunal de Contas TCE/TCU": "https://contas.tcu.gov.br/ords/f?p=1660:3:107492793920456::::P3_TIPO_RELACAO:INIDONEO"
            }

            # Populate Credenciamento sheet based on expected documents
            for doc_name, url in doc_credenciamento_urls.items():
                # Check if this document was found in the raw extraction
                found_doc = df_credenciamento_raw[df_credenciamento_raw["Nome do Documento"].str.contains(doc_name, case=False, na=False)] if not df_credenciamento_raw.empty else pd.DataFrame()
                
                if not found_doc.empty:
                    # If found, use extracted info and provided URL
                    for _, row in found_doc.iterrows():
                        credenciamento_data.append({
                            "Questionamento": row["Nome do Documento"],
                            "Exigência": row["Obrigatoriedade"],
                            "Coletar": url,
                            "Localização da Informação no Edital": row["Localização da Informação"],
                            "Observações do Edital": row["Observacoes"]
                        })
                else:
                    # If not found, just use the expected document name and URL
                    credenciamento_data.append({
                        "Questionamento": doc_name,
                        "Exigência": "Verificar no edital", # Default if not found
                        "Coletar": url,
                        "Localização da Informação no Edital": "Não encontrada",
                        "Observações do Edital": "Não encontrada"
                    })

            df_credenciamento = pd.DataFrame(credenciamento_data)
            df_credenciamento.to_excel(writer, sheet_name="Credenciamento", index=False)

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
                "Garantias Exigidas": [
                    {{
                        "Tipo de Garantia": "Ex: Garantia de Proposta, Garantia de Contrato",
                        "Nome da Garantia": "Ex: Caução em dinheiro, Seguro-Garantia, Fiança Bancária",
                        "Valor ou Porcentagem": "Valor ou porcentagem exigida (Ex: 1% do valor estimado, R$ 10.000,00)",
                        "Localização da Informação": "Item/Cláusula no edital."
                    }}
                    // Adicionar mais objetos para outras garantias se houver
                ],
                "Documentos de Habilitacao": [
                    {{
                        "Tipo do Documento": "Ex: Certidão, Contrato, Comprovante, Declaração, Atestado",
                        "Nome do Documento": "Nome completo do documento (Ex: Certidão Negativa de Débitos Federais, Contrato Social, Declaração de Inexistência de Fatos Impeditivos). Para o Contrato Social, usar exatamente 'Contrato Social'. Para o documento do sócio, usar 'Documento do sócio, proprietário (RG ou CNH)'. Para JUCESP, usar 'Certidão Simplificada JUCESP'. Para Simples Nacional, usar 'Documentação de Optante do Simples Nacional'. Para Procuração, usar 'Procuração do Representante Legal'.",
                        "Obrigatoriedade": "Obrigatório / Opcional",
                        "Localização da Informação": "Item/Cláusula no edital.",
                        "Observacoes": "Quaisquer observações importantes sobre o documento (ex: 'emitida nos últimos 90 dias', 'cópia autenticada')."
                    }}
                    // Adicionar mais objetos para documentos de habilitação
                ],
                "Documentos de Credenciamento": [
                    {{
                        "Tipo do Documento": "Ex: Procuração, Documento de Identidade, Comprovante",
                        "Nome do Documento": "Nome completo do documento. Para Contrato Social, usar exatamente 'Contrato Social'. Para documento pessoal do proprietário, usar 'Documento pessoal do proprietário'. Para Cartão CNPJ, usar 'Cartão CNPJ'. Para CADESP Pública, usar 'CADESP – Consulta Cadastral ICMS “Publica”'. Para CADESP Interna, usar 'CADESP – Consulta Cadastral ICMS “Interna ou Adicional”'. Para FGTS, usar 'Certidão Negativa de Débitos do FGTS'. Para Dívida Ativa Estadual, usar 'Certidão Negativa de Débitos da Dívida Ativa Estadual CND Estadual'. Para Falência/Recuperação, usar 'Certidão de Falência/Recuperação Judicial/Extrajudicial'. Para CNDT, usar 'Certidão Negativa de Débitos Trabalhistas CNDT'. Para CND Federal, usar 'Certidão Conjunta de Débitos Relativos a Tributos Federais e à Dívida Ativa da União CND Federal'. Para Imobiliários, usar 'Certidão Negativa de Débitos Imobiliários'. Para Mobiliários, usar 'Certidão Negativa de Débitos Mobiliários'. Para Alvará, usar 'Alvará de Funcionamento'. Para Débitos Tributários Estaduais, usar 'Certidão de Débitos Tributários não inscritos na Dívida Ativa do Estado de SP'. Para Livro Diário, usar 'Termo de Abertura e Encerramento do Livro Diário'. Para Balanço, usar 'Balanço Patrimonial do último exercício social'. Para DRE, usar 'DRE – Demonstrativo de Resultado do Exercício'. Para Situação Financeira, usar 'Comprovação da Situação Financeira'. Para TCE/TCU, usar 'Certidão Negativa de Débitos junto ao Tribunal de Contas TCE/TCU'.",
                        "Obrigatoriedade": "Obrigatório / Opcional",
                        "Localização da Informação": "Item/Cláusula no edital.",
                        "Observacoes": "Quaisquer observações importantes sobre o documento."
                    }}
                    // Adicionar mais objetos para documentos de credenciamento
                ]
            }}

            **Instruções Cruciais:**
            1.  **Analise todo o edital com extrema atenção** para não perder nenhum detalhe.
            2.  **Preencha TODOS os campos** no objeto "Resumo do Edital". Se a informação não for encontrada, indique explicitamente "Não informado" ou deixe em branco, mas não omita o campo.
            3.  Para as listas de documentos (Habilitação, Credenciamento) e Garantias, inclua **TODOS os itens encontrados no edital**, mesmo que pareçam óbvios ou genéricos, seguindo os nomes exatos especificados para os documentos listados no prompt. Se o documento for mencionado no edital, extraia-o.
            4.  Para cada documento, detalhe o "Tipo do Documento", "Nome do Documento", se é "Obrigatório" ou "Opcional", a "Localização da Informação" (Item/Cláusula) e quaisquer "Observações" pertinentes (prazos de emissão, requisitos de autenticação, etc.).
            5.  **NÃO inclua URLs de coleta externa** (JUCESP, Receita Federal, etc.) na saída JSON. Sua tarefa é extrair *apenas* as informações do edital. As URLs de coleta serão tratadas por outra função no código Python, se necessário.
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
