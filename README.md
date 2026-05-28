# 🔀 Proxy HTTP com Flask

Um proxy HTTP leve desenvolvido em Python com Flask, capaz de interceptar, filtrar e registrar requisições web. Suporta substituição de palavras em páginas HTML, bloqueio de sites e log de acessos.


---
## 🧠 Justificativa da Escolha da Tecnologia

A dupla escolheu utilizar o framework Python Flask para o desenvolvimento do proxy HTTP devido à sua simplicidade, leveza e flexibilidade. Como o objetivo principal do projeto era implementar um proxy funcional capaz de interceptar, filtrar e registrar requisições HTTP, o Flask permitiu construir rapidamente uma aplicação web modular sem a complexidade de frameworks maiores.

Além disso, o Flask possui integração simples com bibliotecas como `requests`, facilitando o encaminhamento de requisições HTTP e o tratamento das respostas recebidas. A estrutura minimalista também ajudou no entendimento do fluxo interno do proxy, permitindo maior controle sobre o comportamento das requisições e respostas.

---

## ✅ Vantagens percebidas

- **Simplicidade de implementação** — poucas configurações iniciais e curva de aprendizado reduzida
- **Leveza** — ideal para aplicações pequenas e experimentais como um proxy HTTP acadêmico
- **Integração com Python** — facilidade para manipular strings, arquivos JSON e logs
- **Flexibilidade** — permitiu implementar filtros de palavras, blacklist e logs sem depender de plugins externos
- **Grande comunidade** — ampla documentação e suporte online

---

## ⚠️ Dificuldades encontradas

- **Limitações nativas para proxy** — o Flask não foi criado especificamente para atuar como proxy HTTP, exigindo implementação manual de alguns comportamentos
- **Tratamento de HTTPS** — o suporte transparente a HTTPS é mais complexo e não foi implementado no projeto
- **Gerenciamento de headers e redirecionamentos** — algumas respostas HTTP exigiram tratamento específico para evitar erros ou incompatibilidades
- **Escalabilidade limitada** — comparado a soluções mais robustas como Node.js com middleware especializado ou proxies dedicados (`Squid`, `Nginx`), o Flask possui menor desempenho para grande volume de requisições

---


## 📋 Funcionalidades

- **Proxy transparente** — redireciona requisições GET, POST, PUT, DELETE e PATCH
- **Filtro de palavras** — substitui termos indesejados em páginas HTML automaticamente
- **Bloqueio de sites** — impede acesso a domínios configurados numa lista negra
- **Log de acessos** — registra todas as requisições com timestamp, URL e ação tomada
- **Página de bloqueio customizada** — exibe uma página HTML ao tentar acessar sites bloqueados

---

## 🗂️ Estrutura do Projeto

```
proxy/
├── proxy.py            # Código principal do servidor proxy
├── words.json          # Mapa de palavras a substituir
├── blocked.json        # Lista de domínios bloqueados
├── log.txt             # Gerado automaticamente com os registros
├── static/
│   └── blocked.html    # Página exibida ao bloquear um acesso
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

### 2. Configure seu cliente para usar o proxy

**Via navegador:** acesse URLs no formato:
```
http://localhost:5000/http://exemplo.com
```

**Via cURL** (usando flag `-x` para proxy):
```bash
curl -x http://127.0.0.1:5000 http://exemplo.com
```

---

## 🧪 Exemplos de Teste

```bash
# POST
curl -v -x http://127.0.0.1:5000 -X POST -d "usuario=luis&teste=1" http://httpbin.org/post

# PUT
curl -v -x http://127.0.0.1:5000 -X PUT -d "atualizar=sim" http://httpbin.org/put

# DELETE
curl -v -x http://127.0.0.1:5000 -X DELETE http://httpbin.org/delete

# PATCH
curl -v -x http://127.0.0.1:5000 -X PATCH -d "campo=modificado" http://httpbin.org/patch
```

---

## 📝 Configuração

### Filtro de Palavras — `words.json`

Define pares `"palavra original": "substituto"`. A substituição é **case-insensitive** e ocorre em todo conteúdo HTML retornado.

```json
{
    "foda": "diabos",
    "merda": "macacos me mordam",
    "idiota": "ingênuo"
}
```

### Sites Bloqueados — `blocked.json`

Lista de domínios que terão acesso negado (retorna HTTP 403).

```json
{
    "bloqueados": [
        "exemplo-bloqueado.com",
        "outro-site.com"
    ]
}
```

---

## 📄 Formato do Log

O arquivo `log.txt` é gerado automaticamente e registra cada requisição no formato:

```
2024-01-15 14:32:01 | URL: http://exemplo.com | Ação: permitido
2024-01-15 14:32:45 | URL: http://site-ruim.com | Ação: bloqueado
2024-01-15 14:33:10 | URL: http://exemplo.com/pagina | Ação: filtrado
```

**Possíveis ações:**
| Ação | Descrição |
|------|-----------|
| `permitido` | Requisição encaminhada sem alterações |
| `filtrado` | Conteúdo HTML modificado pelo filtro de palavras |
| `bloqueado` | Acesso negado por estar na lista negra |

---

## ⚠️ Limitações

- Não suporta HTTPS de forma transparente (apenas HTTP)
- Não implementa cache de respostas
- Não há autenticação no próprio proxy
- Redirecionamentos (`301`/`302`) não são seguidos automaticamente

---

## 📌 Observações

- O servidor roda na porta `5000` por padrão
- O arquivo `blocked.json` deve existir antes de iniciar o servidor
- A pasta `static/` com o arquivo `blocked.html` é necessária para a página de bloqueio
