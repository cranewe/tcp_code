import socket
import threading
import struct

SERVER_IP = '192.168.78.134'
SERVER_PORT = 8080

def reverse_string(s):
    return s[::-1]

def connnect_client(client_socket, addr):
    print(f"成功与客户端{addr}连接！\n")

    while True:
        try:
            #接收initialization报文
            init_data = client_socket.recv(6)
            if not init_data:
                break
            type_field, n_blocks = struct.unpack('!HI', init_data)
            if type_field != 1:
                continue

            #向client发送agree packet
            agree_packet = struct.pack('!H', 2)
            client_socket.send(agree_packet)

            for i in range(n_blocks):
                #逐一接收client的reverse request报文
                header = client_socket.recv(6)
                if not header:
                    break
                type_field, length = struct.unpack('!HI', header)
                if type_field != 3:
                    continue
                
                data = client_socket.recv(length).decode('utf-8')
                print(f"Block {i+1}: {data}")

                #进行反转
                reversed_data = reverse_string(data).encode('utf-8')
                
                #发送reverse answer packet
                reverse_answer_packet = struct.pack('!HI', 4, len(reversed_data)) + reversed_data
                client_socket.send(reverse_answer_packet)

        except Exception as e:
            print(f"客户端{addr}连接错误 : {e}")
            break

    client_socket.close()
    print(f"与客户端{addr}连接关闭")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        client_connecting = threading.Thread(target=connnect_client, args=(client_socket, addr))
        client_connecting.start()

if __name__ == "__main__":
    start_server()
