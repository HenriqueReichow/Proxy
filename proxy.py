from flask import Flask, request , Response
import requests, json, re, datetime
from urllib.parse import urljoin, urlparse
app = Flask(__name__) #instancia server

@app.route('/<path:url>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(url):
    
    target = request.url
    if blocked(url):
        register_log(url, "bloqueado") 
        return get_blocked_page(url), 403
    
    # Monta a URL lidando com caminhos relativos (imagens, css, js)
    if not url.startswith("http://") and not url.startswith("https://"):
        referer = request.headers.get("Referer")
        
        if referer:
            # Pega o referer (ex: http://localhost:5000/httpforever.com) e extrai o site alvo
            ref_path = urlparse(referer).path.lstrip('/')
            
            if not ref_path.startswith("http://") and not ref_path.startswith("https://"):
                base_url = "http://" + ref_path
            else:
                base_url = ref_path
                
            # Junta o domínio original com o arquivo que o navegador pediu
            target = urljoin(base_url, url)
        else:
            target = "http://" + url
    else:
        target = url

    method, headers, body = separate(request)
    print(f"DEBUG: Método: {method}, Target: {target}")

    resp = send_req(method,target,headers,body)

    conteudo, acao = process_resp(resp)
    register_log(url, acao)
    
    
    headers_limpos = []
    for nome, valor in resp.headers.items():
        if nome.lower() not in ('content-encoding', 'content-length', 'transfer-encoding', 'connection'):
            # Força UTF-8 no content-type HTML
            if nome.lower() == 'content-type' and 'text/html' in valor.lower():
                valor = 'text/html; charset=utf-8'
            headers_limpos.append((nome, valor))

    return Response(conteudo, resp.status_code, headers_limpos)

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
    content_type = resp.headers.get('Content-Type', '').lower()
    
    if 'text/html' in content_type:
        if resp.encoding is None or resp.encoding.lower() == 'iso-8859-1':
            resp.encoding = resp.apparent_encoding
        
        original = resp.text
        filtrado = filter_word(original)
        
        # compara as strings ANTES de virar bytes
        if filtrado != original:
            acao = "filtrado"
        else:
            acao = "permitido"
        
        return filtrado.encode('utf-8'), acao  # retorna os dois juntos
    
    if 'text/css' in content_type:
        base = resp.url.split('/')[2]
        def reescrever_url(match):
            caminho = match.group(1)
            if caminho.startswith('http'):
                return f"url('{caminho}')"
            return f"url('http://localhost:5000/{base}{caminho}')"
        css = re.sub(r"url\(['\"]?(/[^)'\"]+)['\"]?\)", reescrever_url, resp.text)
        return css.encode('utf-8'), "permitido"
    
    return resp.content, "permitido"

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