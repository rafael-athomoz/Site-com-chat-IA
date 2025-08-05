"""
Módulo para geração de arquivos Excel a partir de dados de editais públicos.

Este módulo contém funções utilitárias que transformam dados estruturados,
extraídos de editais de pregão eletrônico, em arquivos Excel para download.
O objetivo é organizar e facilitar o gerenciamento das informações
processadas pela análise do edital.

Funções:
---------
- `gerar_excel_resumo(dados_para_excel)`:
    Gera um arquivo Excel contendo um resumo detalhado do edital,
    incluindo itens como solicitações, descrições e a localização
    dessas informações dentro do documento original.

    Args:
        dados_para_excel (dict): Um dicionário com os dados resumidos do edital.

    Returns:
        io.BytesIO: Um objeto de arquivo em memória (BytesIO) do arquivo Excel gerado.

- `gerar_excel_credenciamento(dados_para_excel)`:
    Cria um arquivo Excel com a lista de documentos necessários para o
    credenciamento. A planilha detalha as exigências, a localização
    no edital, observações e quaisquer outros documentos complementares.
    
    Args:
        dados_para_excel (dict): Um dicionário com os dados de credenciamento.

    Returns:
        io.BytesIO: Um objeto de arquivo em memória (BytesIO) do arquivo Excel gerado.

Dependências:
--------------
- `pandas`: Essencial para a manipulação e a exportação eficiente de dados
    estruturados para o formato de planilha.
- `io.BytesIO`: Utilizado para criar o arquivo Excel diretamente na memória,
    sem a necessidade de salvá-lo no disco, o que é ideal para web apps.
- `streamlit`: (Contextual) A biblioteca de UI que integra as funcionalidades
    deste módulo, permitindo que os arquivos gerados sejam oferecidos para
    download ao usuário.

Uso:
-----
As funções deste módulo são tipicamente chamadas no fluxo de uma aplicação
Streamlit, após o processamento de um edital em PDF. O retorno das funções
é um objeto `io.BytesIO` que pode ser passado diretamente para o componente
`st.download_button` para permitir o download ao usuário.

Exemplo de uso em um script Streamlit:
--------------------------------------
```python
import streamlit as st
from utils.excel_utils import gerar_excel_resumo
from io import BytesIO

# Supondo que 'dados_processados' contenha os dados extraídos do edital
dados_processados = {...} # Exemplo de dados extraídos

# Gera o arquivo Excel a partir dos dados processados
excel_file = gerar_excel_resumo(dados_processados)

if excel_file:
    # Cria o botão de download na interface
    st.download_button(
        label="Baixar Planilha Resumo",
        data=excel_file,
        file_name="resumo_do_edital.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
"""
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

            # Extrair a seção de "Outros Documentos"
            outros_documentos = credenciamento.pop("Outros Documentos de Credenciamento", {})

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

            # Percorre os documentos extras identificados pela IA
            for chave, valor in outros_documentos.items():
                if isinstance(valor, dict):
                    cred_exigencia = valor.get("Exigência", "Não informado")
                    cred_localizacao = valor.get("Localização da Informação", "Não informado")
                    cred_observacoes = valor.get("Observação", "Não informado")
                else:
                    # Lidar com casos onde a IA pode não ter retornado um dicionário
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
                    localizacao = valor.get("Localização da Informação", "não informado")
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


def gerar_excel_extras(dados_para_excel):   # Habilitação do edital
    """Gera um arquivo Excel de documentos Extras do Edital."""
    if not dados_para_excel:
        return None
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Processa documentos de Extras --------------------------------------------

            extra = dados_para_excel.get("Documentos extras", {})
            extra_convertido = []

            # Percorre todos os campos do resumo e estrutura no novo formato
            for chave, valor in extra.items():
                if isinstance(valor, dict):
                    extra_nome = valor.get("Nome", "não informado")
                    extra_localizacao = valor.get("Localização da Informação", "não informado")
                    extra_observacao = valor.get("Observação", "não informado")
                else:
                    extra_nome = valor
                    extra_localizacao = "Não informado"
                    extra_observacao = "Não informado"
                extra_convertido.append({
                    "Documento": chave,
                    "Nome": extra_nome,
                    "Localização da Informação": extra_localizacao,
                    "Observação": extra_observacao
                })

            df_extra = pd.DataFrame(extra_convertido)
            df_extra.to_excel(writer, sheet_name="Documentos extras", index=False)

        output.seek(0)
        return output

    except Exception as e:
        st.error(f"Erro ao gerar o arquivo Excel: {e}")
        return None
