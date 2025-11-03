import socket
import json
import random
import threading

"""Generations Server Testing - Now With Threading!"""

# ===== PROTOCOL DEFINITION =====
# 
# MESSAGE FORMAT: "COMMAND_TYPE:DATA\n"
#
# COMMAND TYPES:
# - PLAYER_INFO: "PLAYER_INFO:player_data_json"
# - POSITIONS: "POSITIONS:positions_json" 
# - ERROR: "ERROR:error_message"
# - SUCCESS: "SUCCESS:message"
# - PROMPT: "PROMPT:prompt_text"
# - UPDATE: "UPDATE: game_state"
#
# CLIENT -> SERVER: plain commands like "MOVE north", "ATTACK", "POSITIONS"
# SERVER -> CLIENT: always uses PROTOCOL_FORMAT
#
# ===============================

class GameState:
    def __init__(self):
        self.players = {}  # {slot:, id:, {"name": "Ari", "x": 0, "y": 0, "health": 100}}
        self.enemies = [{"entity": 0,"id": 1, "name": "Demon", "x": 5, "y": 5, "health": 20}] #{entitiy: for global tracking, id: the unique id of an enemy, x: , y: , health:
        self.available_slots = ['1','2','3','4']
        self.slot_to_player = {}
        self.battle = 0
        self.lock = threading.Lock()  # Add thread lock for thread safety
    
    def add_player(self, name):
        with self.lock:  # Thread-safe access
            if not self.available_slots:
                print("No open slots!")
                return None
            slot = self.available_slots.pop(0)
            player_id = random.randint(0,256)
            print(f"Keep this safe! This is your unique player id!\nPlayer ID: {player_id}\n")
            
            self.players[player_id] = {
                "id": player_id,
                "name": name,
                "slot": slot,
                "y": 0,
                "x": 0,
                "health": 100,
                "max_health": 100
            }
            self.slot_to_player[slot] = player_id
            return player_id
    
    def remove_player(self, player_id):
        """Remove a player and free up their slot"""
        with self.lock:  # Thread-safe access
            if player_id in self.players:
                slot = self.players[player_id]["slot"]
                
                # Free up the slot
                self.available_slots.append(slot)
                self.available_slots.sort()  # Keep slots in order
                
                # Remove from tracking
                if slot in self.slot_to_player:
                    del self.slot_to_player[slot]
                
                # Remove player data
                del self.players[player_id]
                
                print(f"Player removed from slot {slot}")
    
    def get_available_slots(self):
        """Return list of available slots"""
        with self.lock:
            return self.available_slots.copy()
    
    def get_player_by_slot(self, slot):
        """Get player data by slot number"""
        with self.lock:
            if slot in self.slot_to_player:
                return self.players.get(self.slot_to_player[slot])
            return None
    
    def add_enemies(self, id, x, y):
        with self.lock:

    
    def move_player(self, player_id, direction):
        with self.lock:  # Thread-safe access
            player = self.players[player_id]
            dx, dy = 0, 0
            if direction == "UP": dy = 1
            elif direction == "DOWN": dy = -1
            elif direction == "LEFT": dx = -1
            elif direction == "RIGHT": dx = 1
            new_x, new_y = player["x"] + dx, player["y"] + dy
            
            # Check for enemies at new position
            for enemy in self.enemies:
                if enemy["x"] == new_x and enemy["y"] == new_y:
                    #Move to encounter!
                    self.battle = 0
                    player["x"] = new_x
                    player["y"] = new_y
                    return {"type": "ENCOUNTER", "enemy": enemy["name"]}
                
            # Normal Move
            player["x"] = new_x
            player["y"] = new_y
            return {"type": "MOVED", "x": new_x, "y": new_y}
    
    def get_all_positions(self):
        with self.lock:  # Thread-safe access
            # Get enemy positions
            enemy_positions = [
                {
                    "id": enemy["id"],
                    "name": enemy["name"], 
                    "x": enemy["x"],
                    "y": enemy["y"],
                    "type": "enemy"
                }
                for enemy in self.enemies
            ]
            
            # Get player positions
            player_positions = [
                {
                    "id": player_data["id"],
                    "name": player_data["name"],
                    "x": player_data["x"],
                    "y": player_data["y"], 
                    "type": "player"
                }
                for player_data in self.players.values()
            ]
            
            return enemy_positions + player_positions
    
    def attack_enemy(self, player_id):
        with self.lock:  # Thread-safe access
            player = self.players[player_id]
            # Find enemy at player position
            for enemy in self.enemies:
                if enemy["x"] == player["x"] and enemy["y"] == player["y"]:
                    damage = random.randint(10, 20)
                    enemy["health"] -= damage
                    if enemy["health"] <= 0:
                        self.enemies.remove(enemy)
                        return {
                            "type": "BATTLE_RESULT",
                            "message": f"You have slain {enemy['name']}...",
                            "enemy_defeated": True
                        }
                    else:
                        return {
                            "type": "BATTLE_RESULT",
                            "message": f"You hit {enemy['name']} for {damage} damage",
                            "enemy_defeated": False
                        }
            return {"type": "ERROR", "message": "No enemy to attack?"}

    def sate_update(self, player_id):
        #Updates Game State for player; position data for entities within 20x20 relative grid; player health; other stuff?
        with self.lock:
            #Get player data
            player = self.players[player_id]
            # Get enemy positions
            enemy_positions = [
                {
                    "id": enemy["id"],
                    "name": enemy["name"], 
                    "x": enemy["x"],
                    "y": enemy["y"],
                    "type": "enemy"
                }
                for enemy in self.enemies
                if abs(enemy['x'] - player['x']) <= 20 and abs(enemy['y'] - player['y']) <= 20
            ]
            # Get player data
            player_data = [
                {
                    "id": player_data["id"],
                    "name": player_data["name"],
                    "x": player_data["x"],
                    "y": player_data["y"],
                    "health": player_data["health"],
                    "type": "player"
                }
                for player_data in player
            ]
            
            return enemy_positions + player_data
class GameServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.game_state = GameState()
 #THE PROTOCOL MESSAGING IS HANDLED HERE   
    def _send_protocol_message(self, client_socket, command_type, data):
        """Send a message using the protocol format"""
        if isinstance(data, dict):
            data = json.dumps(data)
        message = f"{command_type}:{data}\n"
        client_socket.send(message.encode())
    
    def _send_prompt(self, client_socket, prompt_text):
        """Send a prompt using the protocol"""
        self._send_protocol_message(client_socket, "PROMPT", prompt_text)
    
    def _send_error(self, client_socket, error_message):
        """Send an error message using the protocol"""
        self._send_protocol_message(client_socket, "ERROR", error_message)
    
    def _send_success(self, client_socket, success_message):
        """Send a success message using the protocol"""
        self._send_protocol_message(client_socket, "SUCCESS", success_message)
    
    def _send_player_info(self, client_socket, player_data):
        """Send player information using the protocol"""
        self._send_protocol_message(client_socket, "PLAYER_INFO", player_data)
    
    def _send_positions(self, client_socket, positions_data):
        """Send positions data using the protocol"""
        self._send_protocol_message(client_socket, "POSITIONS", positions_data)
    def _send_update(self, client_socket, update_data):
        self._send_protocol_message(client_socket, "UPDATE", update_data)

    def start(self):
        """Start the main server loop"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Generations Server (Now with Threading!) running on {self.host}:{self.port}")
        print("Waiting for players to connect...")
        
        while True:
            client_socket, address = server_socket.accept()
            print(f"New connection from {address}")
            
            # Handle each client in a separate thread
            client_thread = threading.Thread(
                target=self.handle_client, 
                args=(client_socket,)
            )
            client_thread.daemon = True  # Allow thread to exit when main program exits
            client_thread.start()
            print(f"Active threads: {threading.active_count() - 1}")  # Subtract main thread
    
    def handle_client(self, client_socket):
        self._send_prompt(client_socket, "Are you operator?")
        # Process response
        response = client_socket.recv(1024).decode().strip().upper()
        if response == 'YES':
            self.handle_operator(client_socket)
        else:
            self.handle_player(client_socket)
    
    def handle_operator(self, client_socket):
        # Your operator logic here
        self._send_error(client_socket, "Operator mode not implemented yet")
        client_socket.close()
    
    def handle_player(self, client_socket):
        """Handle one client connection in its own thread"""
        player_id = None
        try:
            # Get player name
            self._send_prompt(client_socket, "Welcome:\nEnter your name: ")
            name_data = client_socket.recv(1024)
            player_name = name_data.decode().strip()
            
            # Add player to game
            player_id = self.game_state.add_player(player_name)
            if player_id is None:
                self._send_error(client_socket, "Server is full! Try again later.")
                return
            
            # Send player info
            player_data = self.game_state.players[player_id]
            self._send_player_info(client_socket, player_data)
            self._send_success(client_socket, f"Hello {player_name}! Use WASD to move, 'attack' to fight, 'quit' to exit")
            
            # Main game loop for this client
            while True:
                # Send current game state as player info
                player = self.game_state.players[player_id]
                status = f"\n=== {player['id']}: {player['name']} ===\n"
                status += f"Position: ({player['x']}, {player['y']})\n"
                status += f"Health: {player['health']}/{player['max_health']}\n"
                
                # Check for enemies near
                for enemy in self.game_state.enemies:
                    dist = abs(player['x'] - enemy['x']) + abs(player['y'] - enemy['y'])
                    if dist <= 2 and self.game_state.battle == 0:
                        status += f"You sense a {enemy['name']} nearby...\n"
                
                self._send_prompt(client_socket, status + "\nWhat to do now...? > ")
                
                # Get player input
                data = client_socket.recv(1024)
                if not data:
                    break
                
                command = data.decode().strip().upper()
                # Movement command mapping
                movement_commands = {
                    'MOVE_UP': 'UP',
                    'MOVE_DOWN': 'DOWN', 
                    'MOVE_LEFT': 'LEFT',
                    'MOVE_RIGHT': 'RIGHT'
                }
                print(f"Player {player_id}: {command}")
                
                if command == 'QUIT':
                    self._send_success(client_socket, "Exiting")
                    break
                elif command in movement_commands:
                    direction = movement_commands[command]
                    result = self.game_state.move_player(player_id, direction)
                    if result["type"] == "ENCOUNTER":
                        self._send_success(client_socket, f"\n*** You are entering battle with {result['enemy']}! ***")
                    else:
                        self._send_success(client_socket, f"Moved to ({result['x']}, {result['y']})")
                elif command == 'ATTACK':
                    result = self.game_state.attack_enemy(player_id)
                    self._send_success(client_socket, f"*** BATTLE: {result['message']} ***")
                elif command == 'ADD ENEMY':
                    self._send_error(client_socket, "This command isn't functional")
                elif command == 'POSITIONS':
                    result = self.game_state.get_all_positions()
                    self._send_positions(client_socket, result)
                    self._send_success(client_socket, "Got positions")
                else:
                    self._send_error(client_socket, "Unknown command. Use arrows to move, 'attack' to fight")
                    
        except Exception as e:
            print(f"Client error: {e}")
            self._send_error(client_socket, f"Server error: {str(e)}")
        finally:
            client_socket.close()
            if player_id and player_id in self.game_state.players:
                try:
                    self.game_state.remove_player(player_id)
                    print(f"Player {player_id} disconnected")
                    slots = self.game_state.get_available_slots()
                    print(f"Available slots: {slots}")
                except KeyError:
                    print(f"Player {player_id} was already removed")
                except Exception as e:
                    print(f"Error during player removal: {e}")

#Entry Point
if __name__ == "__main__":
    server = GameServer()
    server.start()