import socket
import struct
import random
import argparse

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def write_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)

def main(server_ip, server_port, file_path, lmin, lmax):
    data = read_file(file_path)
    total_length = len(data)
    
    #根据lmin和lmax依次生成block
    blocks = []
    i = 0
    while i < total_length:
        block_size = random.randint(lmin, lmax)
        if block_size>total_length-i:
            block_size=total_length-i
        blocks.append(data[i:i + block_size])
        i += block_size
    
    n_blocks = len(blocks)#block的总块数

    #创建TCP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))

    #发送initialization报文给server
    init_packet = struct.pack('!HI', 1, n_blocks)
    client.send(init_packet)

    #接收server的agree报文
    agree_packet = client.recv(2)
    type_field = struct.unpack('!H', agree_packet)[0]
    if type_field != 2:
        print("未接收到agree packet")
        client.close()
        return
    
    reversed_data = []
    print("成功与服务器建立连接！")
    for i, block in enumerate(blocks):
        length = len(block)
        reverse_request_packet = struct.pack('!HI', 3, length) + block.encode('utf-8')
        client.send(reverse_request_packet)
        
        #接收来自server的reverse packet
        header = client.recv(6)
        type_field, length = struct.unpack('!HI', header)
        if type_field != 4:
            print("未接收到reverse answer packet")
            client.close()
            return
        
        reversed_block = client.recv(length).decode('utf-8')
        reversed_data.append(reversed_block)
        print(f"Block {i+1}: {reversed_block}")

    final_reversed_content = ''.join(reversed_data[::-1])#将列表元素反转后拼接成字符串
    print("\n完整的反转文件如下:\n")
    print(final_reversed_content)
 
    client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP Client")
    parser.add_argument("server_ip", type=str, help="Server IP")
    parser.add_argument("server_port", type=int, help="Server port")
    parser.add_argument("file_path", type=str, help="ASCII file path")
    parser.add_argument("lmin", type=int, help="minimum length of block")
    parser.add_argument("lmax", type=int, help="maximum length of block")
    args = parser.parse_args()

    main(args.server_ip, args.server_port, args.file_path, args.lmin, args.lmax)
