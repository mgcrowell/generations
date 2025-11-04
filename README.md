# The Generations Engine

*dunno yet exactly*

Hoping to be a framework built in Python for a server-driven multiplayer dungeon crawling RPG.

The idea is to have a game world server and the lightest weight clients possible. Clients should be able to be as simple as text-based interfaces built into BBS systems all the way up to modern implementations using whatever. The Generations Engine is designed to power this idea efficiently and effectively.

---

## The Vision

Imagine being able to play the same persistent world dungeon crawler through:
- **A retro BBS door game**
- **A slick modern web interface** 
- **A mobile app**
- **A terminal client**
- **Whatever else someone dreams up**

All connecting to the same game world, all seeing the same dungeons, all fighting the same monsters.

---

## How It Works

**Server-Driven Everything**: The server does the heavy lifting - game logic, world state, combat resolution. Clients are just fancy display and input devices.

**Protocol First**: Clean, simple messaging protocol that even a potato could implement. JSON over sockets? Probably. Something that doesn't require a PhD to understand.

**Your Client, Your Rules**: Build whatever interface you want. Fancy graphics? Go for it. Pure ASCII art? Beautiful. Telnet-compatible? Absolutely.

---

## Status

Currently in the "this seems like a good idea after a 30 pack of natty light and some fishing" phase. Code exists. A client rewrite is always happening. Progress is.

---

## Why "Generations"?

Because like Sonic Generations I want there to be a union of the new and the old.