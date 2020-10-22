from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import re
import json

c=0

def receive():
    global c;
    #Handles receiving of messages.
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if msg == 'Nome em uso!':
                c+=-1 
            msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break

def send(event=None):  # event is passed by binders.
    #Handles sending of messages.
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
        my_msg.set("")  # Clears input field.
    
        msg = json.dumps(dic)
        client_socket.send(bytes(msg, "utf8"))
        # print(msg)
        if name == "quit":
            client_socket.close()
            top.quit()
            print('connection closed')
    else:
        msg = my_msg.get()
        my_msg.set("")  # Clears input field.
        client_socket.send(bytes(msg, "utf8"))
        if msg == "{quit}":
            client_socket.close()
            top.quit()
            print('connection closed')
        c=+1
    

def on_closing(event=None):
    #This function is to be called when the window is closed.
    my_msg.set("{quit}")
    send()
    print("connection closed")

if __name__ == "__main__":
    top = tkinter.Tk()
    top.title("Chat In a Box")
    messages_frame = tkinter.Frame(top)
    my_msg = tkinter.StringVar()  # For the messages to be sent.
    my_msg.set("Type your messages here.")
    scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
    msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    msg_list.pack()
    messages_frame.pack()
    entry_field = tkinter.Entry(top, textvariable=my_msg)
    entry_field.bind("<Return>", send)
    entry_field.pack()
    send_button = tkinter.Button(top, text="Send", command=send)
    send_button.pack()
    # button to send a delete query
    send_button = tkinter.Button(top, text="Sakujo username ", command=send)
    send_button.pack()
    top.protocol("WM_DELETE_WINDOW", on_closing)

    HOST = input('Enter host: ')
    PORT = input('Enter port: ')

    if not PORT:
        PORT = 5000  # Default value.
    else:
        PORT = int(PORT)

    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)

    receive_thread = Thread(target=receive)
    receive_thread.start()
    tkinter.mainloop()  # Starts GUI execution.

