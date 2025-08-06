"""
Módulo de armazenamento de credenciais de usuários.

Este arquivo armazena os hashes de senha dos usuários autorizados para acesso
à aplicação. O formato é um dicionário Python onde a chave é o nome de
usuário e o valor é o hash criptográfico de sua senha, gerado com bcrypt.

Variáveis:
---------
- `USERS_HASHES` (dict):
    Um dicionário que mapeia nomes de usuário para seus respectivos hashes de
    senha. Esta estrutura é utilizada pela lógica de autenticação do aplicativo
    para verificar as credenciais dos usuários.

    Exemplo de estrutura:
    {
        "nome_de_usuario": "hash_da_senha_com_bcrypt",
        ...
    }

IMPORTANTE:
----------
Este método de armazenamento em um arquivo Python é adequado para ambientes
de desenvolvimento e projetos menores. Em um ambiente de produção, é
fortemente recomendado o uso de um banco de dados seguro, como PostgreSQL
ou MongoDB, para armazenar as credenciais. Isso oferece maior segurança,
escalabilidade e mecanismos de gerenciamento de dados mais robustos.

"""
USERS_HASHES = {
    'VitoriaLicitacao': '$2b$12$ZJ89Iok7ubup1F3ug6J7u.P2SKtyWITY3Nb5ifQuXhRQDDA1RliNm',
    'Usuario2@licitacao': '$2b$12$mhaO76FrQXDNH.MTbIGG1uba4WCC9SmCJtQX.AesBBfCPJwAc.Jvm',
    'Rafael Fortunato': '$2b$12$rBXhTU1ZMcmq/n77uwJPuenzxLOyVH.iXK8eZSb7eGgvo4TqYOK8m',
}
