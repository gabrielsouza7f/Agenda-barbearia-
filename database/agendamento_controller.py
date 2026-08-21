from flask import Blueprint, jsonify, request
from agendamento_controller import agendamento_controller

agendamento_bp = Blueprint('agendamento_bp', __name__)

@agendamento_bp.route('/orcamento', methods=['POST'])
def rota_criar():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados JSON inválidos ou ausentes"}), 400
    return AgendamentoController.criar_orcamento(dados)

@agendamento_bp.route('/orcamentos', methods=['GET'])
def rota_listar():
    return AgendamentoController.listar_orcamentos()

@agendamento_bp.route('/orcamento/<int:id>', methods=['DELETE'])
def rota_deletar(id):
    return AgendamentoController.deletar_orcamento(id)   

    