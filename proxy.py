from flask import Flask, request , Response
import requests, json, re, datetime
from urllib.parse import urljoin, urlparse

with open('words.json', 'r') as file:
    WORDS_FILTER = json.load(file)

with open('blocked.json', 'r') as bloq:
    BLOCKED_SITES = json.load(bloq)['bloqueados']

app = Flask(__name__) #instancia server

@app.route('/<path:url>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(url):
    
    # Corrige o bug do Flask que engole a barra dupla
    if url.startswith('http:/') and not url.startswith('http://'):
        url = url.replace('http:/', 'http://', 1)
    elif url.startswith('https:/') and not url.startswith('https://'):
        url = url.replace('https:/', 'http://', 1)

    if request.query_string:
        url_com_query = f"{url}?{request.query_string.decode('utf-8')}"
    else:
        url_com_query = url

    if blocked(url_com_query):
        register_log(url_com_query, "bloqueado") 
        return get_blocked_page(url_com_query), 403
    
    # Monta a URL lidando com caminhos relativos
    if not url_com_query.startswith("http://") and not url_com_query.startswith("https://"):
        referer = request.headers.get("Referer")
        
        if referer:
            ref_path = urlparse(referer).path.lstrip('/')
            
            # Conserta a barra dupla do referer também
            if ref_path.startswith('http:/') and not ref_path.startswith('http://'):
                ref_path = ref_path.replace('http:/', 'http://', 1)
            elif ref_path.startswith('https:/') and not ref_path.startswith('https://'):
                ref_path = ref_path.replace('https:/', 'https://', 1)

            if not ref_path.startswith("http://") and not ref_path.startswith("https://"):
                base_url = "http://" + ref_path
            else:
                base_url = ref_path
                
            target = urljoin(base_url, url_com_query)
        else:
            target = "http://" + url_com_query
    else:
        target = url_com_query

    method, headers, body = separate(request)
    print(f"DEBUG: Método: {method}, Target: {target}")

    try:
        resp = send_req(method, target, headers, body)
    except requests.exceptions.RequestException as e:
        register_log(url, "erro de conexao")
        return Response(f"Erro ao conectar com o destino: {e}", status=502)
    
    # Passamos o host atual (127.0.0.1:5000) adiante
    conteudo, acao = process_resp(resp, request.host)
    register_log(url, acao)
    
    headers_limpos = []
    for nome, valor in resp.headers.items():
        if nome.lower() not in ('content-encoding', 'content-length', 'transfer-encoding', 'connection'):
            if nome.lower() == 'content-type' and 'text/html' in valor.lower():
                valor = 'text/html; charset=utf-8'

            if nome.lower() == 'location':
                valor = f"http://{request.host}/{valor}"

            headers_limpos.append((nome, valor))

    return Response(conteudo, resp.status_code, headers_limpos)

def register_log(url, acao):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha_log = f"{timestamp} | URL: {url} | Ação: {acao}\n"
    
    with open('log.txt', 'a') as f:
        f.write(linha_log)

def filter_word(html):
    for termo, substituto in WORDS_FILTER.items():
        padrao = re.compile(re.escape(termo), re.IGNORECASE)
        html = padrao.sub(substituto, html)

    return html

def separate(req):
    method = req.method
    headers = {}
    for k,v in req.headers:
        # Adicionamos o 'accept-encoding' aqui para forçar o servidor a mandar texto puro
        if k.lower() not in ('host', 'content-length', 'accept-encoding'):
            headers[k] = v
    body = req.get_data()
    return method, headers, body

def send_req(method, url, headers, body):
    return requests.request(method=method, url=url, headers=headers, data=body, allow_redirects=False)

def process_resp(resp, host):
    content_type = resp.headers.get('Content-Type', '').lower()
    
    if 'text/html' in content_type:
        if resp.encoding is None or resp.encoding.lower() == 'iso-8859-1':
            resp.encoding = resp.apparent_encoding
        
        original = resp.text
        filtrado = filter_word(original)
        
        # Agora repassamos o host para reescrever os links certinho
        html_final = rewrite_links(filtrado, host)
        
        if filtrado != original:
            acao = "filtrado"
        else:
            acao = "permitido"
        
        return html_final.encode('utf-8'), acao  
    
    if 'text/css' in content_type:
        base = resp.url.split('/')[2]
        def reescrever_url(match):
            caminho = match.group(1)
            if caminho.startswith('http'):
                return f"url('{caminho}')"
            # Substituímos o localhost fixo pela variável host
            return f"url('http://{host}/{base}{caminho}')"
        css = re.sub(r"url\(['\"]?(/[^)'\"]+)['\"]?\)", reescrever_url, resp.text)
        return css.encode('utf-8'), "permitido"
    
    return resp.content, "permitido"


def rewrite_links(html, host):
    padrao = re.compile(r'(href|src|action)=([\'"])(https?://[^\'"]+)\2', re.IGNORECASE)
    
    def replace_link(match):
        atributo = match.group(1)
        aspa = match.group(2)
        url_original = match.group(3)
        
        # Se o link já tiver o nosso host, a gente ignora
        if host in url_original:
            return match.group(0)
            
        # Montamos a URL nova usando o host que você realmente está acessando
        return f"{atributo}={aspa}http://{host}/{url_original}{aspa}"
        
    return padrao.sub(replace_link, html)

def blocked(url):
    url_limpa = url.replace("http://", "").replace("https://", "")
    dom = url_limpa.split('/')[0]
        
    for site in BLOCKED_SITES:
        if (site in dom) or (dom in site):
            return True
    return False

def get_blocked_page(url):
    with open('static/blocked.html', 'r') as f:
        html = f.read()
    return html.replace("{{url}}", url)

if __name__ == '__main__':
    app.run(port = 5000)