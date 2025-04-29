# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 13:54:36 2025

@author: Dr. Boaz Ron Zohar
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 2025
Two-Galaxy Gravitational Simulation with UI Controls, Mass-Based Colors and Draggable Centers
"""

import pygame
import math
import sys

# -------------------- Default constants --------------------
dt = 0.5                      # time step
epsilon = 50                  # softening distance
G = 1                         # gravitational constant base
G_factor = 1                  # scaling factor
G_default = G * G_factor      # default G
mass_center_default = 10000   # central mass default
speed_multiplier_default = 1.0# default speed multiplier
sun_mass = 1                  # base solar mass
layer_factor = 3              # layers density scaling
num_per_layer = 20            # number of bodies per layer
center_radius = 8             # display radius for galaxy center for dragging detection

# ------------------ Pygame initialization ------------------
pygame.init()
WIDTH, HEIGHT = 1500, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# ------------------ Input screen ------------------
def show_start_screen():
    pygame.key.start_text_input()
    input_fields = [
        {"name": "G",                  "rect": pygame.Rect(500, 300, 200, 40), "text": str(G_default)},
        {"name": "Center Mass",        "rect": pygame.Rect(500, 360, 200, 40), "text": str(mass_center_default)},
        {"name": "Speed Mult",         "rect": pygame.Rect(500, 420, 200, 40), "text": str(speed_multiplier_default)},
        {"name": "dt",                 "rect": pygame.Rect(500, 480, 200, 40), "text": str(dt)},
        {"name": "Epsilon",            "rect": pygame.Rect(500, 540, 200, 40), "text": str(epsilon)},
        {"name": "Layer Factor",       "rect": pygame.Rect(500, 600, 200, 40), "text": str(layer_factor)},
        {"name": "Bodies per Layer",   "rect": pygame.Rect(500, 660, 200, 40), "text": str(num_per_layer)},
        {"name": "Intergalactic Dist", "rect": pygame.Rect(500, 720, 200, 40), "text": "200"}
    ]
    active_field = None
    start_button = pygame.Rect(650, 780, 120, 50)
    while True:
        screen.fill((0, 0, 0))
        title = font.render("Simulation Settings", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 250))
        for idx, field in enumerate(input_fields):
            box_color = (100, 100, 100) if idx == active_field else (50, 50, 50)
            label = font.render(f"{field['name']}:", True, (255, 255, 255))
            screen.blit(label, (field["rect"].x - 140, field["rect"].y + 10))
            pygame.draw.rect(screen, box_color, field["rect"])
            pygame.draw.rect(screen, (255, 255, 255), field["rect"], 2)
            txt_surf = font.render(field["text"], True, (255, 255, 255))
            screen.blit(txt_surf, (field["rect"].x + 5, field["rect"].y + 10))
        pygame.draw.rect(screen, (0, 128, 0), start_button)
        pygame.draw.rect(screen, (255, 255, 255), start_button, 2)
        start_txt = font.render("Start", True, (255, 255, 255))
        screen.blit(start_txt, (start_button.x + 30, start_button.y + 15))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos; active_field = None
                for i, field in enumerate(input_fields):
                    if field["rect"].collidepoint(pos): active_field = i; break
                if start_button.collidepoint(pos):
                    try: G_val = float(input_fields[0]["text"])
                    except: G_val = G_default
                    try: mass_val = float(input_fields[1]["text"])
                    except: mass_val = mass_center_default
                    try: speed_val = float(input_fields[2]["text"])
                    except: speed_val = speed_multiplier_default
                    try: dt_val = float(input_fields[3]["text"])
                    except: dt_val = dt
                    try: epsilon_val = float(input_fields[4]["text"])
                    except: epsilon_val = epsilon
                    try: layer_val = float(input_fields[5]["text"])
                    except: layer_val = layer_factor
                    try: num_val = int(input_fields[6]["text"])
                    except: num_val = num_per_layer
                    try: dist_val = float(input_fields[7]["text"])
                    except: dist_val = 200.0
                    return G_val, mass_val, speed_val, dt_val, epsilon_val, layer_val, num_val, dist_val
            elif event.type == pygame.KEYDOWN and active_field is not None:
                field = input_fields[active_field]
                if event.key == pygame.K_BACKSPACE: field["text"] = field["text"][:-1]
                elif event.key == pygame.K_RETURN: active_field = (active_field + 1) % len(input_fields)
                else:
                    if event.unicode.isdigit() or event.unicode == ".": field["text"] += event.unicode

# Load parameters
G, mass_center, speed_multiplier, dt, epsilon, layer_factor, num_per_layer, inter_dist = show_start_screen()
# Define galaxy centers
center1_x = WIDTH//2 - int(inter_dist/2); center1_y = HEIGHT//2
center2_x = WIDTH//2 + int(inter_dist/2); center2_y = HEIGHT//2
# Flags for dragging
dragging1 = dragging2 = False
offset_x = offset_y = 0

# Color table and mapping
colors = [(255,0,0),(255,50,0),(255,101,0),(255,152,0),(255,203,0),(255,254,0),
          (204,255,0),(153,255,0),(102,255,0),(51,255,0),(0,255,0),(0,255,50),
          (0,255,101),(0,255,152),(0,255,203),(0,255,254),(0,204,255),(0,153,255),
          (0,102,255),(0,51,255),(0,0,255),(50,0,255),(101,0,255),(152,0,255),
          (203,0,255),(254,0,255)]
Masses = [(i+1)*sun_mass for i in range(len(colors))]
color_to_mass = {c: m for c, m in zip(colors, Masses)}
# Layers
layers = [{"num": num_per_layer, "radius": r*layer_factor, "speed": s*G_factor} for r,s in
          [(10,10.0),(20,8.2),(30,7.1),(40,6.3),(50,5.8),(60,5.2),(70,4.6),(80,4.0),(90,3.5),(100,3.0)]]
for layer in layers: layer['speed']*=speed_multiplier
# UI elements
pause_rect = pygame.Rect(20,50,120,40); restart_rect=pygame.Rect(20,100,120,40)
compress_rect=pygame.Rect(20,150,180,40); spread_rect=pygame.Rect(20,200,180,40)
settings_rect=pygame.Rect(WIDTH-140,HEIGHT-60,120,40)
add_btns=[pygame.Rect(20,250+i*35,30,30) for i in range(len(layers))]
rem_btns=[pygame.Rect(60,250+i*35,30,30) for i in range(len(layers))]

def draw_button(rect,text,color):
    pygame.draw.rect(screen,color,rect); pygame.draw.rect(screen,(255,255,255),rect,2)
    screen.blit(font.render(text,True,(255,255,255)),(rect.x+10,rect.y+10))
def draw_layer_btns():
    for i in range(len(layers)):
        pygame.draw.rect(screen,(0,255,0),add_btns[i]); pygame.draw.rect(screen,(255,0,0),rem_btns[i])
        screen.blit(font.render("+",True,(0,0,0)),(add_btns[i].x+8,add_btns[i].y+5))
        screen.blit(font.render("-",True,(0,0,0)),(rem_btns[i].x+9,rem_btns[i].y+5))
# Containers
pos1,vel1,m1s=[],[],[]; pos2,vel2,m2s=[],[],[]; cidx=0
# Create bodies
def create_gal(center_x,center_y,pos,vel,mass,num,radius,speed):
    global cidx
    for i in range(num):
        ang=2*math.pi/num*i+math.pi/num
        x=center_x+radius*math.cos(ang); y=center_y+radius*math.sin(ang)
        vx=-speed*math.sin(ang); vy=speed*math.cos(ang)
        col=colors[cidx%len(colors)]; m=color_to_mass[col]
        pos.append((x,y)); vel.append((vx,vy)); mass.append(m); cidx+=1
# Init galaxies
def init_gals():
    global pos1,vel1,m1s,pos2,vel2,m2s,cidx,n1,n2
    pos1,vel1,m1s,pos2,vel2,m2s=[],[],[],[],[],[]; cidx=0
    for lay in layers: create_gal(center1_x,center1_y,pos1,vel1,m1s,lay['num'],lay['radius'],lay['speed'])
    pos1.append((center1_x,center1_y)); vel1.append((0,0)); m1s.append(mass_center)
    for lay in layers: create_gal(center2_x,center2_y,pos2,vel2,m2s,lay['num'],lay['radius'],lay['speed'])
    pos2.append((center2_x,center2_y)); vel2.append((0,0)); m2s.append(mass_center)
    n1,n2=len(pos1),len(pos2)
init_gals()
# Gravity
def grav(x1, y1, x2, y2, m1, m2):
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy)
    if dist == 0:
        return 0, 0
    force = G * m1 * m2 / (dist + epsilon) ** 2
    return force * dx / dist, force * dy / dist

# Main loop
run = True
paused = False
while run:
    screen.fill((0, 0, 0))
    # Event handling
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            run = False
        elif evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_p:
                paused = not paused
            elif evt.key == pygame.K_r and paused:
                paused = False
        elif evt.type == pygame.MOUSEBUTTONDOWN:
            mx, my = evt.pos
            # check center grabs
            if math.hypot(mx-center1_x, my-center1_y) < center_radius:
                dragging1 = True
                offset_x = center1_x - mx
                offset_y = center1_y - my
            elif math.hypot(mx-center2_x, my-center2_y) < center_radius:
                dragging2 = True
                offset_x = center2_x - mx
                offset_y = center2_y - my
            else:
                # UI clicks
                if pause_rect.collidepoint((mx, my)):
                    paused = not paused
                elif restart_rect.collidepoint((mx, my)):
                    init_gals()
                    paused = False
                elif compress_rect.collidepoint((mx, my)):
                    for l in layers:
                        l['radius'] *= 0.9
                    init_gals()
                elif spread_rect.collidepoint((mx, my)):
                    for l in layers:
                        l['radius'] *= 1.1
                    init_gals()
                elif settings_rect.collidepoint((mx, my)):
                    G, mass_center, speed_multiplier, dt, epsilon, layer_factor, num_per_layer, inter_dist = show_start_screen()
                    center1_x = WIDTH//2 - int(inter_dist/2)
                    center2_x = WIDTH//2 + int(inter_dist/2)
                    layers[:] = [{"num": num_per_layer, "radius": r*layer_factor, "speed": s*G_factor}
                                  for r, s in [(10,10.0),(20,8.2),(30,7.1),(40,6.3),(50,5.8),(60,5.2),(70,4.6),(80,4.0),(90,3.5),(100,3.0)]]
                    for l in layers:
                        l['speed'] *= speed_multiplier
                    init_gals()
                    paused = False
                else:
                    for i in range(len(layers)):
                        if add_btns[i].collidepoint((mx, my)):
                            layers[i]['num'] += 1
                            init_gals()
                            break
                        if rem_btns[i].collidepoint((mx, my)) and layers[i]['num'] > 0:
                            layers[i]['num'] -= 1
                            init_gals()
                            break
        elif evt.type == pygame.MOUSEBUTTONUP:
            dragging1 = dragging2 = False
        elif evt.type == pygame.MOUSEMOTION:
            if 'dragging1' in locals() and dragging1:
                center1_x = evt.pos[0] + offset_x
                center1_y = evt.pos[1] + offset_y
            if 'dragging2' in locals() and dragging2:
                center2_x = evt.pos[0] + offset_x
                center2_y = evt.pos[1] + offset_y

    # Physics update
    if not paused:
        # Galaxy 1
        new_pos1 = []
        for i in range(len(pos1)):
            fx = fy = 0
            for j in range(len(pos1)):
                if i != j:
                    dfx, dfy = grav(pos1[i][0], pos1[i][1], pos1[j][0], pos1[j][1], m1s[i], m1s[j])
                    fx += dfx
                    fy += dfy
            for j in range(len(pos2)):
                dfx, dfy = grav(pos1[i][0], pos1[i][1], pos2[j][0], pos2[j][1], m1s[i], m2s[j])
                fx += dfx
                fy += dfy
            vx, vy = vel1[i]
            vx += fx / m1s[i] * dt
            vy += fy / m1s[i] * dt
            x, y = pos1[i]
            x += vx * dt
            y += vy * dt
            vel1[i] = (vx, vy)
            new_pos1.append((x, y))
        pos1 = new_pos1
        # Galaxy 2
        new_pos2 = []
        for i in range(len(pos2)):
            fx = fy = 0
            for j in range(len(pos2)):
                if i != j:
                    dfx, dfy = grav(pos2[i][0], pos2[i][1], pos2[j][0], pos2[j][1], m2s[i], m2s[j])
                    fx += dfx
                    fy += dfy
            for j in range(len(pos1)):
                dfx, dfy = grav(pos2[i][0], pos2[i][1], pos1[j][0], pos1[j][1], m2s[i], m1s[j])
                fx += dfx
                fy += dfy
            vx, vy = vel2[i]
            vx += fx / m2s[i] * dt
            vy += fy / m2s[i] * dt
            x, y = pos2[i]
            x += vx * dt
            y += vy * dt
            vel2[i] = (vx, vy)
            new_pos2.append((x, y))
        pos2 = new_pos2

    # Drawing bodies
    for p, m in zip(pos1, m1s):
        idx = int(m / sun_mass) - 1
        idx = max(0, min(idx, len(colors)-1))
        c = colors[idx]
        pygame.draw.circle(screen, c, (int(p[0]), int(p[1])), 5)
    for p, m in zip(pos2, m2s):
        idx = int(m / sun_mass) - 1
        idx = max(0, min(idx, len(colors)-1))
        c = colors[idx]
        pygame.draw.circle(screen, c, (int(p[0]), int(p[1])), 5)

        # Draw galaxy centers (draggable)
    pygame.draw.circle(screen, (255, 255, 255), (int(center1_x), int(center1_y)), center_radius)
    pygame.draw.circle(screen, (255, 255,   0), (int(center2_x), int(center2_y)), center_radius)

    # UI draw
    draw_button(pause_rect, "Pause", (255, 0, 0))
    draw_button(restart_rect, "Restart", (0, 255, 0))
    draw_button(compress_rect, "Compress", (0, 0, 255))
    draw_button(spread_rect, "Spread", (255, 255, 0))
    draw_layer_btns()
    draw_button(settings_rect, "Settings", (254, 0, 255))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
