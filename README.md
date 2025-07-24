# 📑 Leitor de Edital 1.0

Ferramenta Streamlit + OpenAI para extrair, analisar e gerar planilhas de editais públicos em PDF.

---

## 🔍 Visão Geral

Leitor de Edital 1.0 é um aplicativo voltado para análise técnica de editais de licitação. Ele permite:

- Upload de PDFs de editais.
- Extração de texto com PyMuPDF.
- Chamada ao OpenAI (modelo GPT) para extrair dados estruturados: resumo, documentos exigidos, prazos, garantias etc.
- Geração automática de planilha Excel com múltiplas abas (Resumo do Edital e Documentos de Habilitação).
- Chat interativo para esclarecer dúvidas sobre o edital.

---

## 🛠️ Funcionalidades Principais

- **Upload e extração de texto do PDF** (utilizando `fitz`).
- **Análise pontual do edital** com prompt sob medida.
- **Geração de JSON estruturado** conforme schema definido.
- **Exportação de planilha Excel** com múltiplas abas.
- **Chat interativo** para discussões baseadas no conteúdo extraído.
- **Cache inteligente** com `st.cache_data` e `st.cache_resource`.

---

## 🧠 Tecnologias Utilizadas

- **Streamlit** – UI reativa e fácil deploy.  
- **PyMuPDF** – Extração eficiente de texto de PDFs.  
- **OpenAI GPT-4** – Interpretação e extração de dados complexos.  
- **Pandas + openpyxl** – Manipulação e geração da planilha Excel.  
- **dotenv** – Carregamento seguro de variáveis de ambiente.  
- **Pydantic (opcional)** – Validação do JSON de saída.

---

## 🚀 Instalação e Execução

1. Clone o repositório:
   ```bash
   git clone https://github.com/<seu-usuario>/leitor-edital.git
   cd leitor-edital

   ```bash
      ├── app.py              # Aplicação Streamlit
      ├── utils/
      │   ├── pdf_utils.py    # Extração de PDF
      │   ├── excel_utils.py  # Geração de planilha
      │   └── openai_utils.py # Prompt + chamadas OpenAI
      ├── assets/             # Ícones e imagens
      ├── requirements.txt    # Dependências
      ├── .env.example        # Modelo de variáveis de ambiente
      └── README.md           # Este arquivo

📄 Licença
Distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

📞 Contato
Desenvolvedor: Rafael

Email: trello.athomoz@gmail.com

LinkedIn/GitHub: [/rafael-dev](https://github.com/rafael-athomoz)

📚 Referências
Repositórios similares: Talk-with-PDF, PDF Insight Extractor

Boas práticas para apps GenAI com Streamlit.

