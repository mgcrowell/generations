#the simpilest client money can buy
import socket
import os
import json

def clear_terminal():
    """Clears the terminal screen based on the operating system."""
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For macOS and Linux
    else:
        _ = os.system('clear')

def start_client(ip, port):
    print(f"Connecting to Server: {ip}:{port}")
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    movement_commands = {
                    'w':'MOVE_UP',
                    's':'MOVE_DOWN', 
                    'a':'MOVE_LEFT',
                    'd':'MOVE_RIGHT'
                }    
    try:
        client_socket.connect((ip,port))
        data = client_socket.recv(1024).decode()
        print(f"Server asked: {data}")
        
        # Respond "yes" to identify as operator
        client_socket.send(b"no\n")
        
        while True:
            clear_terminal()
            # Receive Data from Server
            data = client_socket.recv(4096).decode()
            if not data:
                print("Server Disconnected")
                break
            print(data, end='')
            
            # Provide input on server ask
            if '>' in data or ':' in data or '?' in data:
                user_input = input().strip()
                if user_input in ['w','a','s','d']:
                    command = movement_commands[user_input]
                    client_socket.send(f"{command}\n".encode())
                elif user_input.upper() == "POSITIONS":
                    receive_positions(client_socket)
                    # Don't send anything to server after returning from positions
                else:
                    command = user_input
                    client_socket.send(f"{command}\n".encode())
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client_socket.close()

def receive_positions(client_socket):
    clear_terminal()
    client_socket.send('POSITIONS\n'.encode())  # Added newline for consistency
    try:
        data = client_socket.recv(4096).decode()
        positions = json.loads(data)
        
        print("=== CURRENT POSITIONS ===")
        for entity in positions:
            print(f"  {entity['type'].title()}: {entity['name']} at ({entity['x']}, {entity['y']})")
        
        input("\nPress Enter to go back.")
        # Don't clear terminal here - let the main loop handle it
        
    except json.JSONDecodeError:
        print("Raw response:", data)
        input("\nPress Enter to go back.")

"""Starting the Server Here"""
if __name__ == "__main__":
    string = input("Enter IP:PORT(Press Enter for Default): ")
    if string == '':
        ip = 'localhost'
        port = 8888
    else:
        ip_full = string.split(':')
        ip = ip_full[0]
        port = int(ip_full[1])  # Fixed: convert port to integer
    start_client(ip, port)