import pygame
import random
from os.path import join
from game_functions import cycle_player_imgs, load_and_scale_imgs


class Player(pygame.sprite.Sprite):
    """
    The player (spaceship) in the game. Handles its movement, animation, health, shields, and explosions.
    """

    def __init__(self, groups, screen_width, screen_height, image_dict, game):
        super().__init__(groups)
        self.game = game
        self.images = image_dict['spaceship']
        self.idle_image_index = 0
        self.image = self.images[self.idle_image_index]
        self.rect = self.image.get_frect(
            center=(screen_width / 2, screen_height / 2))
        self.mask = pygame.mask.from_surface(self.image)

        # Movement and animation attributes
        self.is_moving = False
        self.animation_speed = 0.2
        self.animation_timer = 0
        self.movement_threshold = 3
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x, self.y = self.rect.center

        # Health and shield attributes
        self.max_health = 100
        self.health = self.max_health
        self.max_shield = 100
        self.shield = 0
        self.temp_shield_timer = 0
        self.temp_shield_duration = 5
        self.has_permanent_shield = False

        # Explosion attributes
        self.explosion_images = image_dict['explosions']
        self.explosion_index = 0
        self.is_exploding = False
        self.explosion_timer = 0
        self.explosion_speed = 0.1

    def update(self):
        """Update the player's state each frame."""
        if self.is_exploding:
            self.explode()
        else:
            self.move_player(self.x, self.y)
            self.update_shield()

    def move_player(self, x, y):
        """
        Move the player to the specified position, respecting screen boundaries.
        Also handles player animation based on movement.
        """
        # Clamp the position within screen boundaries
        new_x = max(self.rect.width // 2,
                    min(x, self.screen_width - self.rect.width // 2))
        new_y = max(self.rect.height // 2,
                    min(y, self.screen_height - self.rect.height // 2))

        # Check if the player is moving significantly
        dx = new_x - self.rect.centerx
        dy = new_y - self.rect.centery
        self.is_moving = abs(dx) > self.movement_threshold or abs(
            dy) > self.movement_threshold

        if self.is_moving:
            self.rect.center = (new_x, new_y)
            self.animation_timer += self.game.dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.idle_image_index, self.image = cycle_player_imgs(
                    self.idle_image_index, self.images[1:])
                self.mask = pygame.mask.from_surface(self.image)
        else:
            self.idle_image_index = 0
            self.image = self.images[0]
            self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self, amount):
        """Apply damage to the player, considers shields first."""
        if self.shield > 0:
            self.shield = max(0, self.shield - amount)
            if self.shield == 0 and self.has_permanent_shield:
                self.has_permanent_shield = False
        else:
            self.health = max(0, self.health - amount)

    def update_shield(self):
        """Update the shield status, handling temporary shield decay."""
        if not self.has_permanent_shield and self.temp_shield_timer > 0:
            self.temp_shield_timer -= self.game.dt
            self.shield = max(
                0, self.shield - (self.max_shield / self.temp_shield_duration * self.game.dt))
            if self.temp_shield_timer <= 0:
                self.shield = 0

    def add_shield(self, shield_type):
        """Add a shield to the player based on the shield type."""
        if shield_type == 1:
            if self.has_permanent_shield:
                self.shield = min(self.max_shield, self.shield + 10)
            else:
                self.shield = self.max_shield
                self.temp_shield_timer = self.temp_shield_duration
                self.has_permanent_shield = False
        elif shield_type == 2:
            self.shield = self.max_shield
            self.temp_shield_timer = 0
            self.has_permanent_shield = True

    def explode(self):
        """Handle the player's explosion animation."""
        self.explosion_timer += self.game.dt
        if self.explosion_timer >= self.explosion_speed:
            self.explosion_timer = 0
            if self.explosion_index < len(self.explosion_images):
                self.image = self.explosion_images[self.explosion_index]
                self.explosion_index += 1
            else:
                self.kill()

    def start_explosion(self):
        """Initiate the explosion sequence."""
        self.is_exploding = True
        self.explosion_index = 0
        self.game.sounds['explosion'].play()
        self.game.explosions.add(self)

    def is_explosion_complete(self):
        """Check if the explosion animation is complete."""
        return self.is_exploding and self.explosion_index >= len(self.explosion_images)


class Asteroid(pygame.sprite.Sprite):
    """
    Asteroid in the game. Handles its movement, rotation, and collision detection.
    """

    def __init__(self, groups, pos, image_dict, game, speed_range=(100, 500)):
        super().__init__(groups)
        self.game = game
        self.type = random.choice(['L', 'M', 'S'])
        self.original_image = image_dict['asteroids'][[
            'L', 'M', 'S'].index(self.type)]
        self.image = self.original_image
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(
            random.uniform(-0.5, 0.5), 1).normalize()
        self.speed = random.uniform(*speed_range)

        self.rotation = 0
        self.rotation_speed = random.randint(20, 50)

    def update(self):
        """Update the asteroid's position and rotation."""
        self.pos += self.direction * self.speed * self.game.dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.rotate()

        if self.rect.top > self.game.screen.get_height():
            self.kill()

    def rotate(self):
        """Rotate the asteroid image."""
        self.rotation = (
            self.rotation + self.rotation_speed * self.game.dt) % 360
        self.image = pygame.transform.rotate(
            self.original_image, self.rotation)
        self.rect = self.image.get_frect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def check_collision(self, player):
        """Check for collision with the player using mask collision."""
        return pygame.sprite.collide_mask(self, player)


class Shield(pygame.sprite.Sprite):
    """
    Shield powerup(s) in the game. Handles its movement and collision detection.
    """

    def __init__(self, groups, pos, image_dict, game, shield_type):
        super().__init__(groups)
        self.game = game
        self.shield_type = shield_type
        self.image = image_dict['shields'][shield_type - 1]
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(
            random.uniform(-0.5, 0.5), 1).normalize()
        self.speed = random.uniform(50, 150)

    def update(self):
        """Update the shield's position."""
        self.pos += self.direction * self.speed * self.game.dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        if self.rect.top > self.game.SCREEN_HEIGHT:
            self.kill()

    def check_collision(self, player):
        """Check for collision with the player using mask collision."""
        return pygame.sprite.collide_mask(self, player)


class UI:
    """
    Handles the game's user interface elements by managing the health bar, shield bar, and score display.
    """

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_font = pygame.font.Font(join('font', 'PressStart2P.ttf'))

        scale_factor = 1.3

        # Load and position UI elements
        self.ui_slot = load_and_scale_imgs(
            join('images', 'ui_Slots.png'), scale_factor)
        self.ui_slot_pos = (15, 15)
        self.ui_slot_rect = self.ui_slot.get_frect(topleft=self.ui_slot_pos)

        self.full_health_bar = load_and_scale_imgs(
            join('images', 'ui_Health.png'), scale_factor)
        self.ui_health = self.full_health_bar.copy()
        ui_health_offset_x, ui_health_offset_y = 47, 10
        self.health_rect = self.ui_health.get_frect(
            topleft=(self.ui_slot_rect.left + ui_health_offset_x,
                     self.ui_slot_rect.top + ui_health_offset_y))

        self.health_bar_original_width = self.health_rect.width

        self.full_shield_bar = load_and_scale_imgs(
            join('images', 'ui_Shield.png'), scale_factor)
        self.ui_shield = self.full_shield_bar.copy()
        ui_shield_offset_x, ui_shield_offset_y = 47, 42
        self.shield_rect = self.ui_health.get_frect(
            topleft=(self.ui_slot_rect.left + ui_shield_offset_x,
                     self.ui_slot_rect.top + ui_shield_offset_y))

        self.shield_bar_original_width = self.shield_rect.width

        self.show_ui = False

        self.score = 0
        self.score_text = self.game_font.render(
            'SCORE:0', True, (255, 255, 255))

    def update_score(self, score):
        """Update the score display."""
        if score != self.score:
            self.score = score
            self.score_text = self.game_font.render(
                f'SCORE:{score}', True, (255, 255, 255))

    def update_health_bar(self, player_health):
        """Update the health bar display based on player's current health."""
        health_percentage = player_health / 100
        new_width = int(self.health_bar_original_width * health_percentage)
        self.ui_health = pygame.Surface(self.full_health_bar.get_size())
        self.ui_health.blit(self.full_health_bar, (0, 0),
                            (0, 0, new_width, self.full_health_bar.get_height()))

    def update_shield_bar(self, player_shield):
        """Update the shield bar display based on player's current shield."""
        shield_percentage = player_shield / 100
        new_width = int(self.shield_bar_original_width * shield_percentage)
        self.ui_shield = pygame.Surface(self.full_shield_bar.get_size())
        self.ui_shield.blit(self.full_shield_bar, (0, 0),
                            (0, 0, new_width, self.full_shield_bar.get_height()))

    def draw(self, screen):
        """Draw the UI elements on the screen."""
        if self.show_ui:
            screen.blit(self.ui_slot, self.ui_slot_rect)
            screen.blit(self.ui_health, self.health_rect)
            screen.blit(self.ui_shield, self.shield_rect)

            self.score_rect = self.score_text.get_frect()
            self.score_rect.topright = (self.screen_width - 20, 20)
            screen.blit(self.score_text, self.score_rect)


class GameState:
    """Different game states."""
    LOADING = 0
    PLAYING = 1
    GAME_OVER = 2
