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

from flask import Flask, jsonify, request
import logging

# Inicialização do aplicativo Flask
app = Flask(__name__)

# Configuração básica de logs
logging.basicConfig(level=logging.INFO)

# IMPORTANTE: Certifique-se de que o arquivo 'agendamento_model.py' 
# existe na mesma pasta e contém a classe 'AgendamentoModel'.
try:
    from agendamento_model import AgendamentoModel
except ImportError:
    AgendamentoModel = None


class AgendamentoController:
    """Controlador responsável pelo gerenciamento de agendamentos e conformidade com a LGPD."""

    @staticmethod
    def criar_agendamento():
        """Cria um novo agendamento validando os campos obrigatórios e o consentimento LGPD."""
        if not AgendamentoModel:
            return jsonify({"erro": "Módulo de banco de dados não carregado."}), 500

        dados = request.get_json(silent=True)
        
        if not dados:
            return jsonify({"erro": "Requisição sem corpo JSON ou JSON inválido."}), 400
            
        campos = ['nome', 'telefone', 'servico', 'data_hora', 'consentimento_lgpd']
        for campo in campos:
            if campo not in dados or str(dados[campo]).strip() == "":
                return jsonify({"erro": f"O campo '{campo}' é obrigatório e não pode estar vazio."}), 400

        if dados['consentimento_lgpd'] is not True:
            return jsonify({"erro": "LGPD: O consentimento explícito é obrigatório."}), 400

        try:
            novo_id = AgendamentoModel.inserir(
                nome=dados['nome'],
                telefone=dados['telefone'],
                servico=dados['servico'],
                data_hora=dados['data_hora'],
                consentimento_lgpd=dados['consentimento_lgpd']
            )
            
            if novo_id:
                return jsonify({"mensagem": "Agendamento cadastrado com sucesso!", "id": novo_id}), 201
                
            return jsonify({"erro": "Erro ao salvar o registro no banco de dados."}), 500
            
        except Exception as e:
            logging.error(f"Erro interno ao criar agendamento: {str(e)}")
            return jsonify({"erro": "Erro interno no servidor."}), 500

    @staticmethod
    def listar_agendamentos():
        """Lista todos os agendamentos cadastrados."""
        if not AgendamentoModel:
            return jsonify({"erro": "Módulo de banco de dados não carregado."}), 500

        try:
            resultados = AgendamentoModel.listar_todos()
            return jsonify(resultados), 200
        except Exception as e:
            logging.error(f"Erro ao listar agendamentos: {str(e)}")
            return jsonify({"erro": "Erro interno ao buscar registros."}), 500

    @staticmethod
    def deletar_agendamento(id):
        """Remove um agendamento específico atendendo aos requisitos da LGPD (direito ao esquecimento)."""
        if not AgendamentoModel:
            return jsonify({"erro": "Módulo de banco de dados não carregado."}), 500

        try:
            if AgendamentoModel.deletar(id):
                return jsonify({"mensagem": f"Registro {id} excluído com sucesso - Requisito LGPD atendido."}), 200
                
            return jsonify({"erro": "Registro não encontrado."}), 404
            
        except Exception as e:
            logging.error(f"Erro ao deletar agendamento {id}: {str(e)}")
            return jsonify({"erro": "Erro interno ao processar a exclusão."}), 500


# Mapeamento das Rotas (Endpoints) no Flask
app.add_url_rule('/agendamentos', 'criar_agendamento', AgendamentoController.criar_agendamento, methods=['POST'])
app.add_url_rule('/agendamentos', 'listar_agendamentos', AgendamentoController.listar_agendamentos, methods=['GET'])
app.add_url_rule('/agendamentos/<int:id>', 'deletar_agendamento', AgendamentoController.deletar_agendamento, methods=['DELETE'])


