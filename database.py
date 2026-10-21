
import sqlite3
from pathlib import Path
from contextlib import closing

# Localiza o banco na mesma pasta deste arquivo
DB_PATH = Path(__file__).with_name("ingressos.db")

SITUACOES_VALIDAS = {"dentro", "fora"}


def conectar():
    return sqlite3.connect(DB_PATH)


def listar_ingressos():
    with closing(conectar()) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT codigo, idade_entrada, situacao
            FROM ingressos
            ORDER BY codigo
        """)
        return cursor.fetchall()


def buscar_ingresso(codigo):
    with closing(conectar()) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT codigo, idade_entrada, situacao
            FROM ingressos
            WHERE codigo = ?
        """, (codigo,))
        return cursor.fetchone()


def incluir_ingresso(codigo, idade, situacao):
    if not codigo.strip():
        raise ValueError("O código não pode ficar vazio.")

    if idade < 0:
        raise ValueError("A idade não pode ser negativa.")

    if situacao not in SITUACOES_VALIDAS:
        raise ValueError("Situação deve ser 'dentro' ou 'fora'.")

    with closing(conectar()) as conexao:
        with conexao:
            conexao.execute("""
                INSERT INTO ingressos
                (codigo, idade_entrada, situacao)
                VALUES (?, ?, ?)
            """, (codigo, idade, situacao))


def alterar_ingresso(codigo, idade=None, situacao=None):
    ingresso = buscar_ingresso(codigo)

    if ingresso is None:
        raise ValueError("Ingresso não encontrado.")

    idade_atual = ingresso[1]
    situacao_atual = ingresso[2]

    nova_idade = idade if idade is not None else idade_atual
    nova_situacao = (
        situacao if situacao is not None else situacao_atual
    )

    if nova_idade < 0:
        raise ValueError("A idade não pode ser negativa.")

    if nova_situacao not in SITUACOES_VALIDAS:
        raise ValueError("Situação deve ser 'dentro' ou 'fora'.")

    with closing(conectar()) as conexao:
        with conexao:
            conexao.execute("""
                UPDATE ingressos
                SET idade_entrada = ?, situacao = ?
                WHERE codigo = ?
            """, (nova_idade, nova_situacao, codigo))


def excluir_ingresso(codigo):
    with closing(conectar()) as conexao:
        with conexao:
            cursor = conexao.execute("""
                DELETE FROM ingressos
                WHERE codigo = ?
            """, (codigo,))

            if cursor.rowcount == 0:
                raise ValueError("Ingresso não encontrado.")


def resumir_situacoes():
    with closing(conectar()) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT situacao, COUNT(*)
            FROM ingressos
            GROUP BY situacao
        """)
        return dict(cursor.fetchall())
