import pygame
import socket
import json
import math
import sys

# --- Constants ---
WIDTH, HEIGHT = 800, 600
PLAYER_RADIUS = 20
GRAVITY = 0.5
THRUST = -0.8
MAX_FUEL = 100
BULLET_SPEED = 10

class Network:
    def __init__(self, host="127.0.0.1", port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (host, port)
        self.p_id = self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except Exception as e:
            print(f"Connection Error: {e}")
            return None

    def send_recv(self, data):
        try:
            self.client.sendall(str.encode(json.dumps(data)))
            return json.loads(self.client.recv(8192).decode())
        except:
            return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mini Militia Clone")
    clock = pygame.time.Clock()

    net = Network()
    if not net.p_id: return

    # Player State
    pos = [WIDTH // 2, HEIGHT // 2]
    vel = [0, 0]
    fuel = MAX_FUEL
    health = 100

    running = True
    while running:
        clock.tick(60)
        screen.fill((40, 40, 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Shooting logic
                mx, my = pygame.mouse.get_pos()
                angle = math.atan2(my - pos[1], mx - pos[0])
                bullet = {
                    'x': pos[0], 'y': pos[1],
                    'vx': math.cos(angle) * BULLET_SPEED,
                    'vy': math.sin(angle) * BULLET_SPEED,
                    'owner': net.p_id
                }
                net.send_recv({'type': 'shoot', 'bullet': bullet})

        # Physics & Input
        keys = pygame.key.get_pressed()
        # Horizontal movement
        if keys[pygame.K_a]: vel[0] = -5
        elif keys[pygame.K_d]: vel[0] = 5
        else: vel[0] *= 0.9 # Friction

        # Jetpack (Vertical)
        if keys[pygame.K_SPACE] and fuel > 0:
            vel[1] += THRUST
            fuel -= 1
        else:
            vel[1] += GRAVITY
            if fuel < MAX_FUEL: fuel += 0.2 # Refuel

        pos[0] += vel[0]
        pos[1] += vel[1]

        # Bounds
        pos[0] = max(PLAYER_RADIUS, min(WIDTH - PLAYER_RADIUS, pos[0]))
        pos[1] = max(PLAYER_RADIUS, min(HEIGHT - PLAYER_RADIUS, pos[1]))

        # Sync with Server
        state = {'type': 'update', 'state': {'x': pos[0], 'y': pos[1], 'health': health}}
        server_data = net.send_recv(state)

        if server_data:
            # Draw Bullets
            for b in server_data.get('bullets', []):
                pygame.draw.circle(screen, (255, 255, 0), (int(b['x']), int(b['y'])), 4)

            # Draw Players
            for p_id, p_state in server_data.get('players', {}).items():
                color = (0, 255, 0) if p_id == net.p_id else (255, 50, 50)
                pygame.draw.circle(screen, color, (int(p_state['x']), int(p_state['y'])), PLAYER_RADIUS)
                # Draw ID
                font = pygame.font.SysFont(None, 24)
                img = font.render(p_id, True, (255, 255, 255))
                screen.blit(img, (p_state['x'] - 10, p_state['y'] - 40))

        # UI
        pygame.draw.rect(screen, (200, 0, 0), (10, 10, fuel, 10)) # Fuel Bar
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()