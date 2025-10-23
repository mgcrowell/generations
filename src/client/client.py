#the simpilest client money can buy
import socket

def start_client():
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        client_socket.connect(('localhost',8888))

        while True:
            # Recieve Data from Server
            data = client_socket.recv(4096).decode()
            if not data:
                print("Server Disconnected")
                break
            print(data, end='')

            #Provide input on server ask
            if '>' in data or ':' in data or '?' in data:
                user_input = input()
                client_socket.send(f"{user_input}\n".encode())

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client_socket.close()
if __name__ == "__main__":
    print("Connecting to Server...")
    start_client()