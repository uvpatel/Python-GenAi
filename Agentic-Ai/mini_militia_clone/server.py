import socket
import threading
import json
import time
import math

class GameServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(8) # Support up to 8 players
        self.players = {}  
        self.bullets = []  
        self.lock = threading.Lock()
        self.max_players = 8
        print(f"Server running on {host}:{port} (Max {self.max_players} players)")

    def update_physics(self):
        while True:
            with self.lock:
                # Bullet physics
                new_bullets = []
                for b in self.bullets:
                    b['x'] += b['vx']
                    b['y'] += b['vy']
                    
                    hit = False
                    # Collision Detection: Bullet vs Players
                    for p_id, p_state in self.players.items():
                        if b['owner'] != p_id: # No friendly fire/self-hit
                            dist = math.sqrt((b['x'] - p_state['x'])**2 + (b['y'] - p_state['y'])**2)
                            if dist < 25: # Radius threshold
                                p_state['health'] -= 10
                                hit = True
                                break
                    
                    if not hit and 0 <= b['x'] <= 800 and 0 <= b['y'] <= 600:
                        new_bullets.append(b)
                self.bullets = new_bullets
            time.sleep(0.016)

    def handle_client(self, conn, p_id):
        conn.send(str.encode(p_id))
        while True:
            try:
                data = conn.recv(8192).decode('utf-8')
                if not data: break
                
                msg = json.loads(data)
                with self.lock:
                    if msg['type'] == 'update':
                        # Update existing player state but preserve server-side health
                        if p_id in self.players:
                            current_health = self.players[p_id].get('health', 100)
                            self.players[p_id] = msg['state']
                            self.players[p_id]['health'] = current_health
                        else:
                            self.players[p_id] = msg['state']
                            self.players[p_id]['health'] = 100

                        # Respawn logic
                        if self.players[p_id]['health'] <= 0:
                            self.players[p_id]['x'], self.players[p_id]['y'] = 400, 300
                            self.players[p_id]['health'] = 100

                    elif msg['type'] == 'shoot':
                        self.bullets.append(msg['bullet'])

                    reply = {'players': self.players, 'bullets': self.bullets}
                    conn.sendall(str.encode(json.dumps(reply)))
            except:
                break
        
        with self.lock:
            if p_id in self.players: del self.players[p_id]
        conn.close()
        print(f"Player {p_id} left.")

    def run(self):
        threading.Thread(target=self.update_physics, daemon=True).start()
        p_count = 0
        while True:
            conn, addr = self.server.accept()
            with self.lock:
                if len(self.players) >= self.max_players:
                    conn.close()
                    continue
            
            p_count += 1
            p_id = f"Soldier_{p_count}"
            print(f"Player {p_id} joined from {addr}")
            threading.Thread(target=self.handle_client, args=(conn, p_id), daemon=True).start()

if __name__ == '__main__':
    GameServer().run()