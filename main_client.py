import socket
import threading
from tkinter import scrolledtext
from tkinter import *
from PIL import Image, ImageTk
import sys
class Client:
    def __init__(self,ip_addr,port_num1 , port_num2 , username, debug):
        self.username = username
        self.receiving_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.receiving_socket.connect((ip_addr,port_num2))
        self.sending_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sending_socket.connect((ip_addr,port_num1))
        self.debug = debug
        
        #gui_part
        self.connected = False
        self.app_icon = Image.open('./icon.png')
        self.app_icon = self.app_icon.resize((100, 100), Image.ANTIALIAS)
        self.interface_thread = threading.Thread(target = self.graphical_user_interface)
        self.receving_thread = threading.Thread(target = self.receive_messages)
        self.interface_thread.start()
        self.receving_thread.start()
        self.loaded = False    

    def graphical_user_interface(self):
        self.screen_window = Tk()
        self.screen_window.title("Client - "+ self.username)
        self.screen_window.configure(bg = "#333333") 
        self.app_icon = ImageTk.PhotoImage(self.app_icon)
        icon_label = Label(self.screen_window,image = self.app_icon)
        icon_label.pack(padx = 50,pady = 50)
        icon_label.place(x = 25,y=25,height = 100 , width = 100)
        self.screen_window.geometry("300x700")
        self.header = Label(self.screen_window ,text = "COL334 Assignment 2" ,bg = "#333333",fg = "white")
        self.header.place(x = 150 , y = 25)
        self.header.pack(padx = 200, pady = 35)
        self.header.config(font = ("Abadi MT Condensed Extra Bold",25))

        self.add_chat_area() 
        self.header_down = Label(self.screen_window ,text = "Type your mesage here:" ,bg = "#333333",fg = "white")
        self.header_down.config(font = ("Abadi MT Condensed Extra Bold",12))
        # self.header.place(x = 150 , y = 25)
        self.header_down.pack(padx = 20, pady = 5)

        self.typing_area = Text(self.screen_window , height = 2,bg = "darkgray")
        self.typing_area.pack(padx = 100,pady = 2)
        self.typing_area.config(font = ("Abadi MT Condensed Extra Bold",20))

        self.send_button = Button(self.screen_window,text = "Send" , bg= "black",fg = "white" , command = self.send_message)
        self.send_button.config(font = ("Abadi MT Condensed Extra Bold",12))
        self.send_button.pack(padx = 50,pady = 10)

        self.add_message_red("Hello "+ self.username+"\n")
        self.loaded = True
        self.initialize()
        self.screen_window.mainloop()
       
        
    def add_chat_area(self):
        self.chat_area = scrolledtext.ScrolledText(self.screen_window,bg = "darkgray")
        self.chat_area.config(state = "disabled")
        self.chat_area.pack(padx = 0 , pady = 10)
        self.chat_area.tag_config('sent-message', font = ("Abadi MT Condensed Extra Bold",20), foreground='black',justify= 'right',background = "lightgreen")  # <-- Change colors of texts tagged `name`
        self.chat_area.tag_config('self.header', font = ("Abadi MT Condensed Extra Bold",20), foreground='blue',justify= 'right',background = "white")  # <-- Change colors of texts tagged `name`
        self.chat_area.tag_config('received-message', font = ("Abadi MT Condensed Extra Bold",20),foreground='black',background = "#FFFFFF",justify = 'left') 
        self.chat_area.tag_config('notif-message', font = ("Abadi MT Condensed Extra Bold",12),foreground='red',background = "pink",justify = 'center') 
         

    def initialize(self):        
        self.register_to_receive()
        self.register_to_send()

    def wait_for_ack(self):
        while True:
            message = self.sending_socket.recv(1024).decode('utf-8')
            if message.find("REGISTERED TOSEND") !=-1:
                if self.debug:
                    self.add_message_red("Receving Socket successfully registered!\n")
                return
            if message.find("ERROR"):
                if self.debug:
                    self.add_message_red(message[:-1])
                return

    def register_to_send(self):
        message = "REGISTER TOSEND " + self.username + "\n\n"
        message = message.encode('utf-8')
        self.sending_socket.send(message)
        temp = threading.Thread(target = self.wait_for_ack())
        temp.start()

    def register_to_receive(self):
        message = "REGISTER TORECV " + self.username + "\n\n"
        message = message.encode('utf-8')
        self.receiving_socket.send(message)
             
    def encrypt(self,message):
        for i in range(len(message)):
            message = message[:i] +  chr(2*ord(message[i])+7)+ message[i+1:]
        return message

    def decrypt(self,message):
        for i in range(len(message)):
            message = message[:i] +  chr((ord(message[i])-7)//2)+ message[i+1:]
        return message
    

    def send_message(self):
        message = self.typing_area.get("1.0","end")
        (username, content) = message.split(maxsplit=1)
        content = self.encrypt(content)
        if message != "\n":
            protocol_m = "SEND "+username+"\n"+"Content-length: "+str(len(content))+"\n\n"+content
            self.add_message_green(message)
            self.sending_socket.send(protocol_m.encode('utf-8'))
        self.typing_area.delete("1.0","end")
        

    def add_message_green(self,message):
        self.chat_area.config(state = "normal")
        self.chat_area.insert('end',message,"sent-message")
        self.chat_area.yview('end')
        self.chat_area.config(state = "disabled")


    def add_message_red(self,message):
        self.chat_area.config(state = "normal")
        self.chat_area.insert('end',message,"notif-message")
        self.chat_area.yview('end')
        self.chat_area.config(state = "disabled")


    def add_message_white(self,message):
        self.chat_area.config(state = "normal")
        self.chat_area.insert("end",message,"received-message")
        self.chat_area.yview('end')
        self.chat_area.config(state = "disabled")


    def receive_messages(self):
        while True:
            try:
                if True:
                    message = self.receiving_socket.recv(1024).decode('utf-8')

                    print("message:",message,"mesageend"  )
                    if message=='':
                        return
                    if message[0:3] == 'REG':
                        if "TORECV" in message:
                            print("Receving Socket successfully registered!\n")
                            print(self.loaded)
                            if self.debug:
                                self.add_message_red("Receving Socket successfully registered!\n")
                        else:
                            print("Debug\n")
                            self.add_message_red("Debug:"+ message)
                    elif message[0] == 'E':
                        self.add_message_red(message[:-1])
                        # return
                        pass
                    elif message[0] == 'S':
                        divided_message = message.split(maxsplit = 2)
                        if self.debug:
                            self.add_message_red("Message Received by "+divided_message[1][1:]+"\n")
                        pass
                    elif message[0] == 'F':
                        try:
                            divided_message = message.split(maxsplit = 4)
                            print(divided_message)
                            if divided_message[0]!="FORWARD":
                                error_message = "REPLY "+ divided_message[1] +" ERROR 103 Header Incomplete\n\n"
                                self.sending_socket.send(error_message.encode('utf-8'))
                                pass
                            elif divided_message[1][0]!="@":
                                error_message = "REPLY "+ divided_message[1] +" ERROR 103 Header Incomplete\n\n"
                                self.sending_socket.send(error_message.encode('utf-8'))
                                pass
                            elif divided_message[2]!="Content-length:":
                                error_message = "REPLY "+ divided_message[1] +" ERROR 103 Header Incomplete\n\n"
                                self.sending_socket.send(error_message.encode('utf-8'))
                                pass
                            elif int(divided_message[3])!=len(divided_message[4]):
                                error_message = "REPLY "+ divided_message[1] +" ERROR 103 Header Incomplete\n\n"
                                self.sending_socket.send(error_message.encode('utf-8'))
                                pass

                            print(int(divided_message[3]) , len(divided_message[4]) , divided_message[2] , )
                            self.add_message_white(divided_message[1]+":"+ self.decrypt(divided_message[4]))
                            ack = "RECEIVED " + divided_message[1]+"\n\n"
                            self.sending_socket.send(ack.encode('utf-8'))
                            pass
                        except:
                            error_message = "ERROR 103 Header Incomplete\n\n"
                            self.sending_socket.send(error_message.encode('utf-8'))

                    else:
                        self.add_message_red("Debug:"+ message)

            except:
                self.add_message_red("Error 103 Header Incomplete\n")
                print("Closing connection....")
                self.sending_socket.close()
                self.receiving_socket.close()
                return

        
ipaddr = sys.argv[1]
portnum = int(sys.argv[2])

client = Client(ipaddr , portnum , portnum , sys.argv[3],True)