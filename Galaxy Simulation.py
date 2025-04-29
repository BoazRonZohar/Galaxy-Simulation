# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 00:50:02 2025

@author: Dr. Boaz Ron Zohar
"""

import pygame
import math
import sys

# Default constants
dt = 0.5
Epsilon = 50              # minimum distance modifier
G = 1                     # gravitational constant base
G_Factor = 1              # scaling factor
G_default = G * G_Factor  # gravitational constant default
mass_center_default = 10000   # central mass default
speed_multiplier_default = 1.0  # default speed multiplier
Sun_Mass = 1              # base solar mass
Layer_Factor = 3          # Layers density scaling
NUM = 20                  # Number of bodies per layer

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1500, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
center_x, center_y = WIDTH // 2, HEIGHT // 2

# Create input boxes for all constants (global list)
input_fields = [
    {"name": "G",                "rect": pygame.Rect(500, 300, 200, 40), "text": str(G_default)},
    {"name": "Center Mass",      "rect": pygame.Rect(500, 360, 200, 40), "text": str(mass_center_default)},
    {"name": "Speed Mult",       "rect": pygame.Rect(500, 420, 200, 40), "text": str(speed_multiplier_default)},
    {"name": "dt",               "rect": pygame.Rect(500, 480, 200, 40), "text": str(dt)},
    {"name": "Epsilon",          "rect": pygame.Rect(500, 540, 200, 40), "text": str(Epsilon)},
    {"name": "Layer Factor",     "rect": pygame.Rect(500, 600, 200, 40), "text": str(Layer_Factor)},
    {"name": "Bodies per Layer", "rect": pygame.Rect(500, 660, 200, 40), "text": str(NUM)}
]

def show_start_screen():
    # Use the global input_fields list so all 7 fields are available
    global input_fields
    active_field = None
    start_button = pygame.Rect(WIDTH//2 - 60, 740, 120, 50)
    pygame.key.start_text_input()

    while True:
        screen.fill((0, 0, 0))
        # Title
        title = font.render("Simulation Settings", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 250))

        # Draw each input field
        for idx, field in enumerate(input_fields):
            box_color = (100, 100, 100) if idx == active_field else (50, 50, 50)
            label = font.render(f"{field['name']}:", True, (255, 255, 255))
            screen.blit(label, (field["rect"].x - 140, field["rect"].y + 10))
            pygame.draw.rect(screen, box_color, field["rect"])
            pygame.draw.rect(screen, (255, 255, 255), field["rect"], 2)
            txt_surf = font.render(field["text"], True, (255, 255, 255))
            screen.blit(txt_surf, (field["rect"].x + 5, field["rect"].y + 10))

        # Draw Start button
        pygame.draw.rect(screen, (0, 128, 0), start_button)
        pygame.draw.rect(screen, (255, 255, 255), start_button, 2)
        start_txt = font.render("Start", True, (255, 255, 255))
        screen.blit(start_txt, (start_button.x + 30, start_button.y + 15))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                # Activate clicked field
                active_field = None
                for i, field in enumerate(input_fields):
                    if field["rect"].collidepoint(pos):
                        active_field = i
                        break
                # Start button clicked?
                if start_button.collidepoint(pos):
                    # Parse all seven fields with fallbacks
                    try: G_val = float(input_fields[0]["text"])
                    except: G_val = G_default
                    try: mass_val = float(input_fields[1]["text"])
                    except: mass_val = mass_center_default
                    try: speed_val = float(input_fields[2]["text"])
                    except: speed_val = speed_multiplier_default
                    try: dt_val = float(input_fields[3]["text"])
                    except: dt_val = dt
                    try: epsilon_val = float(input_fields[4]["text"])
                    except: epsilon_val = Epsilon
                    try: layer_factor_val = float(input_fields[5]["text"])
                    except: layer_factor_val = Layer_Factor
                    try: num_val = int(input_fields[6]["text"])
                    except: num_val = NUM

                    return G_val, mass_val, speed_val, dt_val, epsilon_val, layer_factor_val, num_val

            elif event.type == pygame.KEYDOWN and active_field is not None:
                field = input_fields[active_field]
                if event.key == pygame.K_BACKSPACE:
                    field["text"] = field["text"][:-1]
                elif event.key == pygame.K_RETURN:
                    active_field = (active_field + 1) % len(input_fields)
                else:
                    # Accept only digits and dot
                    if event.unicode.isdigit() or event.unicode == ".":
                        field["text"] += event.unicode

# Load parameters via on-screen input
G, mass_center, speed_multiplier, dt, Epsilon, Layer_Factor, NUM = show_start_screen()

# Initialize simulation state
paused = False

# ┌───────────────────────────────────────────────────────────────────────────┐
# │                            Color Index Table                            │
# └───────────────────────────────────────────────────────────────────────────┘
#
# Body Colors (Mass_1 … Mass_26):
# | Index | RGB Tuple      | Color Name     |
# |-------|----------------|----------------|
# | 1     | (255,   0,   0) | Red            |
# | 2     | (255,  50,   0) | Reddish Orange |
# | 3     | (255, 101,   0) | Orange         |
# | 4     | (255, 152,   0) | Dark Orange    |
# | 5     | (255, 203,   0) | Golden         |
# | 6     | (255, 254,   0) | Yellow         |
# | 7     | (204, 255,   0) | Yellow-Green   |
# | 8     | (153, 255,   0) | Light Green    |
# | 9     | (102, 255,   0) | Lime Green     |
# | 10    | ( 51, 255,   0) | Spring Green   |
# | 11    | (  0, 255,   0) | Green          |
# | 12    | (  0, 255,  50) | Aqua-Green     |
# | 13    | (  0, 255, 101) | Light Cyan     |
# | 14    | (  0, 255, 152) | Dark Cyan      |
# | 15    | (  0, 255, 203) | Turquoise      |
# | 16    | (  0, 255, 254) | Light Turquoise|
# | 17    | (  0, 204, 255) | Cyan-Blue      |
# | 18    | (  0, 153, 255) | Sky Blue       |
# | 19    | (  0, 102, 255) | Light Blue     |
# | 20    | (  0,  51, 255) | Medium Blue    |
# | 21    | (  0,   0, 255) | Blue           |
# | 22    | ( 50,   0, 255) | Blue-Violet    |
# | 23    | (101,   0, 255) | Purple         |
# | 24    | (152,   0, 255) | Light Purple   |
# | 25    | (203,   0, 255) | Magenta-Purple |
# | 26    | (254,   0, 255) | Magenta        |
#
# UI-Element Colors:
# | Element           | RGB Tuple      | Color Name       |
# |-------------------|----------------|------------------|
# | Background        | (  0,   0,   0) | Black            |
# | Text              | (255, 255, 255) | White            |
# | Pause button      | (255,   0,   0) | Red              |
# | Restart button    | (  0, 255,   0) | Green            |
# | Compress Layers   | (  0,   0, 255) | Blue             |
# | Spread Layers     | (255, 255,   0) | Yellow           |
# | Settings button   | (128, 128,   0) | Dark Khaki       |

# Precompute colors and mass mapping
colors = [
    (255,   0,   0), (255,  50,   0), (255, 101,   0), (255, 152,   0),
    (255, 203,   0), (255, 254,   0), (204, 255,   0), (153, 255,   0),
    (102, 255,   0), ( 51, 255,   0), (  0, 255,   0), (  0, 255,  50),
    (  0, 255, 101), (  0, 255, 152), (  0, 255, 203), (  0, 255, 254),
    (  0, 204, 255), (  0, 153, 255), (  0, 102, 255), (  0,  51, 255),
    (  0,   0, 255), ( 50,   0, 255), (101,   0, 255), (152,   0, 255),
    (203,   0, 255), (254,   0, 255),
]

Mass_1  =  1 * Sun_Mass
Mass_2  =  2 * Sun_Mass
Mass_3  =  3 * Sun_Mass
Mass_4  =  4 * Sun_Mass
Mass_5  =  5 * Sun_Mass
Mass_6  =  6 * Sun_Mass
Mass_7  =  7 * Sun_Mass
Mass_8  =  8 * Sun_Mass
Mass_9  =  9 * Sun_Mass
Mass_10 = 10 * Sun_Mass
Mass_11 = 11 * Sun_Mass
Mass_12 = 12 * Sun_Mass
Mass_13 = 13 * Sun_Mass
Mass_14 = 14 * Sun_Mass
Mass_15 = 15 * Sun_Mass
Mass_16 = 16 * Sun_Mass
Mass_17 = 17 * Sun_Mass
Mass_18 = 18 * Sun_Mass
Mass_19 = 19 * Sun_Mass
Mass_20 = 20 * Sun_Mass
Mass_21 = 21 * Sun_Mass
Mass_22 = 22 * Sun_Mass
Mass_23 = 23 * Sun_Mass
Mass_24 = 24 * Sun_Mass
Mass_25 = 25 * Sun_Mass
Mass_26 = 26 * Sun_Mass

color_to_mass = {c: globals()[f"Mass_{i+1}"] for i, c in enumerate(colors)}

# Define.layers and apply user multiplier
layers = [
    {"num": NUM, "radius": 10*Layer_Factor, "speed": 10.0*G_Factor},
    {"num": NUM, "radius": 20*Layer_Factor, "speed":  8.2*G_Factor},
    {"num": NUM, "radius": 30*Layer_Factor, "speed":  7.1*G_Factor},
    {"num": NUM, "radius": 40*Layer_Factor, "speed":  6.3*G_Factor},
    {"num": NUM, "radius": 50*Layer_Factor, "speed":  5.8*G_Factor},
    {"num": NUM, "radius": 60*Layer_Factor, "speed":  5.2*G_Factor},
    {"num": NUM, "radius": 70*Layer_Factor, "speed":  4.6*G_Factor},
    {"num": NUM, "radius": 80*Layer_Factor, "speed":  4.0*G_Factor},
    {"num": NUM, "radius": 90*Layer_Factor, "speed":  3.5*G_Factor},
    {"num": NUM, "radius":100*Layer_Factor, "speed":  3.0*G_Factor},
]
for layer in layers:
    layer["speed"] *= speed_multiplier

# Prepare bodies
positions, velocities, masses = [], [], []
color_index = 0

def create_bodies(num, radius, speed):
    global color_index
    for i in range(num):
        angle = (2 * math.pi / num) * i + math.pi / num
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        vx = -speed * math.sin(angle)
        vy =  speed * math.cos(angle)
        positions.append((x, y))
        velocities.append((vx, vy))
        color = colors[color_index % len(colors)]
        masses.append(color_to_mass[color])
        color_index += 1

# Initialize system
for layer in layers:
    create_bodies(layer["num"], layer["radius"], layer["speed"])  
# add central mass
positions.append((center_x, center_y))
velocities.append((0, 0))
masses.append(mass_center)

num_bodies = len(positions)

# UI button rectangles
pause_button_rect    = pygame.Rect(20,  50, 120, 40)
restart_button_rect  = pygame.Rect(20, 100, 120, 40)
compress_button_rect = pygame.Rect(20, 150, 180, 40)
spread_button_rect   = pygame.Rect(20, 200, 180, 40)
settings_button_rect = pygame.Rect(WIDTH-100, HEIGHT - 1000, 120, 40)
  
add_buttons    = []
remove_buttons = []
for i in range(len(layers)):
    y = 250 + i * 35
    add_buttons.append(pygame.Rect(20, y, 30, 30))
    remove_buttons.append(pygame.Rect(60, y, 30, 30))

def draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)
    screen.blit(font.render(text, True, (255, 255, 255)), (rect.x+10, rect.y+10))

def draw_layer_buttons():
    for i in range(len(layers)):
        pygame.draw.rect(screen, (0, 255, 0), add_buttons[i])
        pygame.draw.rect(screen, (255, 0,   0), remove_buttons[i])
        screen.blit(font.render("+", True, (0,0,0)), (add_buttons[i].x + 8, add_buttons[i].y + 5))
        screen.blit(font.render("-", True, (0,0,0)), (remove_buttons[i].x + 9, remove_buttons[i].y + 5))

def gravitational_force(x1, y1, x2, y2, m1, m2):
    dx = x2 - x1
    dy = y2 - y1
    r = math.hypot(dx, dy)
    if r == 0:
        return 0, 0
    f = G * m1 * m2 / ((r + Epsilon)**2)
    return f * dx / r, f * dy / r

def angular_momentum(x, y, vx, vy, m, cx, cy):
    rx, ry = x - cx, y - cy
    return m * (rx * vy - ry * vx)

def kinetic_energy(m, vx, vy):
    return 0.5 * m * (vx**2 + vy**2)

def potential_energy(x1, y1, x2, y2, m1, m2):
    r = math.hypot(x2 - x1, y2 - y1)
    if r == 0:
        return 0
    return -G * m1 * m2 / (r + Epsilon)

# Main simulation loop
running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_r and paused:
                paused = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if pause_button_rect.collidepoint(mouse_pos):
                paused = not paused

            elif restart_button_rect.collidepoint(mouse_pos):
                positions.clear(); velocities.clear(); masses.clear(); color_index = 0
                for layer in layers:
                    create_bodies(layer["num"], layer["radius"], layer["speed"])
                positions.append((center_x, center_y)); velocities.append((0,0)); masses.append(mass_center)
                paused = False

            elif compress_button_rect.collidepoint(mouse_pos):
                for layer in layers:
                    layer["radius"] *= 0.9
                positions.clear(); velocities.clear(); masses.clear(); color_index = 0
                for layer in layers:
                    create_bodies(layer["num"], layer["radius"], layer["speed"])
                positions.append((center_x, center_y)); velocities.append((0,0)); masses.append(mass_center)
                #paused = False

            elif spread_button_rect.collidepoint(mouse_pos):
                for layer in layers:
                    layer["radius"] *= 1.1
                positions.clear(); velocities.clear(); masses.clear(); color_index = 0
                for layer in layers:
                    create_bodies(layer["num"], layer["radius"], layer["speed"])
                positions.append((center_x, center_y)); velocities.append((0,0)); masses.append(mass_center)
                #paused = False

            elif settings_button_rect.collidepoint(mouse_pos):
                # call the settings screen again
                G, mass_center, speed_multiplier, dt, Epsilon, Layer_Factor, NUM = show_start_screen()

                # update layers with new parameters
                layers = [
                    {"num": NUM, "radius": 10*Layer_Factor, "speed": 10.0*G_Factor},
                    {"num": NUM, "radius": 20*Layer_Factor, "speed":  8.2*G_Factor},
                    {"num": NUM, "radius": 30*Layer_Factor, "speed":  7.1*G_Factor},
                    {"num": NUM, "radius": 40*Layer_Factor, "speed":  6.3*G_Factor},
                    {"num": NUM, "radius": 50*Layer_Factor, "speed":  5.8*G_Factor},
                    {"num": NUM, "radius": 60*Layer_Factor, "speed":  5.2*G_Factor},
                    {"num": NUM, "radius": 70*Layer_Factor, "speed":  4.6*G_Factor},
                    {"num": NUM, "radius": 80*Layer_Factor, "speed":  4.0*G_Factor},
                    {"num": NUM, "radius": 90*Layer_Factor, "speed":  3.5*G_Factor},
                    {"num": NUM, "radius":100*Layer_Factor, "speed":  3.0*G_Factor},
                ]
                for layer in layers:
                    layer["speed"] *= speed_multiplier

                positions.clear(); velocities.clear(); masses.clear(); color_index = 0
                for layer in layers:
                    create_bodies(layer["num"], layer["radius"], layer["speed"])
                positions.append((center_x, center_y)); velocities.append((0,0)); masses.append(mass_center)
                num_bodies = len(positions)
                paused = False

            else:
                # layer + / - buttons
                for i in range(len(layers)):
                    if add_buttons[i].collidepoint(mouse_pos):
                        layers[i]["num"] += 1
                    elif remove_buttons[i].collidepoint(mouse_pos) and layers[i]["num"] > 0:
                        layers[i]["num"] -= 1
                    else:
                        continue
                    positions.clear(); velocities.clear(); masses.clear(); color_index = 0
                    for layer in layers:
                        create_bodies(layer["num"], layer["radius"], layer["speed"])
                    positions.append((center_x, center_y)); velocities.append((0,0)); masses.append(mass_center)
                    num_bodies = len(positions)
                    break

    # Physics update
    if not paused:
        forces = [(0,0)] * num_bodies
        for i in range(num_bodies):
            fx_total, fy_total = 0, 0
            for j in range(num_bodies):
                if i != j:
                    fx, fy = gravitational_force(
                        positions[i][0], positions[i][1],
                        positions[j][0], positions[j][1],
                        masses[i], masses[j]
                    )
                    fx_total += fx
                    fy_total += fy
            forces[i] = (fx_total, fy_total)

        for i in range(num_bodies):
            vx, vy = velocities[i]
            fx, fy = forces[i]
            velocities[i] = (vx + fx / masses[i] * dt, vy + fy / masses[i] * dt)

        for i in range(num_bodies):
            x, y = positions[i]
            vx, vy = velocities[i]
            positions[i] = (x + vx * dt, y + vy * dt)

    # Draw bodies
    for i in range(num_bodies):
        pygame.draw.circle(
            screen,
            colors[i % len(colors)],
            (int(positions[i][0]), int(positions[i][1])),
            5
        )

    # Draw UI
    draw_button(pause_button_rect,    "Pause",           (255,   0,   0))
    draw_button(restart_button_rect,  "Restart",         (  0, 255,   0))
    draw_button(compress_button_rect, "Compress Layers", (  0,   0, 255))
    draw_button(spread_button_rect,   "Spread Layers",   (255, 101,   0))
    draw_layer_buttons()
    draw_button(settings_button_rect, "Settings", (254, 0, 255))

    # Stats display
    L = sum(
        angular_momentum(
            positions[i][0], positions[i][1],
            velocities[i][0], velocities[i][1],
            masses[i], center_x, center_y
        )
        for i in range(num_bodies)
    )
    KE = sum(kinetic_energy(masses[i], velocities[i][0], velocities[i][1])
             for i in range(num_bodies))
    PE = sum(
        potential_energy(
            positions[i][0], positions[i][1],
            positions[j][0], positions[j][1],
            masses[i], masses[j]
        )
        for i in range(num_bodies) for j in range(i+1, num_bodies)
    )
    stats_text = font.render(
        f"Angular momentum: {L:.0f} | Total energy: {KE+PE:.0f} | "
        f"Kinetic: {KE:.0f} | Potential: {PE:.0f}",
        True, (255, 255, 255)
    )
    screen.blit(stats_text, (10, 10))
    sat_count = num_bodies - 1
    count_text = font.render(f"Satellites: {sat_count}", True, (255, 255, 255))
    screen.blit(count_text, (10, 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
