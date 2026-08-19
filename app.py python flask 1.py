import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='db_barbearia',
            user='root',
            password=''  # <-- COLOCA AQUI A MESMA SENHA QUE VOCÊ USA NO WORKBENCH. Se for sem senha, deixa '' mesmo
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None 
    from database import get_db_connection

class AgendamentoModel:
    @staticmethod
    def inserir(nome, telefone, servico, data_hora, consentimento_lgpd):
        conn = get_db_connection()
        if not conn: return None
        cursor = conn.cursor()
        query = "INSERT INTO agendamentos (nome, telefone, servico, data_hora, consentimento_lgpd) VALUES (%s, %s, %s, %s, %s)"
        values = (nome, telefone, servico, data_hora, consentimento_lgpd)
        cursor.execute(query, values)
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return novo_id

    @staticmethod
    def listar_todos():
        conn = get_db_connection()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM agendamentos ORDER BY id DESC")
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados

    @staticmethod
    def deletar(id_orcamento):
        conn = get_db_connection()
        if not conn: return False
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agendamentos WHERE id = %s", (id_orcamento,))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()
        return linhas > 0 
    