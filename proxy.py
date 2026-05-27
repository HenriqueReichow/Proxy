from flask import Flask, request 
import requests, json, re, datetime

app = Flask(__name__) #instancia server

@app.route('/<path:url>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(url):
    acao = []

    if blocked(url):
        acao.append('bloqueado')
        return "<h1>Acesso Bloqueado</h1><p>Este site não é permitido.</p>", 403
    
    else:
        if url.startswith("http://"):
            target = url
        else:
            target = "http://" + url

    method, headers, body = separate(request)

    resp = send_req(method,target,headers,body)
    conteudo = process_resp(resp) 

    if conteudo != resp.text:
        acao.append('filtrado')
    else:
        acao.append('sem filtro')

    acao_str = ", ".join(acao)
    register_log(url, acao_str)
    return conteudo, resp.status_code, resp.headers.items()

def register_log(url, acao):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha_log = f"{timestamp} | URL: {url} | Ação: {acao}\n"
    
    with open('log.txt', 'a') as f:
        f.write(linha_log)

def filter_word(html):
    with open('words.json', 'r') as file:
        words = json.load(file)

    for termo, substituto in words.items():
        padrao = re.compile(re.escape(termo), re.IGNORECASE)
        html = padrao.sub(substituto, html)

    return html

def separate(req):
    method = req.method
    headers = {}
    for k,v in req.headers:
        if k.lower() != 'host':
            headers[k] = v
    body = req.get_data()
    return method, headers, body

def send_req(method, url, headers, body):
    return requests.request(method=method, url=url, headers=headers, data=body, allow_redirects=False)

def process_resp(resp):
    if 'text/html' in resp.headers.get('Content-Type', ''):
        return filter_word(resp.text)
    return resp.text

def blocked(url):
    url_limpa = url.replace("http://", "").replace("https://", "")
    dom = url_limpa.split('/')[0]
    print('dom ',dom )
    with open('blocked.json', 'r') as bloq:
        dados = json.load(bloq)
        
        for site in dados['bloqueados']:
            if dom in site:
                return True
        return False

if __name__ == '__main__':
    app.run(port = 5000)