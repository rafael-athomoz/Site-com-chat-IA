from io import BytesIO

import pandas as pd
import streamlit as st


def gerar_excel_resumo(dados_para_excel):  # Resumo do edital
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


def gerar_excel_credenciamento(dados_para_excel):   # Credenciamento do edital
    """Gera um arquivo Excel de Credenciamento do Edital."""
    if not dados_para_excel:
        return None
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Processa documentos de Credenciamento ----------------------------------------------

            credenciamento = dados_para_excel.get("Credenciamento do Edital", {})
            credenciamento_convertido = []

            # Percorre todos os campos do resumo e estrutura no novo formato
            for chave, valor in credenciamento.items():
                if isinstance(valor, dict):
                    cred_exigencia = valor.get("Exigência", "Não informado")
                    cred_localizacao = valor.get("Localização da Informação", "Não informado")
                    cred_observacoes = valor.get("Observação", "Não informado")
                else:
                    cred_exigencia = valor
                    cred_localizacao = "Não informado"
                    cred_observacoes = "Não informado"
                credenciamento_convertido.append({
                    "Documento": chave,
                    "Exigência": cred_exigencia,
                    "Localização da Informação": cred_localizacao,
                    "Observação": cred_observacoes
                })

            df_credenciamento = pd.DataFrame(credenciamento_convertido)
            df_credenciamento.to_excel(writer, sheet_name="Credenciamento do Edital", index=False)

        output.seek(0)
        return output

    except Exception as e:
        st.error(f"Erro ao gerar o arquivo Excel: {e}")
        return None


def gerar_excel_habilitacao(dados_para_excel):   # Habilitação do edital
    """Gera um arquivo Excel de Habilitação do Edital."""
    if not dados_para_excel:
        return None
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Processa documentos de habilitação --------------------------------------------

            habilitacao = dados_para_excel.get("Habilitação do Edital", {})
            habilitacao_convertido = []

            # Percorre todos os campos do resumo e estrutura no novo formato
            for chave, valor in habilitacao.items():
                if isinstance(valor, dict):
                    exigencia = valor.get("Exigência", "não informado")
                    localizacao = valor.get("Localização da Informação", "não informado"),
                    observacao = valor.get("Observação", "não informado")
                else:
                    exigencia = valor
                    localizacao = "Não informado"
                    observacao = "Não informado"
                habilitacao_convertido.append({
                    "Documento": chave,
                    "Exigência": exigencia,
                    "Localização da Informação": localizacao,
                    "Observação": observacao
                })

            df_habilitacao = pd.DataFrame(habilitacao_convertido)
            df_habilitacao.to_excel(writer, sheet_name="Habilitação do Edital", index=False)

        output.seek(0)
        return output

    except Exception as e:
        st.error(f"Erro ao gerar o arquivo Excel: {e}")
        return None
