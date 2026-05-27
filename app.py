from flask import Flask, request
import requests, json
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Olá, Flask no Ubuntu!'

@app.route('/loop')
def loop():
    saida = ''
    for i in range(100):
        saida += f'Oi Pessoal!! Meu servidor Web {i}<br>\n'
    return saida

@app.route('/dados', methods=['POST'])
def dados():
    corpo = request.get_json()
    nome = corpo.get('nome', 'desconhecido')
    return f'Recebido: {nome}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

#####https://github.com/andreprisco/AulaFlask.git
#git@github.com:andreprisco/AulaFlask.git
'''
Um jeito de ver ip dentro da rede
ip addr show| grep inet
'''

'''
python -m venv .venv
source .venv/bin/activate
deactivate
'''