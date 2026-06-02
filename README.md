# 🔀 Proxy HTTP com Flask

Um proxy HTTP desenvolvido em Python com Flask, capaz de interceptar, filtrar e registrar requisições web. Suporta substituição de palavras em páginas HTML, bloqueio de sites e log de acessos.

---

## 🧠 Justificativa da Escolha da Tecnologia

A dupla escolheu o framework Python Flask para o desenvolvimento do proxy HTTP devido à sua simplicidade, leveza e flexibilidade. O Flask permitiu construir uma aplicação modular sem a complexidade de frameworks maiores, e sua integração com a biblioteca `requests` facilitou o encaminhamento de requisições e o tratamento das respostas.

A estrutura minimalista também ajudou no entendimento do fluxo interno do proxy, permitindo maior controle sobre o comportamento das requisições e respostas. Comparado a sockets TCP puros, o Flask elimina a necessidade de implementar manualmente o parsing do protocolo HTTP.

---

## ✅ Vantagens percebidas

- **Simplicidade de implementação** — poucas configurações iniciais e curva de aprendizado reduzida
- **Leveza** — ideal para aplicações pequenas e experimentais como um proxy HTTP acadêmico
- **Integração com Python** — facilidade para manipular strings, arquivos JSON e logs
- **Flexibilidade** — permitiu implementar filtros de palavras, blacklist e logs sem depender de plugins externos
- **Grande comunidade** — ampla documentação e suporte online

---

## ⚠️ Dificuldades encontradas

- **Limitações nativas para proxy** — o Flask não foi criado para atuar como proxy HTTP, exigindo implementação manual de vários comportamentos
- **Tratamento de HTTPS** — o suporte transparente a HTTPS é complexo e não foi implementado
- **Gerenciamento de headers** — cabeçalhos como `Content-Length`, `Content-Encoding` e `Accept-Encoding` exigiram tratamento específico para evitar erros
- **Encoding de páginas** — sites que declaravam `ISO-8859-1` mas eram `UTF-8` causaram problemas de caracteres que exigiram detecção automática de encoding
- **URLs relativas** — recursos como imagens e CSS com caminhos relativos precisaram de lógica extra para ser corretamente redirecionados pelo proxy

---

## 📋 Funcionalidades

- **Proxy transparente** — redireciona requisições GET, POST, PUT, DELETE e PATCH
- **Filtro de palavras** — substitui termos indesejados em páginas HTML automaticamente (case-insensitive, não afeta tags HTML)
- **Bloqueio de sites** — impede acesso a domínios configurados na lista negra, retornando página personalizada
- **Log de acessos** — registra todas as requisições com timestamp, URL e ação tomada
- **Reescrita de links** — reescreve `href`, `src` e `action` para que os links internos continuem passando pelo proxy

---

## 🗂️ Estrutura do Projeto

```
proxy/
├── proxy.py            # Código principal do servidor proxy
├── words.json          # Mapa de palavras a substituir
├── blocked.json        # Lista de domínios bloqueados
├── log.txt             # Gerado automaticamente com os registros
├── static/
│   ├── blocked.html    # Página exibida ao bloquear um acesso
│   ├── painel.html     # Painel visual para disparar requisições de teste
│   └── post.html       # Formulário HTML para teste de POST
└── test.txt            # Comandos cURL para testes
```

---

## ⚙️ Requisitos

- Python 3.7+
- Flask
- Requests

Instale as dependências com:

```bash
pip install flask requests
```

---

## 🚀 Como Usar

### 1. Inicie o servidor

```bash
python proxy.py
```

O proxy estará disponível em `http://127.0.0.1:5000`.

### 2. Acesse sites pelo proxy

**Via navegador:** acesse URLs diretamente no formato:
```
http://localhost:5000/http://exemplo.com
```

**Via cURL:**
```bash
curl -v http://127.0.0.1:5000/http://exemplo.com
```

> ⚠️ **Atenção:** não use a flag `-x` do cURL — ela ativa o modo proxy nativo, que envia a requisição em um formato diferente e não é suportado nesta implementação. Use sempre o formato com a URL no caminho, como mostrado acima.

---

## 🧪 Exemplos de Teste

```bash
# Acesso transparente (GET)
curl -v http://127.0.0.1:5000/http://httpbin.org/get

# POST com dados
curl -v -X POST -d "usuario=luis&teste=1" http://127.0.0.1:5000/http://httpbin.org/post

# PUT
curl -v -X PUT -d "atualizar=sim" http://127.0.0.1:5000/http://httpbin.org/put

# DELETE
curl -v -X DELETE http://127.0.0.1:5000/http://httpbin.org/delete

# PATCH
curl -v -X PATCH -d "campo=modificado" http://127.0.0.1:5000/http://httpbin.org/patch

# Bloqueio de site
curl -v http://127.0.0.1:5000/http://www.sitex.com

# Filtro de palavras (página com conteúdo filtrado)
curl -v http://127.0.0.1:5000/http://httpforever.com
```

---

## 📝 Configuração

### Filtro de Palavras — `words.json`

Define pares `"palavra original": "substituto"`. A substituição é **case-insensitive**, não afeta texto dentro de tags HTML e ocorre em todo conteúdo HTML retornado.

```json
{
    "foda": "diabos",
    "merda": "macacos me mordam",
    "idiota": "ingênuo"
}
```

### Sites Bloqueados — `blocked.json`

Lista de domínios que terão acesso negado (retorna HTTP 403 com página personalizada).

```json
{
    "bloqueados": [
        "www.sitex.com",
        "redes-sociais.net",
        "joguinhos.io"
    ]
}
```

> Os arquivos `words.json` e `blocked.json` são carregados uma vez na inicialização do servidor. Para aplicar mudanças, reinicie o proxy.

---

## 📄 Formato do Log

O arquivo `log.txt` é gerado automaticamente e registra cada requisição no formato:

```
2026-05-28 18:43:57 | URL: httpforever.com | Ação: filtrado
2026-05-28 18:28:33 | URL: joguinhos.io    | Ação: bloqueado
2026-05-28 18:28:08 | URL: you.com         | Ação: permitido
```

| Ação | Descrição |
|------|-----------|
| `permitido` | Requisição encaminhada sem alterações |
| `filtrado` | Conteúdo HTML modificado pelo filtro de palavras |
| `bloqueado` | Acesso negado por estar na lista negra |

---

## ⚠️ Limitações

- Não suporta HTTPS de forma transparente (apenas HTTP)
- Recursos carregados via JavaScript dinâmico podem não passar pelo proxy
- Não implementa cache de respostas
- Não há autenticação no próprio proxy

---

## 📌 Observações

- O servidor roda na porta `5000` por padrão
- Os arquivos `blocked.json` e `words.json` devem existir antes de iniciar o servidor
- A pasta `static/` com o arquivo `blocked.html` é necessária para a página de bloqueio

## 🤖 Uso de Inteligência Artificial

A dupla utilizou IA como apoio durante o desenvolvimento,
principalmente para esclarecimento de dúvidas e geração de documentação.
Todo o código foi escrito e compreendido pela dupla. Detalhes completos no relatório técnico.