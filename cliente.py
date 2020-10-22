from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import re
import json
import sqlite3

c=0
db=sqlite3.connect('lab_redes.db')

def createTable():
    try:
        cur=db.cursor()
        cur.execute('''CREATE TABLE users (
                       UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT (20) NOT NULL,
                       password TEXT (20) NOT NULL
                       );''')
        print ('Tabela criada com sucesso')
    except:
        db.rollback()

def login(name,password):
    qry="SELECT from users where name=?, password=?;"
    try:
        cur=db.cursor()
        cur.execute(qry, (name,password))
        print(cur.fetchone())
        return True
    except:
        db.rollback()
        return False

def userList():
    try:
        cur=db.cursor()
        cur.execute("SELECT name FROM users;")
        print(cur.fetchone())
    except:
        db.rollback()
        return False

def createUser(name,password):
    try:
        cur=db.cursor()
        cur.execute("insert into users (name, password) values(?, ?);", (name,password))
        db.commit()
        print ("Registrado com sucesso")
    except:
        print("Erro na execução")
        db.rollback()

def updateUsername(current_name,name):
    qry="update users set name=?, where name=?;"
    try:
        cur=db.cursor()
        cur.execute(qry, (name,current_name))
        db.commit()
        print("Registro atualizado com sucesso")
    except:
        print("Erro na execução")
        db.rollback()

def updateUserpassword(name,password):
    qry="update users set password=? where name=?;"
    try:
        cur=db.cursor()
        cur.execute(qry, (password,name))
        db.commit()
        print("Registro atualizado com sucesso")
    except:
        print("Erro na execução")
        db.rollback()

def deleteUser(name):
    print(name)
    qry="DELETE from users where name=?;"
    try:
        cur=db.cursor()
        cur.execute(qry, (name))
        db.commit()
        print("Registro excluído com sucesso")
    except:
        print("Erro na execução")
        db.rollback()

def deleteTable():   
    try:
        cur=db.cursor()
        cur.execute('DROP TABLE users;')
        db.commit()
        print("Tabela excluída com sucesso")
    except:
        print("Erro na execução")
        db.rollback()
        db.close()

def receive():
    global c;
    #Handles receiving of messages.
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if msg == 'Nome em uso!':
                c+=-1 
            msg_list.insert(tkinter.END, msg)
        except OSError:  # Cliente deixou o chat
            break

def send(event=None): 
    # Gerencia o envio de mensagens
    global c;
    # print(c)
    if c > 0:
        dic = {} 
        pattern = '{(.+?)}'
        msg = my_msg.get()  
        name = re.search(pattern, msg)
        if name:
            name = name.group(1)
            dic['destino'] = name 
        else:
            name = ''
        msg = re.sub(pattern, '', msg)
        msg = msg.strip() 
        dic['mensagem'] = msg 
        my_msg.set("") # Limpa o campo de enviar texto
    
        msg = json.dumps(dic)
        client_socket.send(bytes(msg, "utf8"))
        # print(msg)
        if name == "quit":
            client_socket.close()
            top.quit()
            print('Conexão Encerrada')
    else:
        msg = my_msg.get()
        my_msg.set("")  # Limpa o campo de enviar texto
        client_socket.send(bytes(msg, "utf8"))
        if msg == "{quit}":
            client_socket.close()
            top.quit()
            print('Conexão Encerrada')
        c=+1


def on_closing(event=None):
    # Fechar conexão quando a janela é fechada
    my_msg.set("{quit}")
    send()
    print("Conexão Encerrada")

def menu():
    print("Escolha uma das opções:\n1 - Login\n2 - Cadastro\n3 - Opções")
    option = input()

    if option == '1':
        name = input('Insira seu nome:\n')
        password = input('Insira sua senha:\n')
        login(name,password)
        return name
    elif option == '2':
        name = input('Insira seu nome:\n')
        password = input('Insira sua senha:\n')
        createUser(name,password)
        return name
    else:
        print("1 - Atualizar nome\n2 - Atualizar senha\n3 - Excluir Usuário\n4 - Listar Usuários")
        option = input()
        if option == '1':
            current_name = input('Insira seu nome atual:\n')
            name = input('Insira o novo nome:\n')
            updateUsername(current_name,name)
            menu()
        elif option == '2':
            name = input('Insira seu nome:\n')
            password = input('Insira a nova senha:\n')
            updateUserpassword(name,password)
            menu()
        elif option == '3':
            name = input('Insira seu nome:\n')    
            deleteUser(name)
            menu()
        else:
            userList()
            menu()    
        

if __name__ == "__main__":

    createTable()
    HOST = ''
    PORT = 33000
    print("Bem-Vindo!")
    usuario = menu()

    top = tkinter.Tk()
    top.title("Bate-Papo")
    messages_frame = tkinter.Frame(top)
    my_msg = tkinter.StringVar()  # Para as mensagens a serem enviadas.
    my_msg.set(usuario)
    scrollbar = tkinter.Scrollbar(messages_frame)  # Para navegação entre as mensagens.
    msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    msg_list.pack()
    messages_frame.pack()
    entry_field = tkinter.Entry(top, textvariable=my_msg)
    entry_field.bind("<Return>", send)
    entry_field.pack()
    send_button = tkinter.Button(top, text="Enviar", command=send)
    send_button.pack()
    top.protocol("WM_DELETE_WINDOW", on_closing)

    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)

    receive_thread = Thread(target=receive)
    receive_thread.start()