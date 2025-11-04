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

def create_local_map(player_x, player_y, positions):
    """Create a 10x10 grid centered around the player"""
    grid_size = 10
    half_size = grid_size // 2
    
    # Initialize empty grid
    grid = [['.' for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Mark player position at center
    center_x, center_y = half_size, half_size
    grid[center_y][center_x] = 'P'
    
    # Place other entities relative to player
    for entity in positions:
        if isinstance(entity, dict):
            rel_x = entity.get('x', 0) - player_x
            rel_y = entity.get('y', 0) - player_y
            
            # Convert to grid coordinates (flip y-axis for display)
            grid_x = center_x + rel_x
            grid_y = center_y - rel_y  # Flip y-axis so up is visually up
            
            # Only draw if within the 10x10 grid
            if 0 <= grid_x < grid_size and 0 <= grid_y < grid_size:
                entity_type = entity.get('type', '')
                entity_name = entity.get('name', '')
                
                if entity_type == 'player' and entity.get('id') != player_id:
                    grid[grid_y][grid_x] = 'P'  # Other players
                elif entity_type == 'enemy':
                    grid[grid_y][grid_x] = 'E'  # Enemies
    
    return grid

def display_grid(grid):
    """Display the grid in a readable format"""
    print("=== LOCAL MAP (10x10 around you) ===")
    print("    " + " ".join(str(i).rjust(2) for i in range(10)))
    print("   " + "+--" * 10 + "+")
    
    for y, row in enumerate(grid):
        print(f"{y:2} |", end="")
        for cell in row:
            print(f" {cell} ", end="")
        print("|")
    
    print("   " + "+--" * 10 + "+")
    print("Legend: P=You/Players, E=Enemies, .=Empty")
    print()

def display_player_info(player_data):
    """Display player information"""
    print("=== PLAYER INFO ===")
    if isinstance(player_data, dict):
        print(f"ID: {player_data.get('id', 'N/A')}")
        print(f"Name: {player_data.get('name', 'N/A')}")
        print(f"Position: ({player_data.get('x', 0)}, {player_data.get('y', 0)})")
        print(f"Health: {player_data.get('health', 0)}/{player_data.get('max_health', 0)}")
    else:
        print(player_data)
    print()

# Global variables to track game state
player_id = None
player_data = None
all_positions = []

def start_client(ip, port):
    global player_id, player_data, all_positions
    
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
            
            # Parse protocol messages
            messages = parse_protocol_message(data)
            waiting_for_input = False
            
            # Process messages and update game state
            for msg in messages:
                if msg['type'] == 'PLAYER_INFO':
                    player_data = msg['data']
                    if isinstance(player_data, dict):
                        player_id = player_data.get('id')
                elif msg['type'] == 'POSITIONS':
                    all_positions = msg['data']
                elif msg['type'] == 'PROMPT':
                    waiting_for_input = True
            
            # Display game state
            if player_data and isinstance(player_data, dict):
                # Create and display local map
                player_x = player_data.get('x', 0)
                player_y = player_data.get('y', 0)
                
                if all_positions:
                    grid = create_local_map(player_x, player_y, all_positions)
                    display_grid(grid)
                
                # Display player info
                display_player_info(player_data)
            
            # Display other messages
            for msg in messages:
                if msg['type'] not in ['PLAYER_INFO', 'POSITIONS']:
                    if msg['type'] == 'PROMPT':
                        print(msg['data'], end='')
                    elif msg['type'] == 'ERROR':
                        print(f"ERROR: {msg['data']}")
                    elif msg['type'] == 'SUCCESS':
                        print(f"{msg['data']}")
                    elif msg['type'] == 'RAW':
                        print(msg['data'], end='')
            
            # Provide input on server prompt
            if waiting_for_input:
                user_input = input().strip().lower()
                if user_input in ['w','a','s','d']:
                    command = movement_commands[user_input]
                    client_socket.send(f"{command}\n".encode())
                elif user_input == 'positions':
                    client_socket.send(f"POSITIONS\n".encode())
                elif user_input == 'quit':
                    client_socket.send(f"QUIT\n".encode())
                else:
                    client_socket.send(f"{user_input}\n".encode())
                    
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
        port = int(ip_full[1])
    start_client(ip, port)