import pygame
import sys
import math
import random 
import os 

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
game_surf = pygame.Surface((WIDTH, HEIGHT)) 
pygame.display.set_caption("Boss Fight - Dev Skip Fixed")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PLAYER_BLUE = (0, 50, 255) 

font_main = pygame.font.SysFont(None, 36)
font_graze = pygame.font.SysFont(None, 24)
font_big = pygame.font.SysFont(None, 72)
font_dmg = pygame.font.SysFont(None, 48, bold=True)
font_charge = pygame.font.SysFont(None, 24)

arena_rect = pygame.Rect(200, 300, 400, 200)
player_size = 16
player_speed = 4
boss_rect = pygame.Rect(WIDTH//2 - 20, 130, 40, 40)
boss_max_hp = 350 

def reset_game():
    global player_hp, player_x, player_y, bullets, invulnerable_timer
    global current_phase, boss_color, spawn_timer, god_mode
    global boss_hp, boss_flash_timer, game_state, spiral_angle
    global attack_bar_active, attack_cooldown, cursor_x, cursor_dir
    global slash_timer, damage_popup, graze_popups, player_turn_timer
    global screen_shake, player_color, y_velocity, x_velocity, is_jumping, gravity_dir, p4_attack_type
    global p5_special_timer, music_time_offset, fallback_timer
    
    player_hp = 5 
    player_x = WIDTH // 2 - player_size // 2
    player_y = 400 - player_size // 2
    bullets = []
    invulnerable_timer = 60 
    
    player_color = RED
    x_velocity = 0
    y_velocity = 0
    is_jumping = False
    gravity_dir = "DOWN" 
    p4_attack_type = "slam"
    
    boss_hp = boss_max_hp
    boss_flash_timer = 0
    current_phase = 1
    boss_color = (0, 100, 255) 
    spawn_timer = 0
    spiral_angle = 0.0 
    screen_shake = 0 
    
    attack_bar_active = True 
    attack_cooldown = 0
    cursor_x = 250
    cursor_dir = 8
    slash_timer = 0
    damage_popup = {"val": "", "y": 0, "timer": 0}
    graze_popups = [] 
    
    player_turn_timer = 180 
    p5_special_timer = 1100 
    
    music_time_offset = 0
    fallback_timer = 0 
    
    game_state = "PLAYING"
    god_mode = False 
    
    try:
        try:
            script_folder = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_folder = os.getcwd()
            
        song_path = os.path.join(script_folder, "song.ogg")
        pygame.mixer.music.load(song_path) 
        pygame.mixer.music.set_volume(0.3) 
        pygame.mixer.music.play(-1, 0.0)
    except Exception as e:
        print(f"Warning: Could not load audio. Make sure song.ogg is in: {script_folder}")

reset_game()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g: god_mode = not god_mode
            if event.key == pygame.K_h: player_hp = 5 
            if event.key == pygame.K_o: boss_hp = 1
            if event.key == pygame.K_c: attack_cooldown = 1 
            
            # --- FIXED PHASE SKIPPING ---
            if event.key == pygame.K_1:
                current_phase = 1; boss_color = (0, 100, 255); player_color = RED; bullets.clear()
                music_time_offset = 0; fallback_timer = 0
                try: pygame.mixer.music.play(-1, 0.0)
                except: pass
            if event.key == pygame.K_2:
                current_phase = 2; boss_color = (255, 0, 255); player_color = RED; bullets.clear()
                music_time_offset = 56000; fallback_timer = 0
                try: pygame.mixer.music.play(-1, 56.0)
                except: pass
            if event.key == pygame.K_3:
                current_phase = 3; boss_color = ORANGE; player_color = RED; bullets.clear()
                music_time_offset = 112000; fallback_timer = 0
                try: pygame.mixer.music.play(-1, 112.0)
                except: pass
            if event.key == pygame.K_4: 
                current_phase = 4; boss_color = CYAN; player_color = PLAYER_BLUE; bullets.clear()
                gravity_dir = "DOWN"
                music_time_offset = 158000; fallback_timer = 0
                try: pygame.mixer.music.play(-1, 158.0)
                except: pass
            if event.key == pygame.K_5: 
                current_phase = 5; boss_color = RED; player_color = RED; bullets.clear()
                p5_special_timer = 1100
                music_time_offset = 203000; fallback_timer = 0
                try: pygame.mixer.music.play(-1, 203.0)
                except: pass
                
            if event.key == pygame.K_SPACE and attack_bar_active and game_state == "PLAYING":
                distance_from_center = abs(400 - cursor_x)
                if distance_from_center < 15: 
                    damage = 35; screen_shake = 15 
                elif distance_from_center < 50: damage = 20  
                elif distance_from_center < 100: damage = 10 
                else: damage = 0                             
                
                if damage > 0:
                    boss_hp -= damage
                    boss_flash_timer = 4
                    slash_timer = 15 
                    damage_popup = {"val": str(damage), "y": boss_rect.y, "timer": 45}
                else:
                    damage_popup = {"val": "MISS", "y": boss_rect.y, "timer": 45}
                    
                attack_bar_active = False
                attack_cooldown = 1800 
                spawn_timer = 0 
                
                if boss_hp <= 0:
                    game_state = "VICTORY"
                    pygame.mixer.music.fadeout(2000) 
                    bullets.clear()

    keys = pygame.key.get_pressed()
    
    if current_phase == 4 and game_state == "PLAYING":
        grav_accel = 1.2
        jump_power = 12.0
        
        if gravity_dir == "DOWN": y_velocity += grav_accel
        elif gravity_dir == "UP": y_velocity -= grav_accel
        elif gravity_dir == "LEFT": x_velocity -= grav_accel
        elif gravity_dir == "RIGHT": x_velocity += grav_accel
            
        player_x += x_velocity
        player_y += y_velocity
        
        if gravity_dir in ["DOWN", "UP"]:
            if keys[pygame.K_LEFT] and player_x > arena_rect.left + 5: player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x < arena_rect.right - player_size - 5: player_x += player_speed
            x_velocity = 0 
        else:
            if keys[pygame.K_UP] and player_y > arena_rect.top + 5: player_y -= player_speed
            if keys[pygame.K_DOWN] and player_y < arena_rect.bottom - player_size - 5: player_y += player_speed
            y_velocity = 0 

        if player_y >= arena_rect.bottom - player_size - 5:
            player_y = arena_rect.bottom - player_size - 5
            if gravity_dir == "DOWN":
                y_velocity = 0; is_jumping = False
                if keys[pygame.K_UP]: y_velocity = -jump_power; is_jumping = True
                
        if player_y <= arena_rect.top + 5:
            player_y = arena_rect.top + 5
            if gravity_dir == "UP":
                y_velocity = 0; is_jumping = False
                if keys[pygame.K_DOWN]: y_velocity = jump_power; is_jumping = True
                
        if player_x <= arena_rect.left + 5:
            player_x = arena_rect.left + 5
            if gravity_dir == "LEFT":
                x_velocity = 0; is_jumping = False
                if keys[pygame.K_RIGHT]: x_velocity = jump_power; is_jumping = True
                
        if player_x >= arena_rect.right - player_size - 5:
            player_x = arena_rect.right - player_size - 5
            if gravity_dir == "RIGHT":
                x_velocity = 0; is_jumping = False
                if keys[pygame.K_LEFT]: x_velocity = -jump_power; is_jumping = True
                
    else:
        if keys[pygame.K_LEFT] and player_x > arena_rect.left + 5: player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < arena_rect.right - player_size - 5: player_x += player_speed
        if keys[pygame.K_UP] and player_y > arena_rect.top + 5: player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < arena_rect.bottom - player_size - 5: player_y += player_speed

    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    graze_rect = player_rect.inflate(16, 16) 
    player_center_x = player_x + (player_size // 2)
    player_center_y = player_y + (player_size // 2)

    if game_state == "PLAYING":
        
        # Calculate precise music time for phase syncing
        fallback_timer += (1000.0 / 60.0) 
        real_time = pygame.mixer.music.get_pos()
        if real_time >= 0:
            music_time = real_time + music_time_offset
        else:
            music_time = fallback_timer + music_time_offset
        
        if music_time >= 56000 and current_phase == 1:
            current_phase = 2; boss_color = (255, 0, 255); bullets.clear()
        if music_time >= 112000 and current_phase == 2:
            current_phase = 3; boss_color = ORANGE; bullets.clear()
        if music_time >= 158000 and current_phase == 3: 
            current_phase = 4; boss_color = CYAN; player_color = PLAYER_BLUE; bullets.clear()
            gravity_dir = "DOWN"
        if music_time >= 203000 and current_phase == 4: 
            current_phase = 5; boss_color = RED; player_color = RED; bullets.clear()

        if attack_bar_active:
            cursor_x += cursor_dir
            if cursor_x > 550 or cursor_x < 250: cursor_dir *= -1 
            player_turn_timer -= 1
            if player_turn_timer <= 0:
                damage_popup = {"val": "TIME UP!", "y": boss_rect.y, "timer": 45}
                attack_bar_active = False
                attack_cooldown = 1800 
                spawn_timer = 0 
        else:
            if attack_cooldown > 0:
                attack_cooldown -= 1
                if attack_cooldown == 0:
                    attack_bar_active = True
                    cursor_x = 250
                    player_turn_timer = 180 
                    bullets.clear() 

        if not attack_bar_active:
            spawn_timer += 1
            angle_to_player = math.atan2(player_center_y - boss_rect.centery, player_center_x - boss_rect.centerx)

            if current_phase == 1:
                if spawn_timer >= 30: 
                    speed_x = math.cos(angle_to_player) * 6
                    speed_y = math.sin(angle_to_player) * 6
                    bullet_rect = pygame.Rect(0, 0, 12, 12)
                    bullet_rect.center = boss_rect.center
                    bullets.append({"rect": bullet_rect, "exact_x": float(bullet_rect.x), "exact_y": float(bullet_rect.y), "sx": speed_x, "sy": speed_y, "grazed": False, "type": "proj"})
                    spawn_timer = 0
            elif current_phase == 2:
                if spawn_timer >= 25:
                    for angle_offset in [-0.3, 0, 0.3]:
                        spread_angle = angle_to_player + angle_offset
                        speed_x = math.cos(spread_angle) * 7 
                        speed_y = math.sin(spread_angle) * 7
                        bullet_rect = pygame.Rect(0, 0, 12, 12)
                        bullet_rect.center = boss_rect.center
                        bullets.append({"rect": bullet_rect, "exact_x": float(bullet_rect.x), "exact_y": float(bullet_rect.y), "sx": speed_x, "sy": speed_y, "grazed": False, "type": "proj"})
                    spawn_timer = 0
            elif current_phase == 3:
                if spawn_timer >= 7: 
                    current_speed = random.uniform(3.5, 6.5)
                    for angle_offset in [0, math.pi]: 
                        speed_x = math.cos(spiral_angle + angle_offset) * current_speed
                        speed_y = math.sin(spiral_angle + angle_offset) * current_speed
                        bullet_rect = pygame.Rect(0, 0, 12, 12)
                        bullet_rect.center = boss_rect.center
                        bullets.append({"rect": bullet_rect, "exact_x": float(bullet_rect.x), "exact_y": float(bullet_rect.y), "sx": speed_x, "sy": speed_y, "grazed": False, "type": "proj"})
                    spiral_angle += random.uniform(0.1, 0.25) 
                    spawn_timer = 0
            elif current_phase == 4:
                if spawn_timer == 1:
                    p4_attack_type = random.choice(["slam", "slide", "slide"])
                    if p4_attack_type == "slam":
                        possible_dirs = ["DOWN", "UP", "LEFT", "RIGHT"]
                        if gravity_dir in possible_dirs: possible_dirs.remove(gravity_dir)
                        gravity_dir = random.choice(possible_dirs)
                        x_velocity = 0; y_velocity = 0
                        screen_shake = 15 
                    elif p4_attack_type == "slide":
                        direction = random.choice([1, -1]) 
                        speed = 6.0 * direction
                        bone_h = random.randint(20, 50) 
                        if gravity_dir in ["DOWN", "UP"]:
                            rect = pygame.Rect(0, 0, 16, bone_h)
                            sx, sy = speed, 0
                            if gravity_dir == "DOWN":
                                if direction == 1: rect.bottomright = (arena_rect.left - 20, arena_rect.bottom - 5)
                                else: rect.bottomleft = (arena_rect.right + 20, arena_rect.bottom - 5)
                            else: 
                                if direction == 1: rect.topright = (arena_rect.left - 20, arena_rect.top + 5)
                                else: rect.topleft = (arena_rect.right + 20, arena_rect.top + 5)
                        else: 
                            rect = pygame.Rect(0, 0, bone_h, 16) 
                            sx, sy = 0, speed
                            if gravity_dir == "LEFT":
                                if direction == 1: rect.bottomleft = (arena_rect.left + 5, arena_rect.top - 20)
                                else: rect.topleft = (arena_rect.left + 5, arena_rect.bottom + 20)
                            else: 
                                if direction == 1: rect.bottomright = (arena_rect.right - 5, arena_rect.top - 20)
                                else: rect.topright = (arena_rect.right - 5, arena_rect.bottom + 20)
                        bullets.append({"rect": rect, "exact_x": float(rect.x), "exact_y": float(rect.y), "sx": sx, "sy": sy, "grazed": False, "type": "slide"})
                
                if p4_attack_type == "slam":
                    if spawn_timer == 15:
                        if gravity_dir == "DOWN": rect = pygame.Rect(arena_rect.left, arena_rect.bottom - 30, arena_rect.width, 30)
                        elif gravity_dir == "UP": rect = pygame.Rect(arena_rect.left, arena_rect.top, arena_rect.width, 30)
                        elif gravity_dir == "LEFT": rect = pygame.Rect(arena_rect.left, arena_rect.top, 30, arena_rect.height)
                        elif gravity_dir == "RIGHT": rect = pygame.Rect(arena_rect.right - 30, arena_rect.top, 30, arena_rect.height)
                        bullets.append({"rect": rect, "type": "warning", "timer": 30, "grazed": True})

                    elif spawn_timer == 45:
                        bullets.append({"rect": pygame.Rect(-100,-100,1,1), "type": "bone_wall", "timer": 20, "max_thick": 30, "wall_dir": gravity_dir, "grazed": False})
                    elif spawn_timer >= 80: spawn_timer = 0
                        
                elif p4_attack_type == "slide" and spawn_timer >= 45: spawn_timer = 0
                
            elif current_phase == 5:
                p5_special_timer += 1
                
                if p5_special_timer % 1200 == 0:
                    safe_spots = [(0,0), (2,0), (0,2), (2,2), (1,1)] 
                    safe_c, safe_r = random.choice(safe_spots)

                    cols = [ {"x": 200, "w": 134}, {"x": 334, "w": 133}, {"x": 467, "w": 133} ]
                    rows = [ {"y": 300, "h": 67},  {"y": 367, "h": 66},  {"y": 433, "h": 67}  ]

                    for c in range(3):
                        if c != safe_c:
                            beam = pygame.Rect(cols[c]["x"], arena_rect.top, cols[c]["w"], arena_rect.height)
                            warn = pygame.Rect(cols[c]["x"] + cols[c]["w"]//2 - 2, arena_rect.top, 4, arena_rect.height)
                            blaster = pygame.Rect(cols[c]["x"] + cols[c]["w"]//2 - 20, arena_rect.top - 35, 40, 30)
                            bullets.append({"type": "laser", "beam_rect": beam, "warn_rect": warn, "blaster_rect": blaster, "timer": 105, "grazed": False})

                    for r in range(3):
                        if r != safe_r:
                            beam = pygame.Rect(arena_rect.left, rows[r]["y"], arena_rect.width, rows[r]["h"])
                            warn = pygame.Rect(arena_rect.left, rows[r]["y"] + rows[r]["h"]//2 - 2, arena_rect.width, 4)
                            blaster = pygame.Rect(arena_rect.left - 35, rows[r]["y"] + rows[r]["h"]//2 - 20, 30, 40)
                            bullets.append({"type": "laser", "beam_rect": beam, "warn_rect": warn, "blaster_rect": blaster, "timer": 105, "grazed": False})
                    
                    spawn_timer = -105 
                
                if spawn_timer == 17: 
                    for angle_offset in [-0.25, 0, 0.25]:
                        spread_angle = angle_to_player + angle_offset
                        speed_x = math.cos(spread_angle) * 3.8 
                        speed_y = math.sin(spread_angle) * 3.8
                        bullet_rect = pygame.Rect(0, 0, 12, 12)
                        bullet_rect.center = boss_rect.center
                        bullets.append({"rect": bullet_rect, "exact_x": float(bullet_rect.x), "exact_y": float(bullet_rect.y), "sx": speed_x, "sy": speed_y, "grazed": False, "type": "proj"})
                
                if spawn_timer >= 35: 
                    num_blasters = random.choice([1, 2, 2]) 
                    for i in range(num_blasters):
                        ori = random.choice(["H", "V"])
                        thick = 40 
                        if ori == "H":
                            ty = player_center_y if i == 0 else random.randint(arena_rect.top+20, arena_rect.bottom-20)
                            beam_rect = pygame.Rect(arena_rect.left, ty - thick//2, arena_rect.width, thick)
                            warn_rect = pygame.Rect(arena_rect.left, ty - 1, arena_rect.width, 2)
                            blaster_rect = pygame.Rect(arena_rect.left - 30, ty - 20, 30, 40) 
                        else:
                            tx = player_center_x if i == 0 else random.randint(arena_rect.left+20, arena_rect.right-20)
                            beam_rect = pygame.Rect(tx - thick//2, arena_rect.top, thick, arena_rect.height)
                            warn_rect = pygame.Rect(tx - 1, arena_rect.top, 2, arena_rect.height)
                            blaster_rect = pygame.Rect(tx - 20, arena_rect.top - 30, 40, 30) 
                        bullets.append({"type": "laser", "beam_rect": beam_rect, "warn_rect": warn_rect, "blaster_rect": blaster_rect, "timer": 50, "grazed": False})
                    spawn_timer = 0

    if invulnerable_timer > 0:
        invulnerable_timer -= 1

    for b in bullets[:]:
        if b.get("type") == "warning":
            b["timer"] -= 1
            if b["timer"] <= 0: bullets.remove(b)
            continue 
            
        elif b.get("type") == "bone_wall":
            b["timer"] -= 1
            if b["timer"] <= 0: bullets.remove(b); continue
            
            life = b["timer"]
            max_t = b["max_thick"]
            if life > 16:    cur_t = max_t * (20 - life) / 4   
            elif life <= 8:  cur_t = max_t * life / 8          
            else:            cur_t = max_t                     
            
            cur_t = max(1, int(cur_t))
            wd = b["wall_dir"]
            
            if wd == "DOWN": b["rect"] = pygame.Rect(arena_rect.left, arena_rect.bottom - cur_t, arena_rect.width, cur_t)
            elif wd == "UP": b["rect"] = pygame.Rect(arena_rect.left, arena_rect.top, arena_rect.width, cur_t)
            elif wd == "LEFT": b["rect"] = pygame.Rect(arena_rect.left, arena_rect.top, cur_t, arena_rect.height)
            elif wd == "RIGHT": b["rect"] = pygame.Rect(arena_rect.right - cur_t, arena_rect.top, cur_t, arena_rect.height)
            
        elif b.get("type") == "laser":
            b["timer"] -= 1
            if b["timer"] <= 0: bullets.remove(b); continue
            
            if b["timer"] == 15:
                screen_shake = 18 
                
            if b["timer"] <= 15:
                if player_rect.colliderect(b["beam_rect"]):
                    if invulnerable_timer == 0 and not god_mode:
                        player_hp -= 1
                        invulnerable_timer = 60
                        screen_shake = 20
                elif not b["grazed"] and invulnerable_timer == 0 and graze_rect.colliderect(b["beam_rect"]):
                    b["grazed"] = True
                    if attack_cooldown > 0: attack_cooldown = max(1, attack_cooldown - 30)
                    graze_popups.append({"y": player_rect.top, "x": player_rect.centerx, "timer": 20})
            continue 
            
        else:
            b["exact_x"] += b["sx"]
            b["exact_y"] += b["sy"]
            b["rect"].x = int(b["exact_x"])
            b["rect"].y = int(b["exact_y"])
            
        if player_rect.colliderect(b["rect"]):
            if invulnerable_timer == 0 and not god_mode: 
                player_hp -= 1
                invulnerable_timer = 60
                screen_shake = 20 
                if b.get("type") not in ["bone_wall", "warning", "laser"]: bullets.remove(b) 
                graze_popups.clear() 
                
        elif not b["grazed"] and invulnerable_timer == 0 and graze_rect.colliderect(b["rect"]):
            b["grazed"] = True 
            if attack_cooldown > 0: attack_cooldown = max(1, attack_cooldown - 30) 
            graze_popups.append({"y": player_rect.top, "x": player_rect.centerx, "timer": 20})
            
        elif b.get("type") not in ["bone_wall", "warning", "laser"] and (b["rect"].y > HEIGHT or b["rect"].y < 0 or b["rect"].x < 0 or b["rect"].x > WIDTH):
            if b in bullets: bullets.remove(b)

    game_surf.fill(BLACK)
    pygame.draw.rect(game_surf, WHITE, arena_rect, 5)

    if game_state == "PLAYING":
        if boss_flash_timer > 0:
            pygame.draw.rect(game_surf, WHITE, boss_rect)
            boss_flash_timer -= 1
        else:
            pygame.draw.rect(game_surf, boss_color, boss_rect)

        if slash_timer > 0:
            pygame.draw.line(game_surf, WHITE, (boss_rect.left - 10, boss_rect.top - 10), (boss_rect.right + 10, boss_rect.bottom + 10), 5)
            slash_timer -= 1

        if damage_popup["timer"] > 0:
            color = RED if damage_popup["val"] not in ["MISS", "TIME UP!"] else (150, 150, 150)
            dmg_text = font_dmg.render(damage_popup["val"], True, color)
            game_surf.blit(dmg_text, (boss_rect.centerx + 30, damage_popup["y"]))
            damage_popup["y"] -= 1 
            damage_popup["timer"] -= 1

        pygame.draw.rect(game_surf, RED, (WIDTH//2 - 150, 40, 300, 15))
        health_ratio = boss_hp / boss_max_hp
        if health_ratio > 0:
            pygame.draw.rect(game_surf, GREEN, (WIDTH//2 - 150, 40, int(300 * health_ratio), 15))

        if attack_bar_active:
            pygame.draw.rect(game_surf, WHITE, (250, 510, 300, 30), 2)
            pygame.draw.rect(game_surf, GREEN, (390, 510, 20, 30))
            pygame.draw.rect(game_surf, LIGHT_BLUE, (cursor_x, 505, 6, 40))
            
            timer_ratio = player_turn_timer / 180.0
            pygame.draw.rect(game_surf, RED, (250, 545, 300, 5))
            pygame.draw.rect(game_surf, YELLOW, (250, 545, int(300 * timer_ratio), 5))
            
        else:
            charge_ratio = 1.0 - (attack_cooldown / 1800.0)
            pygame.draw.rect(game_surf, WHITE, (250, 510, 300, 15), 2)
            pygame.draw.rect(game_surf, LIGHT_BLUE, (250, 510, int(300 * charge_ratio), 15))
            c_text = font_charge.render("CHARGING...", True, WHITE)
            game_surf.blit(c_text, (400 - c_text.get_width()//2, 490))

    elif game_state == "VICTORY":
        win_text = font_big.render("BOSS DEFEATED", True, GOLD)
        game_surf.blit(win_text, (WIDTH//2 - win_text.get_width()//2, 150))

    for b in bullets:
        if b.get("type") == "warning":
            w_color = RED if (b["timer"] // 4) % 2 == 0 else YELLOW 
            pygame.draw.rect(game_surf, w_color, b["rect"])
        elif b.get("type") == "laser":
            if b["timer"] > 15:
                w_color = RED if (b["timer"] // 4) % 2 == 0 else YELLOW 
                pygame.draw.rect(game_surf, w_color, b["warn_rect"])
                pygame.draw.rect(game_surf, w_color, b["blaster_rect"])

    if god_mode: 
        pygame.draw.rect(game_surf, GOLD, player_rect)
    elif invulnerable_timer > 0 and invulnerable_timer % 10 < 5: 
        pygame.draw.rect(game_surf, WHITE, player_rect) 
    else: 
        pygame.draw.rect(game_surf, player_color, player_rect) 

    for b in bullets:
        if b.get("type") not in ["warning", "laser"]:
            pygame.draw.rect(game_surf, WHITE, b["rect"])
        elif b.get("type") == "laser" and b["timer"] <= 15:
            intensity = int(255 * (b["timer"] / 15))
            beam_color = (intensity, intensity, intensity)
            pygame.draw.rect(game_surf, beam_color, b["beam_rect"])
            pygame.draw.rect(game_surf, WHITE, b["blaster_rect"]) 

    for gp in graze_popups[:]:
        g_text = font_graze.render("GRAZE!", True, LIGHT_BLUE)
        game_surf.blit(g_text, (gp["x"] - g_text.get_width()//2, gp["y"]))
        gp["y"] -= 2
        gp["timer"] -= 1
        if gp["timer"] <= 0: graze_popups.remove(gp)

    if god_mode: game_surf.blit(font_main.render("GOD MODE", True, GOLD), (10, 10))
    else: game_surf.blit(font_main.render("Dev: [G] God [H] Heal [1-5] Phase Skip [C] Charge [O] 1HP", True, (100, 100, 100)), (10, 10))

    hp_text = font_main.render(f"HP", True, WHITE)
    game_surf.blit(hp_text, (200, 560))
    for i in range(player_hp):
        pygame.draw.rect(game_surf, GREEN, (260 + (i * 30), 560, 25, 25))

    phase_text = font_main.render(f"PHASE: {current_phase}", True, boss_color)
    game_surf.blit(phase_text, (500, 560))

    if screen_shake > 0:
        shake_x = random.randint(-8, 8)
        shake_y = random.randint(-8, 8)
        screen.blit(game_surf, (shake_x, shake_y))
        screen_shake -= 1
    else:
        screen.blit(game_surf, (0, 0))

    pygame.display.flip()
    clock.tick(60)
    
    if player_hp <= 0:
        reset_game()

pygame.quit()
sys.exit()
