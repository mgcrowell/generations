import socket
import json
import random
"""Generations Server Testing"""

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
#
# CLIENT -> SERVER: plain commands like "MOVE north", "ATTACK", "POSITIONS"
# SERVER -> CLIENT: always uses PROTOCOL_FORMAT
#
# ===============================

class GameState:
    def __init__(self):
        self.players = {}  # {slot:, id:, {"name": "Ari", "x": 0, "y": 0, "health": 100}}
        self.enemies = [{"id": 1, "name": "Demon", "x": 5, "y": 5, "health": 20}]
        self.available_slots = ['1','2','3','4']
        self.slot_to_player = {}
        self.battle = 0
    
    def add_player(self, name):
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
        return self.available_slots.copy()
    
    def get_player_by_slot(self, slot):
        """Get player data by slot number"""
        if slot in self.slot_to_player:
            return self.players.get(self.slot_to_player[slot])
        return None
    
    def add_enemies(self, id, x, y):
        # Nothing here yet!
        return 404
    
    def move_player(self, player_id, direction):
        #print(f"Moving Player {direction}".encode())
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

class GameServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.game_state = GameState()
    
    def start(self):
        """Start the main server loop"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Generations Server running on {self.host}:{self.port}")
        print("Waiting for players to connect...")
        
        while True:
            client_socket, address = server_socket.accept()
            print(f"New connection from {address}")
            # Handle the client
            self.handle_client(client_socket)
    
    def  handle_client(self, client_socket):
        prompt = "Are you operator?"
        client_socket.send(prompt.encode())
        #Process reponsonse
        response = client_socket.recv(1024).decode().strip().upper()
        if response == 'yes':
            self.handle_operator(client_socket)
        else:
            self.handle_player(client_socket)

    def handle_operator(self, client_socket):
        random()

    def handle_player(self, client_socket):
        """Handle one client connection"""
        player_id = None
        try:
            # Get player name
            client_socket.send(b"Welcome:\nEnter your name: ")
            name_data = client_socket.recv(1024)
            player_name = name_data.decode().strip()
            
            # Add player to game
            player_id = self.game_state.add_player(player_name)
            client_socket.send(f"Hello {player_name}! Use WASD to move, 'attack' to fight, 'quit' to exit\n".encode())
            
            # Main game loop for this client
            while True:
                # Send current game state
                player = self.game_state.players[player_id]
                status = f"\n=== {player['id']}: {player['name']} ===\n"
                status += f"Position: ({player['x']}, {player['y']})\n"
                status += f"Health: {player['health']}/{player['max_health']}\n"
                
                # Check for enemies near
                for enemy in self.game_state.enemies:
                    dist = abs(player['x'] - enemy['x']) + abs(player['y'] - enemy['y'])
                    if dist <= 2 and self.game_state.battle == 0:
                        status += f"You sense a {enemy['name']} nearby...\n"
                
                status += "\nWhat to do now...? > "
                client_socket.send(status.encode())
                
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
                print(command)

                if command == 'QUIT':
                    client_socket.send(b"Exiting\n")
                    break
                elif command in movement_commands:
                    direction = movement_commands[command]
                    result = self.game_state.move_player(player_id, direction)
                    if result["type"] == "ENCOUNTER":
                        client_socket.send(f"\n*** You are entering battle with {result['enemy']}! ***\n".encode())
                    else:
                        client_socket.send(f"Moved to ({result['x']}, {result['y']})\n".encode())
                elif command == 'ATTACK':
                    result = self.game_state.attack_enemy(player_id)
                    client_socket.send(f"*** BATTLE: {result['message']} ***\n".encode())
                elif command == 'ADD ENEMY':
                    client_socket.send(b"This command isn't functional\n")
                elif command == 'POSITIONS':
                    result = self.game_state.get_all_positions()
                    json_data = json.dumps(result)
                    client_socket.send(json_data.encode())
                    client_socket.send(b"Got positions\n")
                else:
                    client_socket.send(b"Unknown command. Use arrows to move, 'attack' to fight\n")
                    
        except Exception as e:
            print(f"Client error: {e}")
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

if __name__ == "__main__":
    server = GameServer()
    server.start()