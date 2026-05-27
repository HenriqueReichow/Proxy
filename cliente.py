import socket

s = socket.socket()
s.connect(('192.168.50.206', 8080))

requisicao = (
    "POST /dados HTTP/1.0\r\n"
    "Host: 192.168.50.206\r\n"
    "\r\n"

    
)

s.send(requisicao.encode())

resposta = s.recv(4096)
print(resposta.decode())

s.close()
