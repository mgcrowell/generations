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

def parse_protocol_message(data):
    """Parse protocol messages in format 'COMMAND_TYPE:DATA\n'"""
    lines = data.strip().split('\n')
    messages = []
    
    for line in lines:
        if ':' in line:
            command_type, message_data = line.split(':', 1)
            try:
                # Try to parse as JSON if it looks like JSON
                if message_data.strip().startswith('{') or message_data.strip().startswith('['):
                    parsed_data = json.loads(message_data)
                else:
                    parsed_data = message_data
                messages.append({'type': command_type, 'data': parsed_data})
            except json.JSONDecodeError:
                messages.append({'type': command_type, 'data': message_data})
        else:
            # Handle non-protocol messages (backward compatibility)
            messages.append({'type': 'RAW', 'data': line})
    
    return messages

def display_protocol_message(message):
    """Display protocol messages in a user-friendly format"""
    msg_type = message['type']
    data = message['data']
    
    if msg_type == 'PROMPT':
        print(data, end='')
    elif msg_type == 'ERROR':
        print(f"ERROR: {data}")
    elif msg_type == 'SUCCESS':
        print(f"{data}")
    elif msg_type == 'PLAYER_INFO':
        print("=== PLAYER INFO ===")
        if isinstance(data, dict):
            print(f"ID: {data.get('id', 'N/A')}")
            print(f"Name: {data.get('name', 'N/A')}")
            print(f"Position: ({data.get('x', 0)}, {data.get('y', 0)})")
            print(f"Health: {data.get('health', 0)}/{data.get('max_health', 0)}")
        else:
            print(data)
    elif msg_type == 'POSITIONS':
        print("=== CURRENT POSITIONS ===")
        if isinstance(data, list):
            for entity in data:
                print(f"  {entity.get('type', 'unknown').title()}: {entity.get('name', 'Unknown')} at ({entity.get('x', 0)}, {entity.get('y', 0)})")
        else:
            print(data)
    elif msg_type == 'RAW':
        print(data, end='')

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
        
        # Receive initial prompt using protocol
        data = client_socket.recv(1024).decode()
        messages = parse_protocol_message(data)
        
        for msg in messages:
            if msg['type'] == 'PROMPT':
                print(f"Server: {msg['data']}")
        
        # Respond "no" to identify as player
        client_socket.send(b"no\n")
        
        while True:
            clear_terminal()
            # Receive Data from Server
            data = client_socket.recv(4096).decode()
            if not data:
                print("Server Disconnected")
                break
            
            # Parse and display protocol messages
            messages = parse_protocol_message(data)
            waiting_for_input = False
            
            for msg in messages:
                display_protocol_message(msg)
                if msg['type'] == 'PROMPT':
                    waiting_for_input = True
            
            # Provide input on server prompt
            if waiting_for_input:
                user_input = input().strip()
                if user_input in ['w','a','s','d']:
                    command = movement_commands[user_input]
                    client_socket.send(f"{command}\n".encode())
                elif user_input.upper() == "POSITIONS":
                    # POSITIONS command is now handled by the protocol
                    client_socket.send(f"POSITIONS\n".encode())
                else:
                    command = user_input
                    client_socket.send(f"{command}\n".encode())
                    
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client_socket.close()

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