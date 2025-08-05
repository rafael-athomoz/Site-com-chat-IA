"""
Módulo de utilitários para gerenciamento de usuários e segurança da aplicação.

Este módulo contém as lógicas para gerar hashes de senhas e para a interface
de gerenciamento de usuários. As funcionalidades incluem a criação e a deleção
de contas, com acesso restrito e autenticado ao perfil de administrador.

Funções:
---------
- `generate_hashed_password(password)`: 
    Gera um hash criptográfico seguro a partir de uma senha de texto plano,
    utilizando a biblioteca bcrypt para garantir a segurança no armazenamento.

- `add_user_page()`:
    Cria e renderiza a página de gerenciamento de usuários dentro da interface
    do Streamlit. Esta página permite ao usuário com perfil de "admin"
    adicionar novos usuários com senhas seguras e remover usuários existentes,
    requerendo a autenticação da senha do administrador para cada ação de deleção.

Dependências:
--------------
- `streamlit`: Essencial para a construção da interface de usuário (UI) e
    exibição de formulários, botões e mensagens de feedback (sucesso, erro).
- `bcrypt`: Biblioteca de criptografia de senhas utilizada para gerar e
    verificar os hashes de forma segura e robusta.

- `credentials`: Módulo local que armazena o dicionário de usuários e seus
    respectivos hashes de senha. É crucial para a autenticação e o gerenciamento.

Uso:
-----
As funções deste módulo são integradas ao aplicativo principal Streamlit
(`app.py`) para fornecer um painel de controle administrativo. A função
`add_user_page` deve ser chamada apenas após a verificação de que o usuário
logado possui o perfil de "admin", garantindo o controle de acesso.

Exemplo de uso em `app.py`:
---------------------------
```python
# Importa a função do módulo admin_utils
from admin_utils import add_user_page

# ... lógica de login ...

if st.session_state["username"] == "admin":
    if st.button("Gerenciar Usuários"):
        add_user_page()
"""
import streamlit as st
import bcrypt


# Importa o dicionário de hashes
from credentials import USERS_HASHES


def generate_hashed_password(password):
    """
    Gera um hash seguro para a senha fornecida.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def add_user_page():
    """
    Função que renderiza a tela de adição de novos usuários.
    """
    st.title("👨‍💻 Gerenciar Usuários")
    st.subheader("Adicionar Novo Usuário")

    with st.form("new_user_form"):
        new_username = st.text_input("Novo Usuário", key="new_user")
        new_password = st.text_input("Nova Senha", type="password", key="new_pass")
        submit_button = st.form_submit_button("Criar Usuário")

        if submit_button:
            if not new_username or not new_password:
                st.error("Por favor, preencha todos os campos.")
            elif new_username in USERS_HASHES:
                st.error(f"O usuário '{new_username}' já existe.")
            else:
                # Gera o hash da nova senha
                hashed_password = generate_hashed_password(new_password)

                # Prepara o novo par de usuário/hash
                new_user_entry = f"    '{new_username}': '{hashed_password}',\n"

                # Adiciona o novo usuário ao arquivo de credenciais
                try:
                    with open("credentials.py", "r+") as f:
                        lines = f.readlines()
                        f.seek(0)
                        for line in lines:
                            if line.strip().startswith("USERS_HASHES = {"):
                                f.write(line)
                                f.write(new_user_entry)

                            else:
                                f.write(line)

                    st.success(f"Usuário '{new_username}' criado com sucesso!")
                    # Recarrega o app para que as novas credenciais sejam carregadas
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro ao adicionar usuário: {e}")

    # (Opcional) Exibir a lista de usuários existentes
    st.markdown("---")

    st.subheader("Deletar Usuário")

    # Garante não deletar o admin
    users_to_delete = [user for user in USERS_HASHES.keys() if user != "Rafael Fortunato"]

    if not users_to_delete:
        st.info("Não há Usuários para deletar além do administrador")
        return

    with st.form("delete_user_form"):
        users_to_delete = st.selectbox(
            "Selecione o Usuário para deletar",
            options=users_to_delete
        )
        admin_password = st.text_input("Senha Administrador", type="password", key="admin_pass_delete")
        delete_button = st.form_submit_button("Deletar Usuário")

        if delete_button:
            admin_username = "Rafael Fortunato"
            if admin_username in USERS_HASHES:
                hashed_admin_password = USERS_HASHES[admin_username].encode('utf-8')
                password_is_correct = bcrypt.checkpw(admin_password.encode('utf-8'), hashed_admin_password)

                if not password_is_correct:
                    st.error("Senha do Administrador incorreta")
            else:
                st.error("Usuário administrador não encontrado nas credenciais")
                return
            if users_to_delete in USERS_HASHES:
                try:
                    with open("credentials.py", "r") as f:
                        lines = f.readlines()

                    # Remove Linha do usuário a ser deletado
                    new_lines = [line for line in lines if users_to_delete not in line]

                    # Salva as alterações no arquivo
                    with open("credentials.py", "w") as f:
                        f.writelines(new_lines)

                    st.success(f"Usuário '{users_to_delete}' deletado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao deletar o usuário: {e}")
        else:
            st.error("Usuário não encontrado")

    st.subheader("Usuários Existentes")
    if USERS_HASHES:
        for user in USERS_HASHES.keys():
            st.write(f"- {user}")
    else:
        st.write("Nenhum usuário cadastrado.")
