import socket
import json
import random

class GameState:
    def __init__(self):
        self.players = {}  # {player_id: {"name": "Ari", "x": 0, "y": 0, "health": 100}}
        self.enemies = [{"id": 1, "name": "Demon", "x": 5, "y": 5, "health": 50}]
        self.next_player_id = 1
    
    def add_player(self, name):
        player_id = self.next_player_id
        self.next_player_id += 1
        self.players[player_id] = {
            "name": name,
            "y": 0,
            "x": 0,
            "health": 100,
            "max_health": 100
        }
        return player_id
    
    def add_enemies(self, id, x, y):
        # Nothing here yet!
        return 404
    
    def move_player(self, player_id, direction):
        player = self.players[player_id]
        dx, dy = 0, 0
        if direction == "w": dy = -1
        elif direction == "s": dy = 1
        elif direction == "a": dx = -1
        elif direction == "d": dx = 1
        new_x, new_y = player["x"] + dx, player["y"] + dy
        
        # Check for enemies at new position
        for enemy in self.enemies:
            if enemy["x"] == new_x and enemy["y"] == new_y:
                return {"type": "ENCOUNTER", "enemy": enemy["name"]}
            
        # Complete the Move
        player["x"] = new_x
        player["y"] = new_y
        return {"type": "MOVED", "x": new_x, "y": new_y}
    
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
            
    def handle_client(self, client_socket):
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
                status = f"\n=== {player['name']} ===\n"
                status += f"Position: ({player['x']}, {player['y']})\n"
                status += f"Health: {player['health']}/{player['max_health']}\n"
                
                # Check for enemies near
                for enemy in self.game_state.enemies:
                    dist = abs(player['x'] - enemy['x']) + abs(player['y'] - enemy['y'])
                    if dist <= 2:
                        status += f"You sense a {enemy['name']} nearby...\n"
                
                status += "\nWhat to do now...? > "
                client_socket.send(status.encode())
                
                # Get player input
                data = client_socket.recv(1024)
                if not data:
                    break
                
                command = data.decode().strip().lower()
                print(command)
                
                if command == 'quit':
                    client_socket.send(b"Exiting\n")
                    break
                elif command in ['w', 'a', 's', 'd']:
                    result = self.game_state.move_player(player_id, command)
                    if result["type"] == "ENCOUNTER":
                        client_socket.send(f"\n*** You are entering battle with {result['enemy']}! ***\n".encode())
                    else:
                        client_socket.send(f"Moved to ({result['x']}, {result['y']})\n".encode())
                elif command == 'attack':
                    result = self.game_state.attack_enemy(player_id)
                    client_socket.send(f"*** BATTLE: {result['message']} ***\n".encode())
                elif command == 'add enemy':
                    client_socket.send(b"This command isn't functional\n".encode())
                else:
                    client_socket.send(b"Unknown command. Use WASD to move, 'attack' to fight\n".encode())
                    
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            client_socket.close()
            if player_id and player_id in self.game_state.players:
                del self.game_state.players[player_id]
                print(f"Player {player_id} disconnected")

if __name__ == "__main__":
    server = GameServer()
    server.start()