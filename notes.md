Server:
I stopped at line 308 in the server, I need to make PROTOCOL DECODE function of some sort in order to decode the client side of the protocol. I figure maybe I could use some sort of state machine if I did that? 

Here's my thought
"EXPLORATION": {
                'MOVE': self._handle_move,
                'ATTACK': self._handle_attack_start,
                'LOOK': self._handle_look,
                'INVENTORY': self._handle_inventory,
                'QUIT': self._handle_quit,
                'REQUEST_POSITIONS': self._handle_positions
            },
            "BATTLE": {
                'ATTACK': self._handle_attack_battle,
                'DEFEND': self._handle_defend,
                'FLEE': self._handle_flee,
                'USE_ITEM': self._handle_use_item,
                'QUIT': self._handle_quit
            },
            "MENU": {
                'INVENTORY': self._handle_inventory,
                'STATS': self._handle_stats,
                'RESUME': self._handle_resume
            }


Client:
I don't even think this works atm.
It will need a full rewrite with the new protocol