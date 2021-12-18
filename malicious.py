import socket 
import threading
import sys
def send_mess(my_socket):
    while True:
        try:
            mess = input("Client>")
            my_socket.send(mess.encode('utf-8'))
        except:
            print("Connection Closed...")
            my_socket.close()
            return



def receive_mess(my_socket):
    while True:
        try:
            mess = my_socket.recv(1024).decode('utf-8')
            if mess=="":
                print("Connection Closed...")
                my_socket.close()
                return
            print("Server>"+mess)
        except:
            print("Connection Closed...")
            my_socket.close()
            return



ipaddr = sys.argv[1]
portnum = int(sys.argv[2])
my_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
my_socket.connect((ipaddr,portnum))

sending_thread = threading.Thread(target = send_mess , args = (my_socket,))
sending_thread.start()

receiving_thread = threading.Thread(target = receive_mess ,args = (my_socket,))
receiving_thread.start()


