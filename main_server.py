import socket 
import threading
import time
import sys
class user_data:
    def __init__(self):
        self.sending_socket = None
        self.receiving_socket = None


class Server:
    def __init__(self, ip_addr , port_num):
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.bind((ip_addr,port_num))
        self.server.listen()
        self.temp = []
        self.receiving_sockets = []
        self.usernames = []
        self.num_users = 0
        self.get_sockets_by_username = {}
        self.get_username_by_socket = {}
        self.registered = {}
        self.get_receiver_from_sender = {}
        
        print("Server Started at port number "+ str(port_num) +"....")

    def send_to_all(self,sender,sender_name,message):
        protocol = "FORWARD "+"@"+sender_name+ "\n" +"Content-length: " + str(len(message)) + "\n\n" + message
        print(protocol)
        for user in self.receiving_sockets:
            if self.get_username_by_socket[user] != sender_name:
                user.send(protocol.encode('utf-8'))
    

    def encrypt(self,message):
        for i in range(len(message)):
            message = message[:i] +  chr(2*ord(message[i])+7)+ message[i+1:]

        return message

    def decrypt(self,message):
        for i in range(len(message)):
            message = message[:i] +  chr((ord(message[i])-7)//2)+ message[i+1:]

        return message
    
    def get_username(self , message):
        return message[16:-2]

    def close_conn(self , user):
        message = "ERROR 103 Header incomplete\n\n"
        name_user = self.get_username_by_socket[user]
        self.get_sockets_by_username[self.get_username_by_socket[user]].receiving_socket.send(message.encode('utf-8'))
        receving_socket =  self.get_sockets_by_username[name_user].receiving_socket
        del self.get_username_by_socket[receving_socket]
        del self.get_username_by_socket[user]
        time.sleep(1)
        self.get_sockets_by_username[name_user].receiving_socket.close()
        self.get_sockets_by_username[name_user].sending_socket.close()
        del self.get_sockets_by_username[name_user]

    def handle_requests(self,user):
        registered = False
        while True:
            try:
                # print("keyset:",self.get_sockets_by_username)
                message = user.recv(1024).decode('utf-8')
                print(message)
                if message[:3] == "REG":
                    if message[11] == 'S':
                        name = self.get_username(message)
                        print("name" , name)
                        if not name.isalnum():
                            if not name in self.get_sockets_by_username.keys():
                                self.get_sockets_by_username[name] = user_data()    
                            self.get_sockets_by_username[name].sending_socket = user
                            err_msg = "Error 100 Malformed username\n\n"
                            user.send(err_msg.encode('utf-8'))
                            self.get_username_by_socket[user] = name
                            self.registered[name] = 0
                        
                        elif name in self.get_sockets_by_username.keys():
                            self.get_sockets_by_username[name].sending_socket = user
                            ack = "REGISTERED TOSEND "+name
                            user.send(ack.encode('utf-8'))
                            self.get_username_by_socket[user] = name 
                            registered = True
                            self.registered[name] = 1
                        else:
                            self.get_sockets_by_username[name] = user_data()
                            self.get_sockets_by_username[name].sending_socket = user
                            ack = "REGISTERED TOSEND "+name
                            user.send(ack.encode('utf-8'))
                            self.get_username_by_socket[user] = name    
                            registered = True
                            self.registered[name] = 1

                                            
                    elif message[11] == 'R':
                        name = self.get_username(message)
                        if not name.isalnum():
                            if not name in self.get_sockets_by_username.keys():
                                self.get_sockets_by_username[name] = user_data()
                            self.get_sockets_by_username[name].receiving_socket = user
                            err_msg = "Error 100 Malformed username\n\n"
                            user.send(err_msg.encode('utf-8'))
                            self.get_username_by_socket[user] = name
                            self.registered[name] = 0
                            
                        
                        elif name in self.get_sockets_by_username.keys():
                            self.get_sockets_by_username[name].receiving_socket = user
                            ack = "REGISTERED TORECV "+name
                            self.get_sockets_by_username[name].receiving_socket.send(ack.encode('utf-8'))
                            self.receiving_sockets.append(user)
                            self.get_username_by_socket[user] = name
                            registered = True
                            self.registered[name] = 1
                            
                        else:
                            self.get_sockets_by_username[name] = user_data()
                            self.get_sockets_by_username[name].receiving_socket = user
                            ack = "REGISTERED TORECV "+name
                            self.get_sockets_by_username[name].receiving_socket.send(ack.encode('utf-8'))
                            self.receiving_sockets.append(user)
                            self.get_username_by_socket[user] = name
                            registered = True
                            self.registered[name] = 1
                        
                        return    
                    else:
                        print("Error\n")
                elif not registered:
                        err_msg = "Error 101 No user registered\n\n"
                        try:
                            cur_name = self.get_username_by_socket[user]
                            # print(err_msg , user)
                            self.get_sockets_by_username[cur_name].receiving_socket.send(err_msg.encode('utf-8')) 
                        except:
                            user.send(err_msg.encode('utf-8'))          
                elif message[:4]=="SEND":
                    # try:
                    divided_message = message.split(maxsplit = 4)
                    
                    print(divided_message,"divided Message")
                    cur_name = self.get_username_by_socket[user]
                    print("curename", cur_name)
                    if len(divided_message)<5:
                        message = "ERROR 103a Header incomplete.Closing Connection\n\n"
                        name_user = self.get_username_by_socket[user]
                        print(name_user,"name")
                        self.get_sockets_by_username[self.get_username_by_socket[user]].receiving_socket.send(message.encode('utf-8'))
                        receving_socket =  self.get_sockets_by_username[name_user].receiving_socket
                        del self.get_username_by_socket[receving_socket]
                        del self.get_username_by_socket[user]
                        self.get_sockets_by_username[name_user].receiving_socket.close()
                        self.get_sockets_by_username[name_user].sending_socket.close()
                        del self.get_sockets_by_username[name_user]
                        return 

                    elif divided_message[0]!="SEND":
                        error_message = "ERROR 103b Header Incomplete\n\n"
                        print(error_message)
                        # self.get_sockets_by_username[cur_name].receiving_socket.send(error_message.encode('utf-8'))
                        self.close_conn(user)
                        return
                        pass
                    elif divided_message[1][0]!="@":
                        error_message = "ERROR 103c Header Incomplete\n\n"
                        print(error_message)
                        # self.get_sockets_by_username[cur_name].receiving_socket.send(error_message.encode('utf-8'))
                        self.close_conn(user)
                        return
                        pass
                    elif divided_message[2]!="Content-length:":
                        error_message = "ERROR 103d Header Incomplete\n\n"
                        print(error_message)
                        # self.get_sockets_by_username[cur_name].receiving_socket.send(error_message.encode('utf-8'))
                        self.close_conn(user)
                        return
                        pass
                    elif int(divided_message[3])!=len(divided_message[4]):
                        error_message = "ERROR 103e Header Incomplete\n\n"
                        print(error_message)
                        # self.get_sockets_by_username[cur_name].receiving_socket.send(error_message.encode('utf-8'))
                        self.close_conn(user)
                        return
                        pass

                    elif divided_message[1] == "@all":
                        #send to all
                        self.send_to_all(user , self.get_username_by_socket[user] , divided_message[4])
                        pass
                    else:
                        print("keyseet:",self.get_sockets_by_username.keys())

                        if divided_message[1][1:] in self.get_sockets_by_username.keys() and self.registered[divided_message[1][1:]]==1:
                            self.unicast(self.get_username_by_socket[user],divided_message[1][1:],divided_message[4])    
                        else:
                            
                            message = "ERROR 102 Unable to send\n\n"
                            self.get_sockets_by_username[cur_name].receiving_socket.send(message.encode('utf-8'))   
                    # except:
                    #         print("Checl\n")
                    #         self.close_conn(user)
                            
                    #         return 
                            
                            

                elif message[:3]== "REC":
                    divided_message = message.split(maxsplit = 2)
                    if divided_message[1][1:] in self.get_sockets_by_username.keys():
                        print("saree ",self.get_username_by_socket[user] , divided_message[1][1:] )
                        ack = "SENT @"+ self.get_username_by_socket[user] + "\n\n"
                        self.get_sockets_by_username[divided_message[1][1:]].receiving_socket.send(ack.encode('utf-8'))
                elif message[:5]=="REPLY":
                    divided_message = message.split(maxsplit = 2)
                    print(divided_message,"divided Messagse")
                    err_msg = "ERROR 103 header incomplete\n\n"
                    self.get_sockets_by_username[divided_message[1][1:]].receiving_socket.send(err_msg.encode('utf-8'))



                else:

                    message = "ERROR 103 Header incomplete.Closing Connection\n\n"
                    name_user = self.get_username_by_socket[user]
                    self.get_sockets_by_username[self.get_username_by_socket[user]].receiving_socket.send(message.encode('utf-8'))
                    receving_socket =  self.get_sockets_by_username[name_user].receiving_socket
                    del self.get_username_by_socket[receving_socket]
                    del self.get_username_by_socket[receving_socket]
                    del self.get_sockets_by_username[name_user]
                    self.get_sockets_by_username[name_user].receiving_socket.close()
                    self.get_sockets_by_username[name_user].sending_socket.close()
                    del self.get_sockets_by_username[name_user]
                    return 
            except:
                print("No Network\n")    
                break
    def unicast(self ,sender, receiptent , message):
         protocol = "FORWARD "+"@"+sender+ "\n" +"Content-length: " + str(len(message)) + "\n\n" + message
         self.get_sockets_by_username[receiptent].receiving_socket.send(protocol.encode('utf-8'))

         
    def receive(self):
        while True:
            user_connection , user_addr = self.server.accept()
            curr_thread = threading.Thread(target = self.handle_requests , args=(user_connection,))
            curr_thread.start()
            self.num_users += 1



ipaddr = sys.argv[1]
portnum = int(sys.argv[2])
my_server = Server(ipaddr, portnum)
my_server.receive()