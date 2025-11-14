#the first client rewrite we made it
import socket
import os
import json
import time
debug = True
# ===== PROTOCOL DEFINITION =====
# 
# MESSAGE FORMAT: "COMMAND_TYPE:DATA\n"
#
# SERVER COMMAND TYPES:
# - PLAYER_INFO: "player_data_json"
# - POSITIONS: "positions_json" 
# - ERROR: "error_message"
# - SUCCESS: "message"
# - PROMPT: "prompt_text"
# - UPDATE: "game_state"
#
# CLIENT COMMAND TYPES:
# - MOVE: "direction"           # north, south, east, west, up, down
# - ATTACK: "target_id"         # ID of enemy/player to attack
# - INTERACT: "object_id"       # ID of object to interact with
# - LOOK: ""                    # Get room description
# - INVENTORY: ""               # Check inventory
# - USE: "item_id"              # Use item from inventory
# - CHAT: "message"             # Send chat message
# - RESPONSE: "user_input"      # Response to server prompts
# - READY: ""                   # Client is ready for game start
#
# ===============================

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
    
#THE PROTOCOL MESSAGING IS HANDLED HERE   
    def _send_protocol_message(self, client_socket, command_type, data):
        """Send a message using the protocol format"""
        #Always create a structured message
        message_obj = {
            "type": command_type,
            "data": data,
            "timestamp": time.time()
        }
        message_str = json.dumps(message_obj) + "\n"
        if debug:
            print(f"Sending: {message_str.strip()}")

        client_socket.send(message_str.encode())
    
    def _send_response(self, client_socket, response_text):
        """Send a response using the protocol"""
        self._send_protocol_message(client_socket, "RESPONSE", response_text)
    
    def _send_move(self, client_socket, move_data):
        """Send a move using the protocol"""
        self._send_protocol_message(client_socket, "MOVE", move_data)
    
    def _send_attack(self, client_socket, attack_data):
        """Send an attack using the protocol"""
        self._send_protocol_message(client_socket, "ATTACK", attack_data)
    
    def _send_interact(self, client_socket, interact_data):
        """Send an interact using the protocol"""
        self._send_protocol_message(client_socket, "INTERACT", interact_data)
    def _send_use(self, client_socket, use_data):
        self._send_protocol_message(client_socket, "USE", use_data)

    def _send_chat(self, client_socket, chat_data):
        self._send_protocol_message(client_socket, "CHAT", chat_data)

    def _send_client_ready(self, client_socket, ready_data):
        self._send_protocol_message(client_socket, "READY", ready_data)
    

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
