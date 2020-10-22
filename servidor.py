import socket
from threading import Thread
import json
import time

# Laboratórios de Redes e Sistemas Operacionais

# Rafael Alkmim Machado
# Ian Rodrigues dos Reis Paixão

class Server():
    def __init__(self, host='', port=33000, max_connections=5):
        if host is None or port is None:
            raise Exception('Faltam argumentos')
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = host if len(host) > 0 else socket.gethostbyname(socket.gethostname())
        self.PORT = port
        self.BUFSIZ = 2048
        origin = (host, port)
        self.SERVER.bind(origin)
        self.SERVER.listen(max_connections)
        self.cliente_nome = {}
        self.nome_cliente = {}
        print('HOST {} PORT {}'.format(self.HOST, self.PORT))

    def start(self):
        begining = time.time()
        print('Iniciou em', begining)
        while True:
            elapsed = time.time() - begining
            con, client = self.SERVER.accept()
            self.cliente_nome[con] = client
            # Iniciar Conexão
            print('{} conectado'.format(client))
            # Criação de threads
            Thread(target=self.handle, args=(con,)).start()

    def close(self):
        self.SERVER.close()
        # Fechar Conexão
        print('Conexão {}:{} fechada'.format(self.HOST, self.PORT))

    def handle(self, client):
        name = client.recv(self.BUFSIZ).decode("utf8")
        while name in self.nome_cliente:
            client.send(bytes("Nome em uso!", 'utf8'))
            name = client.recv(self.BUFSIZ).decode("utf8")

        if name == '{quit}':
            client.close()
            print('{} saiu'.format(self.cliente_nome[client]))
            del self.cliente_nome[client]
            return
        else:
            msg = "%s entrou na sala!" % name
            print(msg)
            self.to_group(bytes(msg, "utf8"))
            self.nome_cliente[name] = client
            self.cliente_nome[client] = name
            while True:
                # print(client)
                obj = client.recv(self.BUFSIZ)
                # print(obj)
                dic = json.loads(obj)
                # print(dic)
                destino = dic.get('destino', 'GROUP')

                if destino == 'GROUP':
                    self.to_group(bytes(dic['mensagem'], 'utf8'), '{}@GROUP: '.format(self.cliente_nome[client]))
                elif destino != 'quit':
                    self.to_person(dic, client)
                else:
                    # client.send(bytes("{quit}", "utf8"))
                    client.close()
                    print('{} fechado'.format(self.cliente_nome[client]))
                    del self.nome_cliente[self.cliente_nome[client]]
                    del self.cliente_nome[client]
                    self.to_group(bytes("%s deixou o chat." % name, "utf8"))
                    break

    def to_group(self, msg, prefix=''): 
        # Manda a mensagem pra todos os integrantes de um grupo
        for sock in self.cliente_nome:
            sock.send(bytes(prefix, "utf8")+msg)

    def to_person(self, dic, client):
        destino = self.nome_cliente.get(dic['destino'], None)
        if destino is None:
            client.send(bytes("DESTINO NÃO ENCONTRADO!"))
        else: 
            msg = "{}->{}: {}".format(self.cliente_nome[client], dic.get('destino'), dic.get('mensagem', ''))
            destino.send(bytes(msg, 'utf8'))
            client.send(bytes(msg, 'utf8'))
        

if __name__ == "__main__":
    server = Server()
    server.start()
    pass
