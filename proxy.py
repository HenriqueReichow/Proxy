from flask import Flask, request 
import requests, json, re, datetime

app = Flask(__name__) #instancia server

@app.route('/<path:url>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(url):
    
    target = request.url
    print(target)
    if blocked(url):
        register_log(url, "bloqueado") 
        return get_blocked_page(url), 403
    
    if request.host != '127.0.0.1:5000' and request.host != 'localhost:5000':
        # Caso cURL: Junta o host extraído com o caminho
        target = f"http://{request.host}/{url}"
    else:
        # Caso Navegador: Usa a sua lógica original que estava certinha
        if not url.startswith("http://") and not url.startswith("https://"):
            target = "http://" + url
        else:
            target = url

    method, headers, body = separate(request)
    print(f"DEBUG: Método: {method}, Target: {target}")

    resp = send_req(method,target,headers,body)
    print(f"DEBUG CABEÇALHO: {resp.headers.get('Content-Type')}")
    conteudo = process_resp(resp) 

    if conteudo != resp.text:
        register_log(url, "filtrado")
    else:
        register_log(url, "permitido")
    
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
        if k.lower() != 'host' and k.lower() != 'content-length':
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
    # print('dom ',dom )
    with open('blocked.json', 'r') as bloq:
        dados = json.load(bloq)
        
        for site in dados['bloqueados']:
            if dom in site:
                return True
        return False

def get_blocked_page(url):
    with open('static/blocked.html', 'r') as f:
        html = f.read()
    return html.replace("{{url}}", url)

if __name__ == '__main__':
    app.run(port = 5000)