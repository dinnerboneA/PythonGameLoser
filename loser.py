
import pygame
import math
import random
import sys

# --- Pygame Initialization ---
try:
    pygame.init()
    # It's a good practice to initialize the mixer for audio
    pygame.mixer.init()
except pygame.error as e:
    print(f"Error initializing Pygame: {e}")
    sys.exit()


def draw_entity_with_direction(screen, image, rect, direction):
    if direction == "left":
        flipped_image = pygame.transform.flip(image, True, False)
        screen.blit(flipped_image, rect)
    else:
        screen.blit(image, rect)

# --- Global Game State ---
unlocked_levels = {1}
current_level_number = 1
boss_active = False
enemies_destroyed_in_level = 0
total_enemies_for_level = 0
boss_attack_timer = 0
current_boss_attack = 'bullets'
background_music_enabled = True  # New global state for music
menu_music_playing = False  # New global state for menu music

# --- Game Constants and Settings (Easily Changeable) ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (239, 68, 68)
GREEN = (20, 184, 166)
BLUE = (59, 130, 246)
YELLOW = (252, 211, 77)
GRAY_LIGHT = (107, 114, 128)
GRAY_DARK = (31, 41, 55)
PURPLE = (147, 51, 234)
ORANGE = (249, 115, 22)
MEDIC_COLOR = (255, 255, 255)  # White color for medic helicopter
LASER_COLOR = (255, 0, 0, 150)  # Red with some transparency
WARNING_COLOR = (255, 255, 0, 150)  # Yellow warning color with transparency

GAME_SETTINGS = {
    'PLAYER_SPEED': 5,
    'PLAYER_HEALTH': 100,
    'SHIELD_METER_MAX': 100,
    'SHIELD_DRAIN_RATE': 0.15,  # Shield meter drains per frame
    'SHIELD_REFILL_ON_PICKUP': 20,  # %
    'PLAYER_BULLET_SPEED': 10,
    'PLAYER_BULLET_DAMAGE': 10,
    'BOMB_BULLET_DAMAGE': 50,
    'BOMB_AOE': 150,
    'RAPID_FIRE_RATE': 100,
    'STANDARD_FIRE_RATE': 200,
    'ENEMY_BULLET_SPEED': 5,
    'ENEMY_BULLET_DAMAGE': 5,
    'TANK_BULLET_DAMAGE': 10,
    'BOSS_BULLET_DAMAGE': 10,  # Base damage for boss bullet attack
    'BOSS_BOMB_DAMAGE': 20,
    'BOSS_LASER_DAMAGE': 10,  # Damage per hit if not shielded
    'BOSS_LASER_SHIELD_DRAIN': 2,  # Shield damage per hit
    'LASER_WARNING_DURATION': 1000,  # ms, how long the warning sign is visible before the laser fires
    'ENEMY_AIR_SPAWN_RATE': 2000,
    'ENEMY_GROUND_SPAWN_RATE': 20000,
    'MEDIC_SPAWN_RATE': 19000,  # Medic helicopter spawns
    'MAX_ENEMIES_ON_SCREEN': 5,
    'LEVEL_1_TOTAL_ENEMIES': 20,
    'LEVEL_2_TOTAL_ENEMIES': 30,
    'BOSS_HEALTH_L1': 500,
    'BOSS_HEALTH_L2': 1000,
    'ENEMY_DROP_CHANCES': {
        'coin': 0.3,  # 30% chance for a coin
        'shield': 0.1  # 10% chance for a shield pickup
    },
    'DROP_DESPAWN_TIME': 5000,  # ms
    'SCORES': {
        'helicopter': 10,
        'jet': 20,
        'tank': 30,
        'boss': 100,
        'medic_helicopter': -25  # Penalty for shooting medic
    },
    'COIN_VALUES': {
        'helicopter': 5,
        'jet': 10,
        'tank': 15,
        'boss': 50,
        'medic_helicopter': -20,  # Penalty for shooting medic
        'medic_pass_by': 15  # Reward for letting medic pass
    },
    'UPGRADE_COSTS': {
        'rapid_fire': 100,
        'shield_upgrade': 100,
        'bomb_gun': 200
    }
}

# --- Screen Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Loser")  # Changed title here
clock = pygame.time.Clock()
FONT_SIZE = 18
font = pygame.font.Font(None, FONT_SIZE)
large_font = pygame.font.Font(None, 40)
hud_font = pygame.font.Font(None, 24)

# --- Asset Loading ---

try:
    # Player and Enemies
    player_image = pygame.image.load("player_tank.png").convert_alpha()
    player_cannon_image = pygame.image.load("player_cannon.png").convert_alpha()
    enemy_helicopter_image = pygame.image.load("enemy_helicopter.png").convert_alpha()
    enemy_jet_image = pygame.image.load("enemy_jet.png").convert_alpha()
    enemy_tank_image = pygame.image.load("enemy_tank.png").convert_alpha()
    boss_image = pygame.image.load("boss.png").convert_alpha()
    medic_helicopter_image = pygame.image.load("medic_helicopter.png").convert_alpha()

    # Pickups
    coin_image = pygame.image.load("coin.png").convert_alpha()
    shield_pickup_image = pygame.image.load("shield_pickup.png").convert_alpha()

    # Special effects & bullets
    player_bullet_image = pygame.image.load("player_bullet.png").convert_alpha()
    bomb_bullet_image = pygame.image.load("bomb_bullet.png").convert_alpha()
    enemy_bullet_image = pygame.image.load("enemy_bullet.png").convert_alpha()
    explosion_image = pygame.image.load("explosion.png").convert_alpha()

    # Backgrounds - New assets
    menu_bg_image = pygame.image.load("menu_bg.png").convert()
    level1_bg_image = pygame.image.load("level1_bg.png").convert()
    level2_bg_image = pygame.image.load("level2_bg.png").convert()

    # Sound effects
    player_fire_sfx = pygame.mixer.Sound("player_fire.wav")
    enemy_explosion_sfx = pygame.mixer.Sound("enemy_explosion.wav")
    pickup_sfx = pygame.mixer.Sound("pickup.wav")
    game_over_sfx = pygame.mixer.Sound("game_over.wav")

    # Music - New assets
    menu_music = "menu_music.mp3"
    level1_music = "level1_music.mp3"
    level2_music = "level2_music.mp3"

