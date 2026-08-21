from flask import Flask
from agendamento_routes import agendamento_bp

app = Flask(__name__)
app.register_blueprint(agendamento_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)  

    