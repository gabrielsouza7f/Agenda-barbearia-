from flask import jsonify, request
import logging

from agendamento_model import AgendamentoModel


class AgendamentoController:
    @staticmethod
    def criar_agendamento():
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Requisição sem corpo JSON ou JSON inválido."}), 400

        campos = ["nome", "telefone", "servico", "data_hora", "consentimento_lgpd"]
        for campo in campos:
            if campo not in dados or str(dados[campo]).strip() == "":
                return jsonify({"erro": f"O campo '{campo}' é obrigatório e não pode estar vazio."}), 400

        if dados["consentimento_lgpd"] is not True:
            return jsonify({"erro": "LGPD: o consentimento explícito é obrigatório."}), 400

        try:
            novo_id = AgendamentoModel.inserir(
                nome=dados["nome"],
                telefone=dados["telefone"],
                servico=dados["servico"],
                data_hora=dados["data_hora"],
                consentimento_lgpd=dados["consentimento_lgpd"],
            )
            if novo_id is None:
                return jsonify({"erro": "Erro ao salvar o registro no banco de dados."}), 500
            return jsonify({"mensagem": "Agendamento cadastrado com sucesso!", "id": novo_id}), 201
        except Exception:
            logging.exception("Erro interno ao criar agendamento")
            return jsonify({"erro": "Erro interno no servidor."}), 500

    @staticmethod
    def listar_agendamentos():
        try:
            return jsonify(AgendamentoModel.listar_todos()), 200
        except Exception:
            logging.exception("Erro ao listar agendamentos")
            return jsonify({"erro": "Erro interno ao buscar registros."}), 500

    @staticmethod
    def deletar_agendamento(id):
        try:
            if AgendamentoModel.deletar(id):
                return jsonify({"mensagem": f"Registro {id} excluído com sucesso."}), 200
            return jsonify({"erro": "Registro não encontrado."}), 404
        except Exception:
            logging.exception("Erro ao deletar agendamento %s", id)
            return jsonify({"erro": "Erro interno ao processar a exclusão."}), 500

    