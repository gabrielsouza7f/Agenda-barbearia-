from flask import Flask
from agendamento_controller import AgendamentoController

app = Flask(__name__)
app.add_url_rule(
    '/agendamentos',
    'criar_agendamento',
    AgendamentoController.criar_agendamento,
    methods=['POST'],
)
app.add_url_rule(
    '/agendamentos',
    'listar_agendamentos',
    AgendamentoController.listar_agendamentos,
    methods=['GET'],
)
app.add_url_rule(
    '/agendamentos/<int:id>',
    'deletar_agendamento',
    AgendamentoController.deletar_agendamento,
    methods=['DELETE'],
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)  

    