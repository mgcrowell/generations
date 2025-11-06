#the first client rewrite we made it
import socket
import os
import json
import time

class GameClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        
    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def connect(self, ip, port):
        print(f"Connecting to Server: {ip}:{port}")
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def send_message(self, data):
        if self.connected:
            # caht gpt implement protocol here
            self.socket.send(json.dumps(data).encode())
    
    def receive_message(self):
        if self.connected:
            data = self.socket.recv(1024)
            return self.parse_message(data.decode())
        return None
    @staticmethod
    def parse_message(raw_message):
        try:
            message_str = raw_message.decode().strip()
            message_obj = json.loads(message_str)

            return{
                "type": message_obj.get("type"),
                "data": message_obj.get("data"),
                "timestamp": message_obj.get("timestamp")
            }
        except json.JSONDecodeError:
            return {"type": "ERROR", "data": "Invalid JSON Format"}

class PlayerGUI:
    def __init__(self, client):
        self.client = client
    
    def display_game_state(self, game_data):
        # Implement da GUI here
        pass
    
    def handle_input(self):
        # Handle player input and send to server
        movement_commands = {
            'w': 'MOVE_UP',
            's': 'MOVE_DOWN', 
            'a': 'MOVE_LEFT',
            'd': 'MOVE_RIGHT'
        }
        #Finish input handling logic

# Usage
if __name__ == "__main__":
    client = GameClient()
    gui = PlayerGUI(client)
    
    # Get connected for free
    string = input("Enter IP:PORT (Press Enter For Default): ")
    if string == '':
        ip, port = 'localhost', 8888
    else:
        ip, port = string.split(':')
        port = int(port)
    
    if client.connect(ip, port):
        # Start the game loop here
        print("Connected successfully!")
        client.socket.send(b"no\n")
        if client.socket:
            while True:
                raw = client.socket.recv(1024)
                if not raw:
                    break
                parsed = client.parse_message(raw)
                print(f"{parsed}")
                command = input(":")
                if command == "quit":
                    break
        else:
            print("Failed to connect")
client.clear_terminal()
