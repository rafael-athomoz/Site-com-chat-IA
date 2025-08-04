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
    st.subheader("Usuários Existentes")
    if USERS_HASHES:
        for user in USERS_HASHES.keys():
            st.write(f"- {user}")
    else:
        st.write("Nenhum usuário cadastrado.")