except pygame.error as e:
    print(f"Error loading an asset: {e}")
    # Handle the error by falling back to drawing shapes
    player_image = None
    player_cannon_image = None
    enemy_helicopter_image = None
    enemy_jet_image = None
    enemy_tank_image = None
    boss_image = None
    medic_helicopter_image = None
    coin_image = None
    shield_pickup_image = None
    player_bullet_image = None
    bomb_bullet_image = None
    enemy_bullet_image = None
    explosion_image = None
    menu_bg_image = None
    level1_bg_image = None
    level2_bg_image = None
    player_fire_sfx = None
    enemy_explosion_sfx = None
    pickup_sfx = None
    game_over_sfx = None
    menu_music = None
    level1_music = None
    level2_music = None


# --- Classes ---

class Player:
    """Represents the player's tank and cannon."""

    def __init__(self):
        self.width = 60
        self.height = 40
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 60
        self.health = GAME_SETTINGS['PLAYER_HEALTH']
        self.cannon_angle = -math.pi / 2
        self.cannon_target_angle = -math.pi / 2
        self.shield_active = False
        self.shield_meter = GAME_SETTINGS['SHIELD_METER_MAX']
        self.coins = 0
        self.upgrades = {'rapid_fire': False, 'bomb_gun': False, 'shield_upgrade': False}
        self.is_hit_by_laser = False  # Flag to indicate if player is currently in a laser beam

    def draw(self, screen):
        """Draws the tank and cannon on the screen."""
        if player_image:
            # Scale the image to fit the tank's dimensions and draw it
            scaled_player_image = pygame.transform.scale(player_image, (self.width, self.height))
            screen.blit(scaled_player_image, (self.x - self.width // 2, self.y - self.height // 2))
        else:
            # Fallback to drawing a shape if image failed to load
            pygame.draw.rect(screen, GRAY_LIGHT,
                             (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height),
                             border_radius=8)
            pygame.draw.circle(screen, GRAY_DARK, (self.x, self.y), self.width // 3)

        # Cannon
        if player_cannon_image:
            # Set cannon size (you can define these as class attributes or constants)
            cannon_width = 20  # <--- Changeable width
            cannon_height = 80  # <--- Changeable height

            # Scale the cannon image before rotating
            resized_cannon = pygame.transform.scale(player_cannon_image, (cannon_width, cannon_height))
            rotated_cannon = pygame.transform.rotate(resized_cannon, -math.degrees(self.cannon_angle) - 90)
            cannon_rect = rotated_cannon.get_rect(center=(self.x, self.y))
            screen.blit(rotated_cannon, cannon_rect)

        else:
            # Fallback to drawing a line
            cannon_length = 30
            cannon_end_x = self.x + math.cos(self.cannon_angle) * cannon_length
            cannon_end_y = self.y + math.sin(self.cannon_angle) * cannon_length
            pygame.draw.line(screen, GRAY_DARK, (self.x, self.y), (cannon_end_x, cannon_end_y), 5)

        # Shield
        if self.shield_active:
            shield_radius = self.width + 5
            # Shield color fades with meter level
            alpha = int(255 * (self.shield_meter / GAME_SETTINGS['SHIELD_METER_MAX']))
            if alpha > 0:
                shield_color = (BLUE[0], BLUE[1], BLUE[2], alpha)
                s = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, shield_color, (shield_radius, shield_radius), shield_radius, 4)
                screen.blit(s, (self.x - shield_radius, self.y - shield_radius))

    def update(self, keys, mouse_pos):
        """Updates player position and cannon angle based on input."""
        speed = GAME_SETTINGS['PLAYER_SPEED']
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(self.width // 2, self.x - speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(SCREEN_WIDTH - self.width // 2, self.x + speed)

        # Spacebar to toggle shield
        if keys[pygame.K_SPACE]:
            if not self.shield_active and self.shield_meter > 0:
                self.shield_active = True
        else:
            self.shield_active = False

        if self.shield_active:
            # Drain shield meter
            drain_rate = GAME_SETTINGS['SHIELD_DRAIN_RATE']
            if self.upgrades['shield_upgrade']:
                drain_rate *= 0.5  # Shield upgrade makes it drain slower
            self.shield_meter -= drain_rate
            if self.shield_meter <= 0:
                self.shield_meter = 0
                self.shield_active = False

        self.is_hit_by_laser = False  # Reset flag each frame

        # Cannon aiming logic
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.cannon_target_angle = math.atan2(dy, dx)
        angle_diff = self.cannon_target_angle - self.cannon_angle
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        self.cannon_angle += angle_diff * 0.1


class Bullet:
    """Represents a projectile fired by the player or enemy."""

    def __init__(self, x, y, angle, speed, damage, is_bomb=False, from_player=True):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = 8 if is_bomb else 3
        self.is_bomb = is_bomb
        self.damage = damage
        self.from_player = from_player

    def draw(self, screen):
        """Draws the bullet on the screen using an image."""
        if self.from_player and not self.is_bomb and player_bullet_image:
            img = pygame.transform.scale(player_bullet_image, (self.radius * 2, self.radius * 2))
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(img, rect)
        elif self.is_bomb and bomb_bullet_image:
            img = pygame.transform.scale(bomb_bullet_image, (self.radius * 2, self.radius * 2))
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(img, rect)
        elif not self.from_player and enemy_bullet_image:
            img = pygame.transform.scale(enemy_bullet_image, (self.radius * 2, self.radius * 2))
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(img, rect)
        else:
            # Fallback to drawing a shape
            color = RED if self.from_player and not self.is_bomb else ORANGE
            if self.is_bomb:
                color = (255, 100, 0)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)

    def update(self):
        """Updates bullet position."""
        self.x += self.vx
        self.y += self.vy


class BombBullet(Bullet):
    """A special type of bullet for the boss that falls and explodes."""

    def __init__(self, x, y, damage):
        super().__init__(x, y, 0, 0, damage, is_bomb=True, from_player=False)
        self.radius = 12
        self.vy = 2
        self.grounded = False

    def update(self):
        """Updates bomb position with gravity."""
        if not self.grounded:
            self.y += self.vy
            if self.y >= SCREEN_HEIGHT - 60:
                self.y = SCREEN_HEIGHT - 60
                self.grounded = True
                self.vx = 0
                self.vy = 0


class LaserWarning:
    """Represents a visual warning for an upcoming laser attack."""

    def __init__(self, start_pos, end_pos, duration=GAME_SETTINGS['LASER_WARNING_DURATION']):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.width = 10
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.done = False

    def draw(self, screen):
        """Draws the flashing warning line."""
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time > self.duration:
            self.done = True
            return

        # Flashing effect
        flash_interval = 200
        if (elapsed_time // flash_interval) % 2 == 0:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            color_with_alpha = WARNING_COLOR
            pygame.draw.line(s, color_with_alpha, self.start_pos, self.end_pos, self.width)
            screen.blit(s, (0, 0))


class Laser:
    """Represents a laser beam fired by the boss."""

    def __init__(self, start_pos, end_pos, duration=1000):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.width = 10
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.done = False
        self.hit_player = False  # Flag to ensure damage is dealt only once

    def draw(self, screen):
        """Draws the laser beam."""
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time > self.duration:
            self.done = True
            return

        # Alpha transparency for a fading effect
        alpha = 255 - int(255 * (elapsed_time / self.duration))
        if alpha > 0:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            color_with_alpha = LASER_COLOR
            pygame.draw.line(s, color_with_alpha, self.start_pos, self.end_pos, self.width)
            screen.blit(s, (0, 0))


class Enemy:
    """Base class for all enemies with random movement."""

    def __init__(self, type, x, y, speed, health, width, height, can_fire, fire_rate_mod=1):
        self.type = type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = health
        self.can_fire = can_fire
        self.fire_rate_mod = fire_rate_mod
        self.last_fire_time = pygame.time.get_ticks()

        self.vx = speed if x == 0 else -speed
        self.vy = 0
        if self.type == 'boss':
            self.vy = speed
        elif self.type != 'tank':
            self.vy = random.uniform(-1, 1)

    def draw(self, screen):
        """Draws the enemy on the screen using an image."""
        image = None
        if self.type == 'helicopter' and enemy_helicopter_image:
            image = enemy_helicopter_image
        elif self.type == 'jet' and enemy_jet_image:
            image = enemy_jet_image
        elif self.type == 'tank' and enemy_tank_image:
            image = enemy_tank_image
        elif self.type == 'boss' and boss_image:
            image = boss_image
        elif self.type == 'medic_helicopter' and medic_helicopter_image:
            image = medic_helicopter_image

        if image:
            # Optional: override default size per enemy type
            if self.type == 'helicopter':
                image_width, image_height = 100, 60
            elif self.type == 'jet':
                image_width, image_height = 120, 55
            elif self.type == 'tank':
                image_width, image_height = 90, 70
            elif self.type == 'boss':
                image_width, image_height = 150, 100
            elif self.type == 'medic_helicopter':
                image_width, image_height = 100, 55
            else:
                image_width, image_height = self.width, self.height  # fallback

            scaled_image = pygame.transform.scale(image, (image_width, image_height))
            rect = scaled_image.get_rect(center=(self.x, self.y))
            screen.blit(scaled_image, rect)
        else:
            # Fallback to drawing a shape if image failed to load
            color_map = {
                'helicopter': GREEN,
                'jet': ORANGE,
                'tank': (148, 163, 184),
                'boss': PURPLE,
                'medic_helicopter': MEDIC_COLOR
            }
            color = color_map.get(self.type, WHITE)
            if self.type == 'tank':
                # Tank body
                pygame.draw.rect(screen, color,
                                 (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height),
                                 border_radius=5)
                pygame.draw.rect(screen, GRAY_DARK,
                                 (self.x - self.width // 2, self.y - self.height // 2 - 10, self.width, 10))
            elif self.type == 'boss':
                pygame.draw.rect(screen, color,
                                 (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height),
                                 border_radius=15)
            else:
                # Air enemies
                pygame.draw.rect(screen, color,
                                 (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height))
                if self.type == 'medic_helicopter':
                    draw_text(screen, "+", font, RED, self.x, self.y, centered=True)

    def update(self):
        """Updates enemy position with random movement, restricted to the top of the screen."""
        if self.type == 'tank':
            # Tanks move horizontally on the ground, bouncing off walls
            self.x += self.vx
            if self.x <= self.width // 2 or self.x >= SCREEN_WIDTH - self.width // 2:
                self.vx *= -1
        elif self.type == 'boss':
            # Boss bounces off screen edges
            self.x += self.vx
            self.y += self.vy
            if self.x <= self.width // 2 or self.x >= SCREEN_WIDTH - self.width // 2:
                self.vx *= -1
            if self.y <= self.height // 2 or self.y >= SCREEN_HEIGHT * 0.5 - self.height // 2:
                self.vy *= -1
        else:
            # Air enemies fly across the screen with a slight vertical movement
            self.x += self.vx
            self.y += self.vy

            # Keep air enemies within the upper part of the screen
            min_y = SCREEN_HEIGHT * 0.1
            max_y = SCREEN_HEIGHT * 0.5
            if self.y <= min_y or self.y >= max_y:
                self.vy *= -1

    def fire(self, player_x, player_y):
        """Enemy firing logic, returns a bullet if it fires."""
        now = pygame.time.get_ticks()
        fire_rate = 2000
        damage = GAME_SETTINGS['ENEMY_BULLET_DAMAGE']
        new_bullets = []

        if self.type == 'jet':
            fire_rate = 1500
        elif self.type == 'tank':
            fire_rate = 3000
            damage = GAME_SETTINGS['TANK_BULLET_DAMAGE']
        elif self.type == 'boss':
            fire_rate = 1000
            # Boss attacks are handled separately in the main loop based on a timer
            return new_bullets

        # Apply a modification to the fire rate based on level
        fire_rate /= self.fire_rate_mod

        if self.can_fire and now - self.last_fire_time > fire_rate:
            angle = math.atan2(player_y - self.y, player_x - self.x)
            self.last_fire_time = now
            new_bullets.append \
                (Bullet(self.x, self.y, angle, GAME_SETTINGS['ENEMY_BULLET_SPEED'], damage, from_player=False))
        return new_bullets


class Drop:
    """Represents a dropped item (coin or shield pickup)."""

    def __init__(self, type, x, y):
        self.type = type
        self.x = x
        self.y = y
        self.vy = 2  # Downward velocity
        self.radius = 13
        self.spawn_time = pygame.time.get_ticks()
        self.grounded = False

    def draw(self, screen):
        """Draws the drop on the screen using an image."""
        image = None
        if self.type == 'coin' and coin_image:
            image = coin_image
        elif self.type == 'shield' and shield_pickup_image:
            image = shield_pickup_image

        if image:
            scaled_image = pygame.transform.scale(image, (self.radius * 2, self.radius * 2))
            rect = scaled_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(scaled_image, rect)
        else:
            # Fallback to drawing a shape
            color = YELLOW if self.type == 'coin' else BLUE
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
            icon_text = "$" if self.type == 'coin' else "S"
            draw_text(screen, icon_text, font, BLACK, self.x, self.y, centered=True)

    def update(self):
        """Drops fall until they hit the bottom of the screen."""
        if not self.grounded:
            self.y += self.vy
            if self.y >= SCREEN_HEIGHT - 60:  # Stop falling at player's y-level
                self.y = SCREEN_HEIGHT - 60
                self.grounded = True


class Explosion:
    """A simple class to handle visual explosions using a sprite."""

    def __init__(self, x, y, size, bomb=False):
        self.x = x
        self.y = y
        self.size = size
        self.color = ORANGE if bomb else RED
        self.start_time = pygame.time.get_ticks()
        self.duration = 500  # milliseconds
        self.done = False

    def draw(self, screen):
        """Draws the explosion effect."""
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time > self.duration:
            self.done = True
            return

        progress = elapsed_time / self.duration
        current_radius = int(self.size * (progress + 0.1))  # Start from a small size

        # Use image if available
        if explosion_image:
            alpha = 255 - int(255 * progress)
            if alpha > 0:
                scaled_image = pygame.transform.scale(explosion_image, (current_radius * 2, current_radius * 2))
                scaled_image.set_alpha(alpha)
                rect = scaled_image.get_rect(center=(self.x, self.y))
                screen.blit(scaled_image, rect)
        else:
            # Fallback to drawing a shape
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            alpha = 255 - int(255 * progress)
            if alpha > 0:
                color_with_alpha = self.color + (alpha,)
                pygame.draw.circle(s, color_with_alpha, (self.size, self.size), current_radius)
                screen.blit(s, (self.x - self.size, self.y - self.size))


def draw_text(surface, text, font, color, x, y, centered=False):
    """Utility function to draw text on the screen."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if centered:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def button(screen, text, x, y, w, h, inactive_color, active_color, action=None, font_size=FONT_SIZE, enabled=True):
    """Creates a clickable button."""
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    current_font = pygame.font.Font(None, font_size)

    button_color = inactive_color
    if enabled:
        if x + w > mouse[0] > x and y + h > mouse[1] > y:
            button_color = active_color
            if click[0] == 1 and action is not None:
                action()
                return True

    pygame.draw.rect(screen, button_color, (x, y, w, h), border_radius=8)
    draw_text(screen, text, current_font, WHITE, x + w // 2, y + h // 2, centered=True)
    return False


def upgrade_shop(player):
    """Displays the upgrade shop."""
    message = ""

    def buy_upgrade(upgrade_id):
        nonlocal message
        cost = GAME_SETTINGS['UPGRADE_COSTS'][upgrade_id]
        if player.coins >= cost and not player.upgrades[upgrade_id]:
            player.upgrades[upgrade_id] = True
            player.coins -= cost
            message = f"Purchased {upgrade_id.replace('_', ' ').title()}!"
            if pickup_sfx: pickup_sfx.play()
        elif player.upgrades[upgrade_id]:
            message = "You already own this upgrade."
        else:
            message = "Not enough coins!"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    return  # Exit the shop and return to game

        screen.fill(GRAY_DARK)
        draw_text(screen, "Upgrade Shop", large_font, WHITE, SCREEN_WIDTH // 2, 50, centered=True)
        draw_text(screen, f"Current Coins: {player.coins}", hud_font, YELLOW, SCREEN_WIDTH // 2, 90, centered=True)
        if message:
            draw_text(screen, message, font, YELLOW, SCREEN_WIDTH // 2, 120, centered=True)

        upgrade_x = SCREEN_WIDTH // 2 - 100
        upgrade_y = 180

        # Rapid Fire Button
        if not player.upgrades['rapid_fire']:
            button(screen, f"Rapid Fire ({GAME_SETTINGS['UPGRADE_COSTS']['rapid_fire']} coins)", upgrade_x, upgrade_y,
                   200, 50, PURPLE, (120, 0, 200), lambda: buy_upgrade('rapid_fire'))
        else:
            button(screen, "Rapid Fire (Owned)", upgrade_x, upgrade_y, 200, 50, GRAY_LIGHT, GRAY_LIGHT, enabled=False)

        # Shield Upgrade Button (Shield drains slower)
        if not player.upgrades['shield_upgrade']:
            button(screen, f"Shield Upgrade ({GAME_SETTINGS['UPGRADE_COSTS']['shield_upgrade']} coins)", upgrade_x,
                   upgrade_y + 70, 200, 50, PURPLE, (120, 0, 200), lambda: buy_upgrade('shield_upgrade'))
        else:
            button(screen, "Shield Upgrade (Owned)", upgrade_x, upgrade_y + 70, 200, 50, GRAY_LIGHT, GRAY_LIGHT,
                   enabled=False)

        # Bomb Gun Button
        if not player.upgrades['bomb_gun']:
            button(screen, f"Bomb Gun ({GAME_SETTINGS['UPGRADE_COSTS']['bomb_gun']} coins)", upgrade_x, upgrade_y + 140,
                   200, 50, PURPLE, (120, 0, 200), lambda: buy_upgrade('bomb_gun'))
        else:
            button(screen, "Bomb Gun (Owned)", upgrade_x, upgrade_y + 140, 200, 50, GRAY_LIGHT, GRAY_LIGHT,
                   enabled=False)

        draw_text(screen, "Press 'U' to return to game", font, GRAY_LIGHT, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50,
                  centered=True)

        pygame.display.flip()
        clock.tick(60)

def settings_menu():
    """Displays the settings menu."""
    global background_music_enabled, menu_music_playing

    while True:
        mouse = pygame.mouse.get_pos()
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True

        screen.fill(GRAY_DARK)
        draw_text(screen, "Settings", large_font, WHITE, SCREEN_WIDTH // 2, 50, centered=True)

        # Music toggle button area
        music_toggle_text = "Music: ON" if background_music_enabled else "Music: OFF"
        music_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 150, 200, 50)
        pygame.draw.rect(screen, GREEN if music_btn_rect.collidepoint(mouse) else (0, 200, 0), music_btn_rect)
        draw_text(screen, music_toggle_text, font, WHITE, music_btn_rect.centerx, music_btn_rect.centery, centered=True)

        if music_btn_rect.collidepoint(mouse) and click:
            background_music_enabled = not background_music_enabled
            if background_music_enabled and menu_music:
                pygame.mixer.music.load(menu_music)
                pygame.mixer.music.play(-1)
            elif not background_music_enabled:
                pygame.mixer.music.stop()

        # Back button area
        back_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 220, 200, 50)
        pygame.draw.rect(screen, RED if back_btn_rect.collidepoint(mouse) else (200, 0, 0), back_btn_rect)
        draw_text(screen, "Back", font, WHITE, back_btn_rect.centerx, back_btn_rect.centery, centered=True)

        if back_btn_rect.collidepoint(mouse) and click:
            return  # Exit settings menu

        pygame.display.flip()
        clock.tick(60)


def main_menu():
    """Displays the main menu screen."""
    global unlocked_levels, current_level_number, background_music_enabled, menu_music_playing

    if background_music_enabled and not menu_music_playing and menu_music:
        pygame.mixer.music.load(menu_music)
        pygame.mixer.music.play(-1)
        menu_music_playing = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if menu_bg_image:
            screen.blit(pygame.transform.scale(menu_bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        else:
            screen.fill(GRAY_DARK)

        draw_text(screen, "Loser", large_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4,
                  centered=True)  # Changed title here

        draw_text(screen, "Select a Level:", font, GRAY_LIGHT, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80,
                  centered=True)

        level_buttons_y = SCREEN_HEIGHT // 2 - 40
        # Level 1 button
        if button(screen, "Level 1", SCREEN_WIDTH // 2 - 100, level_buttons_y, 200, 50, GREEN, (0, 200, 0),
                  lambda: run_game(1)):
            current_level_number = 1
            pygame.mixer.music.stop()
            return

        # Level 2 button
        level_2_unlocked = 2 in unlocked_levels
        if button(screen, "Level 2" if level_2_unlocked else "Level 2 (Locked)", SCREEN_WIDTH // 2 - 100,
                  level_buttons_y + 60, 200, 50, GREEN if level_2_unlocked else GRAY_LIGHT, (0, 200, 0),
                  lambda: run_game(2), enabled=level_2_unlocked):
            current_level_number = 2
            pygame.mixer.music.stop()
            return

        # Settings button
        if button(screen, "Settings", SCREEN_WIDTH // 2 - 100, level_buttons_y + 120, 200, 50, BLUE, (59, 100, 246),
                  settings_menu):
            pass

        draw_text(screen, "Controls:", font, GRAY_LIGHT, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120, centered=True)
        draw_text(screen, "Desktop: Arrow Keys/A & D to move, Mouse to aim & click to fire.", font, GRAY_LIGHT,
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, centered=True)
        draw_text(screen, "Space to activate shield, U for Upgrade Shop.", font, GRAY_LIGHT, SCREEN_WIDTH // 2,
                  SCREEN_HEIGHT - 80, centered=True)

        pygame.display.flip()
        clock.tick(60)


def game_over_screen(score, coins, upgrades, level_completed=False):
    """Displays the game over screen with stats."""
    global unlocked_levels, menu_music_playing
    debriefing = "You fought valiantly, but the enemy forces proved too overwhelming. We'll get 'em next time."
    if level_completed:
        debriefing = f"Congratulations! You successfully completed Level {level_completed}!"
        title = "MISSION COMPLETE"
        title_color = GREEN
        unlocked_levels.add(level_completed + 1)
    else:
        title = "MISSION FAILED"
        title_color = RED
        if game_over_sfx: game_over_sfx.play()

    if background_music_enabled and menu_music:
        pygame.mixer.music.load(menu_music)
        pygame.mixer.music.play(-1)
        menu_music_playing = True
    else:
        menu_music_playing = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(GRAY_DARK)
        draw_text(screen, title, large_font, title_color, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, centered=True)
        draw_text(screen, f"Final Score: {score}", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 50,
                  centered=True)
        draw_text(screen, f"Total Coins: {coins}", font, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 75,
                  centered=True)

        # Debriefing box
        pygame.draw.rect(screen, GRAY_LIGHT, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2, 500, 70), border_radius=8)
        draw_text(screen, debriefing, font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 35, centered=True)

        # The restart button now returns to the main menu, which will allow a new game to be started
        if button(screen, "Return to Main Menu", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50, GREEN,
                  (0, 200, 0), main_menu):
            return

        pygame.display.flip()
        clock.tick(60)


def run_game(level_num):
    """The main game loop and logic."""
    global boss_active, enemies_destroyed_in_level, total_enemies_for_level, boss_attack_timer, current_boss_attack, background_music_enabled, menu_music_playing

    # Play level music
    if background_music_enabled:
        music_file = level1_music if level_num == 1 else level2_music
        if music_file:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)
    menu_music_playing = False

    player = Player()
    bullets = []
    enemies = []
    enemy_bullets = []
    drops = []
    explosions = []
    lasers = []
    laser_warnings = []  # New list for laser warnings

    score = 0
    level = level_num
    enemies_spawned_in_level = 0
    total_enemies_for_level = GAME_SETTINGS[f'LEVEL_{level}_TOTAL_ENEMIES']

    last_air_spawn = pygame.time.get_ticks()
    last_ground_spawn = pygame.time.get_ticks()
    last_medic_spawn = pygame.time.get_ticks()
    last_fire = pygame.time.get_ticks()

    boss_active = False
    enemies_destroyed_in_level = 0
    boss_attack_timer = pygame.time.get_ticks()
    boss_attack_cooldown = 3000  # Time between boss attacks

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    upgrade_shop(player)

        # --- Input Handling ---
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        player.update(keys, mouse_pos)

        # Player firing
        now = pygame.time.get_ticks()
        fire_rate = GAME_SETTINGS['RAPID_FIRE_RATE'] if player.upgrades['rapid_fire'] else GAME_SETTINGS[
            'STANDARD_FIRE_RATE']
        if pygame.mouse.get_pressed()[0] and now - last_fire > fire_rate:
            bullets.append(Bullet(player.x, player.y, player.cannon_angle, GAME_SETTINGS['PLAYER_BULLET_SPEED'],
                                  GAME_SETTINGS['BOMB_BULLET_DAMAGE'] if player.upgrades['bomb_gun'] else GAME_SETTINGS
                                  ['PLAYER_BULLET_DAMAGE'],
                                  is_bomb=player.upgrades['bomb_gun']))
            if player_fire_sfx: player_fire_sfx.play()  # Play firing sound
            last_fire = now

        # --- Enemy Spawning ---
        # Spawning for regular enemies is now capped by total_enemies_for_level
        if enemies_spawned_in_level < total_enemies_for_level and not boss_active:
            if len([e for e in enemies if e.type not in ['boss', 'medic_helicopter']]) < GAME_SETTINGS[
                'MAX_ENEMIES_ON_SCREEN']:
                if now - last_air_spawn > GAME_SETTINGS['ENEMY_AIR_SPAWN_RATE']:
                    enemy_type = 'helicopter' if random.random() > 0.5 else 'jet'
                    start_x = 0 if random.random() > 0.5 else SCREEN_WIDTH
                    speed = 2 if level == 1 else 3
                    health = 10 if enemy_type == 'helicopter' else 20
                    enemies.append \
                        (Enemy(enemy_type, start_x, random.uniform(SCREEN_HEIGHT * 0.1, SCREEN_HEIGHT * 0.5), speed,
                               health, 50, 30, True, level))
                    last_air_spawn = now
                    enemies_spawned_in_level += 1

                if level >= 2 and now - last_ground_spawn > GAME_SETTINGS['ENEMY_GROUND_SPAWN_RATE']:
                    start_x = 0 if random.random() > 0.5 else SCREEN_WIDTH
                    speed = 1 if level == 2 else 1.5
                    enemies.append(Enemy('tank', start_x, SCREEN_HEIGHT - 40, speed, 50, 80, 40, True, level))
                    last_ground_spawn = now
                    enemies_spawned_in_level += 1

        if not boss_active:
            if now - last_medic_spawn > GAME_SETTINGS['MEDIC_SPAWN_RATE']:
                start_x = 0 if random.random() > 0.5 else SCREEN_WIDTH
                speed = 3
                enemies.append \
                    (Enemy('medic_helicopter', start_x, random.uniform(SCREEN_HEIGHT * 0.1, SCREEN_HEIGHT * 0.5), speed, 1,
                           50, 30, False, 1))
                last_medic_spawn = now





        # Boss spawning logic: check if enough enemies are destroyed
        if enemies_destroyed_in_level >= total_enemies_for_level and not boss_active:
            boss_health = GAME_SETTINGS[f'BOSS_HEALTH_L{level}']
            boss_size = 150
            enemies.append \
                (Enemy('boss', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, 1, boss_health, boss_size, boss_size, True,
                       level))
            boss_active = True
            boss_attack_timer = now

        # --- Boss Attack Logic (State Machine) ---
        # Only run boss logic if there is a boss in the enemies list
        if boss_active and enemies:
            boss = enemies[0]
            if now - boss_attack_timer > boss_attack_cooldown:
                # Cycle through attack patterns
                if current_boss_attack == 'bullets':
                    current_boss_attack = 'bombs'
                elif current_boss_attack == 'bombs':
                    current_boss_attack = 'laser'
                    # When switching to laser, create a warning instead of a laser
                    laser_warnings.append(LaserWarning((boss.x, boss.y), (player.x, player.y)))
                elif current_boss_attack == 'laser':
                    current_boss_attack = 'bullets'

                boss_attack_timer = now

            if current_boss_attack == 'bullets' and now - boss.last_fire_time > 200:
                angle = math.atan2(player.y - boss.y, player.x - boss.x)
                enemy_bullets.append(Bullet(boss.x, boss.y, angle, GAME_SETTINGS['ENEMY_BULLET_SPEED'] * 1.5,
                                            GAME_SETTINGS['BOSS_BULLET_DAMAGE'], from_player=False))
                boss.last_fire_time = now
            elif current_boss_attack == 'bombs' and now - boss.last_fire_time > 1000:
                enemy_bullets.append(BombBullet(boss.x, boss.y, GAME_SETTINGS['BOSS_BOMB_DAMAGE']))
                boss.last_fire_time = now
            elif current_boss_attack == 'laser' and not laser_warnings and not lasers:  # Fire the laser only after the warning is gone
                lasers.append(Laser((boss.x, boss.y), (player.x, player.y)))

        # --- Update Game Objects ---
        for bullet in bullets:
            bullet.update()

        for enemy in enemies:
            enemy.update()
            if enemy.type != 'boss' and enemy.can_fire:
                new_bullets = enemy.fire(player.x, player.y)
                enemy_bullets.extend(new_bullets)

        for e_bullet in enemy_bullets:
            e_bullet.update()

        for drop in drops:
            drop.update()

        for laser in lasers:
            laser.draw(screen)
        for warning in laser_warnings:
            warning.draw(screen)

        # --- Collision Detection (Player Bullets vs Enemies) ---
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if (bullet.x > enemy.x - enemy.width // 2 and
                        bullet.x < enemy.x + enemy.width // 2 and
                        bullet.y > enemy.y - enemy.height // 2 and
                        bullet.y < enemy.y + enemy.height // 2):

                    if enemy.type == 'medic_helicopter':
                        score += GAME_SETTINGS['SCORES']['medic_helicopter']
                        player.coins += GAME_SETTINGS['COIN_VALUES']['medic_helicopter']
                        explosions.append(Explosion(enemy.x, enemy.y, 50))
                        if enemy_explosion_sfx: enemy_explosion_sfx.play()  # Play explosion sound
                        enemies.remove(enemy)
                        bullets.remove(bullet)
                        continue  # Skip to next enemy

                    if bullet.is_bomb:
                        # Bomb explosion AOE
                        for e in enemies[:]:
                            distance = math.sqrt((e.x - bullet.x) ** 2 + (e.y - bullet.y) ** 2)
                            if distance < GAME_SETTINGS['BOMB_AOE']:
                                e.health -= bullet.damage
                                if e.health <= 0 and e.type != 'medic_helicopter':
                                    # Handle drops for destroyed enemies
                                    if random.random() < GAME_SETTINGS['ENEMY_DROP_CHANCES']['coin']:
                                        drops.append(Drop('coin', e.x, e.y))
                                    if random.random() < GAME_SETTINGS['ENEMY_DROP_CHANCES']['shield']:
                                        drops.append(Drop('shield', e.x, e.y))

                                    if e.type == 'boss':  # Don't increment for boss
                                        pass
                                    else:
                                        enemies_destroyed_in_level += 1

                                    enemies.remove(e)
                                    score += GAME_SETTINGS['SCORES'].get(e.type, 10)
                                    player.coins += GAME_SETTINGS['COIN_VALUES'].get(e.type, 5)
                                    explosions.append(Explosion(e.x, e.y, 50))
                                    if enemy_explosion_sfx: enemy_explosion_sfx.play()

                        explosions.append(Explosion(bullet.x, bullet.y, GAME_SETTINGS['BOMB_AOE'], bomb=True))
                    else:
                        enemy.health -= bullet.damage
                        if enemy.health <= 0:
                            # Handle drops for destroyed enemies
                            if random.random() < GAME_SETTINGS['ENEMY_DROP_CHANCES']['coin']:
                                drops.append(Drop('coin', enemy.x, enemy.y))
                            if random.random() < GAME_SETTINGS['ENEMY_DROP_CHANCES']['shield']:
                                drops.append(Drop('shield', enemy.x, enemy.y))

                            if enemy.type == 'boss':  # Don't increment for boss
                                pass
                            else:
                                enemies_destroyed_in_level += 1

                            enemies.remove(enemy)
                            score += GAME_SETTINGS['SCORES'].get(enemy.type, 10)
                            player.coins += GAME_SETTINGS['COIN_VALUES'].get(enemy.type, 5)
                            explosions.append(Explosion(enemy.x, enemy.y, 50))
                            if enemy_explosion_sfx: enemy_explosion_sfx.play()

                    bullets.remove(bullet)
                    break  # Bullet can only hit one enemy

        # --- Collision Detection (Enemy Bullets vs Player) ---
        for e_bullet in enemy_bullets[:]:
            if (e_bullet.x > player.x - player.width // 2 and
                    e_bullet.x < player.x + player.width // 2 and
                    e_bullet.y > player.y - player.height // 2 and
                    e_bullet.y < player.y + player.height // 2):

                if player.shield_active:
                    # Player shield absorbs damage
                    player.shield_meter -= e_bullet.damage
                    if player.shield_meter <= 0:
                        player.shield_meter = 0
                        player.shield_active = False

                else:
                    player.health -= e_bullet.damage

                explosions.append(Explosion(e_bullet.x, e_bullet.y, 20))
                enemy_bullets.remove(e_bullet)

        # --- Collision Detection (Laser vs Player) ---
        for laser in lasers[:]:
            # Check for collision with the player's bounding box and if the player hasn't been hit by this laser instance yet
            if not laser.hit_player and \
                    (player.x - player.width / 2 < laser.end_pos[0] < player.x + player.width / 2 and
                     player.y - player.height / 2 < laser.end_pos[1] < player.y + player.height / 2):

                laser.hit_player = True  # Set the flag to prevent repeated hits

                if player.shield_active:
                    # Laser drains shield
                    player.shield_meter -= GAME_SETTINGS['BOSS_LASER_SHIELD_DRAIN']
                    if player.shield_meter <= 0:
                        player.shield_meter = 0
                        player.shield_active = False
                else:
                    # Laser damages player health
                    player.health -= GAME_SETTINGS['BOSS_LASER_DAMAGE']

        # --- Collision Detection (Player vs Drops) ---
        for drop in drops[:]:
            distance = math.sqrt((player.x - drop.x) ** 2 + (player.y - drop.y) ** 2)
            if distance < player.width:
                if drop.type == 'coin':
                    player.coins += 10
                elif drop.type == 'shield':
                    player.shield_meter = min(GAME_SETTINGS['SHIELD_METER_MAX'], player.shield_meter + (
                            GAME_SETTINGS['SHIELD_METER_MAX'] * GAME_SETTINGS['SHIELD_REFILL_ON_PICKUP'] / 100))

                drops.remove(drop)
                if pickup_sfx: pickup_sfx.play()  # Play pickup sound

        # --- Cleanup, Level Progression, and Game Over ---
        bullets = [b for b in bullets if 0 < b.x < SCREEN_WIDTH and 0 < b.y < SCREEN_HEIGHT]
        enemy_bullets = [b for b in enemy_bullets if 0 < b.x < SCREEN_WIDTH and 0 < b.y < SCREEN_HEIGHT]
        lasers = [l for l in lasers if not l.done]
        laser_warnings = [w for w in laser_warnings if not w.done]

        # Remove drops and explosions that have finished
        drops = [d for d in drops if pygame.time.get_ticks() - d.spawn_time < GAME_SETTINGS['DROP_DESPAWN_TIME']]
        explosions = [exp for exp in explosions if not exp.done]

        # Enemy recycling logic and medic reward
        # Temporary list to hold enemies to be removed
        enemies_to_remove = []
        for enemy in enemies:
            # Check if enemy has gone off-screen
            if enemy.x < -enemy.width or enemy.x > SCREEN_WIDTH + enemy.width:
                if enemy.type == 'medic_helicopter':
                    player.coins += GAME_SETTINGS['COIN_VALUES']['medic_pass_by']
                    enemies_to_remove.append(enemy)
                elif enemy.type != 'boss':
                    # Recycle regular enemies
                    if enemy.x < -enemy.width:
                        enemy.x = SCREEN_WIDTH + enemy.width
                    elif enemy.x > SCREEN_WIDTH + enemy.width:
                        enemy.x = -enemy.width

        # Remove medic helicopters that have passed
        for enemy in enemies_to_remove:
            enemies.remove(enemy)

        # Level Progression (Winning condition: boss defeated)
        # Check if the boss was active and now the enemies list is empty
        if boss_active and not enemies:
            running = False  # Boss defeated, level won

        if player.health <= 0:
            running = False

        # --- Drawing ---
        if level_num == 1 and level1_bg_image:
            screen.blit(pygame.transform.scale(level1_bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        elif level_num == 2 and level2_bg_image:
            screen.blit(pygame.transform.scale(level2_bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        else:
            screen.fill(BLACK)

        player.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for e_bullet in enemy_bullets:
            e_bullet.draw(screen)
        for drop in drops:
            drop.draw(screen)

        for exp in explosions:
            exp.draw(screen)

        for laser in lasers:
            laser.draw(screen)
        for warning in laser_warnings:
            warning.draw(screen)

        # Draw HUD
        draw_text(screen, f"Score: {score}", hud_font, YELLOW, 10, 10)
        draw_text(screen, f"Coins: {player.coins}", hud_font, YELLOW, 10, 35)
        draw_text(screen, f"Level: {level}", hud_font, YELLOW, 10, 60)
        draw_text(screen, f"Health: {player.health}%", hud_font, YELLOW, 10, 85)

        # Draw Shield Meter
        shield_bar_width = 150
        shield_bar_height = 15
        shield_bar_x = 10
        shield_bar_y = 110
        pygame.draw.rect(screen, GRAY_LIGHT, (shield_bar_x, shield_bar_y, shield_bar_width, shield_bar_height),
                         border_radius=5)
        fill_width = (player.shield_meter / GAME_SETTINGS['SHIELD_METER_MAX']) * shield_bar_width
        pygame.draw.rect(screen, BLUE, (shield_bar_x, shield_bar_y, fill_width, shield_bar_height), border_radius=5)
        draw_text(screen, f"Shield: {int(player.shield_meter)}%", font, WHITE, shield_bar_x + shield_bar_width // 2,
                  shield_bar_y + shield_bar_height // 2, centered=True)

        # Draw Progress Bar
        progress_bar_width = 200
        progress_bar_height = 15
        progress_bar_x = SCREEN_WIDTH - progress_bar_width - 10
        progress_bar_y = 10
        pygame.draw.rect(screen, GRAY_LIGHT, (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height),
                         border_radius=5)
        if total_enemies_for_level > 0:
            fill_width = (enemies_destroyed_in_level / total_enemies_for_level) * progress_bar_width
            if fill_width > progress_bar_width:
                fill_width = progress_bar_width  # Don't exceed the bar length
            pygame.draw.rect(screen, GREEN, (progress_bar_x, progress_bar_y, fill_width, progress_bar_height),
                             border_radius=5)
        draw_text(screen, f"Progress: {enemies_destroyed_in_level}/{total_enemies_for_level}", font, WHITE,
                  progress_bar_x + progress_bar_width // 2, progress_bar_y + progress_bar_height // 2, centered=True)

        # Boss health bar
        if boss_active and enemies:
            boss = enemies[0]
            boss_bar_width = SCREEN_WIDTH - 20
            boss_bar_height = 20
            boss_bar_x = 10
            boss_bar_y = SCREEN_HEIGHT - 30
            pygame.draw.rect(screen, GRAY_LIGHT, (boss_bar_x, boss_bar_y, boss_bar_width, boss_bar_height))
            fill_width = (boss.health / GAME_SETTINGS[f'BOSS_HEALTH_L{level}']) * boss_bar_width
            pygame.draw.rect(screen, RED, (boss_bar_x, boss_bar_y, fill_width, boss_bar_height))
            draw_text(screen, "BOSS", font, WHITE, SCREEN_WIDTH // 2, boss_bar_y + boss_bar_height // 2, centered=True)

        pygame.display.flip()
        clock.tick(60)

    # After the loop, check if the player won or lost
    pygame.mixer.music.stop()  # Stop the level music
    if player.health <= 0:
        game_over_screen(score, player.coins, player.upgrades)
    else:
        game_over_screen(score, player.coins, player.upgrades, level_completed=level)


if __name__ == '__main__':
    main_menu()















































































