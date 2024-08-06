import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

import mediapipe as mp
import pygame
import sys
from os.path import join
from pygame import mixer
from game_functions import *
from game_classes import *
import random
import time
import cv2


class Game:
    """
    Main game class that handles the game loop, initialization, and overall game logic of the game 'astroDodger'.
    """
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    MAX_FPS = 60

    def __init__(self):
        """Initialize the game, set up display, load resources, and initialize main game's objects."""
        # Initialize Pygame and mixer
        pygame.mixer.pre_init(44100, -16, 2, 512)
        mixer.init()
        pygame.init()

        # Set up the game window
        self.icon = pygame.image.load(join('images', 'favicon1.ico'))
        pygame.display.set_icon(self.icon)
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("astroDodger by ushellnullpath")

        # Set up game clock and cursor
        self.clock = pygame.time.Clock()
        self.cursor_img = load_custom_cursor(join('images', 'cursor.png'))
        self.show_cursor = False

        # Load background image
        self.bg = pygame.image.load(join('images', 'background.jpg')).convert()
        self.bg_height = self.bg.get_height()

        # Load game resources
        self.image_dict = load_images()
        self.sounds = load_sounds()
        self.set_sound_volumes()

        # Initialize main game variables and objects
        self.init_game_variables()
        self.init_game_objects()

    def set_sound_volumes(self):
        """Set the volume levels for various game sounds."""
        self.sounds['bg_track'].set_volume(0.06)
        self.sounds['asteroid_impact'].set_volume(0.2)
        self.sounds['shield_pickUp'].set_volume(0.2)
        self.sounds['alert'].set_volume(0.2)
        self.sounds['explosion'].set_volume(0.4)

    def init_game_variables(self):
        """Initializes various game variables."""
        # Scrolling background variables
        self.scroll = 0
        self.scroll_speed = 100

        # Game progression variables
        self.score = 0
        self.game_start_time = None
        self.loading_complete = False

        # Wave system variables
        self.last_wave_time = None
        self.wave_number = 0
        self.wave_interval = 30
        self.initial_wave_duration = 30
        self.wave_duration_increment = random.randint(10, 20)
        self.wave_duration = self.initial_wave_duration
        self.wave_active = False

        # Game state variables
        self.dt = 0
        self.game_state = GameState.LOADING
        self.explosion_in_progress = False
        self.gamertag = None

        # Alert system variables
        self.alert_text = ""
        self.alert_timer = 0
        self.alert_duration = 3

        # Shield spawn variables
        self.shield1_count = 0
        self.shield2_spawned = False

    def init_game_objects(self):
        """Initializes game objects including sprites and UI elements."""
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shields = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()

        # Create player
        self.player = Player(self.all_sprites, self.SCREEN_WIDTH,
                             self.SCREEN_HEIGHT, self.image_dict, self)
        self.player.rect.midbottom = (
            self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT + self.player.rect.height // 2)

        # Create UI
        self.ui = UI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.game_font = self.ui.game_font

    def create_asteroid(self):
        """Creates and returns a new asteroid object."""
        x = random.randint(0, self.SCREEN_WIDTH)
        y = -50
        new_asteroid = Asteroid(
            [self.all_sprites, self.asteroids], (x, y), self.image_dict, self)
        return new_asteroid

    def create_shield(self, shield_type):
        """Creates and returns a new shield object of the specified type."""
        x = random.randint(0, self.SCREEN_WIDTH)
        y = -50
        new_shield = Shield([self.all_sprites, self.shields],
                            (x, y), self.image_dict, self, shield_type)
        return new_shield

    def spawn_shields(self):
        """Spawns shields during active waves based on probability."""
        if self.wave_active:
            # Spawn Shield 1 (max 3 per wave)
            if self.shield1_count < 3 and random.random() < 0.005:
                self.create_shield(1)
                self.shield1_count += 1

            # Spawn Shield 2 (only once per wave)
            if not self.shield2_spawned and random.random() < 0.002:
                self.create_shield(2)
                self.shield2_spawned = True

    def handle_shield_collisions(self):
        """Checks for collisions between the player and shields, and apply shield effects."""
        collided_shields = pygame.sprite.spritecollide(
            self.player, self.shields, True, pygame.sprite.collide_mask)
        for shield in collided_shields:
            self.player.add_shield(shield.shield_type)
            self.sounds['shield_pickUp'].play()

    def show_alert(self, text):
        """Displays an alert message on the screen for when the asteroid waves start and end."""
        self.alert_text = text
        self.alert_timer = self.alert_duration

    def update_asteroids(self):
        """Updates asteroid-related game logic, including wave system and collisions."""
        if self.game_state != GameState.PLAYING or self.player.is_exploding:
            return

        current_time = time.time()
        time_since_start = current_time - self.game_start_time

        self.handle_wave_logic(current_time, time_since_start)
        self.spawn_asteroids()
        self.handle_collisions()

    def handle_wave_logic(self, current_time, time_since_start):
        """
        Manages the wave logic of the game.
        """
        if not self.wave_active and time_since_start >= self.wave_interval and current_time - self.last_wave_time >= self.wave_interval:
            self.start_new_wave(current_time)
        elif self.wave_active and current_time - self.last_wave_time >= self.wave_duration:
            self.end_wave(current_time)

    def start_new_wave(self, current_time):
        """
        Initializes a new wave of asteroids.
        """
        self.shield1_count = 0
        self.shield2_spawned = False
        self.wave_active = True
        self.last_wave_time = current_time
        self.wave_number += 1
        self.wave_duration = self.initial_wave_duration + \
            (self.wave_number - 1) * self.wave_duration_increment
        self.show_alert("wave incoming!")
        self.sounds['alert'].play(loops=2)

    def end_wave(self, current_time):
        """
        Ends the current wave.
        """
        self.wave_active = False
        self.last_wave_time = current_time
        self.show_alert("wave has ended!")

    def spawn_asteroids(self):
        """
        Handles the spawning of asteroids based on game state.
        """
        # Set base spawn rate depending on whether a wave is active
        base_spawn_rate = 5 if self.wave_active else 1.3  # Spawns per second
        spawn_chance = base_spawn_rate * self.dt

        # Randomly decide whether to spawn an asteroid
        if random.random() < spawn_chance:
            self.create_asteroid()

    def handle_collisions(self):
        """
        Handles collisions between the player and asteroids.
        """
        if not self.player.is_exploding:
            # Check for collisions between player and asteroids
            collided_asteroids = pygame.sprite.spritecollide(
                self.player, self.asteroids, False, pygame.sprite.collide_mask)

            for asteroid in collided_asteroids:
                self.sounds['asteroid_impact'].play()
                # Determine damage based on asteroid size
                damage = 2 if asteroid.type == 'S' else 4 if asteroid.type == 'M' else 6
                self.player.take_damage(damage)
                asteroid.kill()

        # Start player explosion if health reaches zero
        if self.player.health <= 0 and not self.player.is_exploding:
            self.player.start_explosion()
            self.explosion_in_progress = True

    def are_all_elements_cleared(self):
        """
        Checks if all game elements (player, asteroids, shields) are cleared.
        """
        return (self.player.is_explosion_complete() and
                len(self.asteroids) == 0 and
                len(self.shields) == 0)

    def game_over(self):
        """
        Handles the game over state and cleanup.
        """
        self.game_state = GameState.GAME_OVER

        # Release webcam if it exists
        if hasattr(self, 'webcam'):
            self.webcam.release()

        # Show game over screen and handle replay option
        play_again = game_over_screen(
            self, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.sounds['input'], self.game_font
        )

        if play_again:
            self.all_sprites.empty()
            self.asteroids.empty()
            self.shields.empty()
            self.explosions.empty()

            # Reset game variables
            self.init_game_variables()
            self.init_game_objects()

            # Restart the game
            self.start()
        else:
            self.cleanup_and_exit()

    def start(self):
        """
        Initializes and starts the game, including the main game loop.
        """
        # Show cursor for gamertag input
        self.show_cursor = True
        self.gamertag = gamertag_screen(
            self, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.sounds['input'], self.game_font)
        if self.gamertag is None:
            self.cleanup_and_exit()
            return

        # Hide cursor for gameplay
        self.show_cursor = False
        pygame.mouse.set_visible(False)

        # Show loading screen
        self.loading_complete = False
        loading_screen(self, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        # Initialize hand tracking
        if not self.init_hand_tracking():
            print("ERROR: Failed to initialize hand tracking. Exiting game.")
            self.cleanup_and_exit()
            return

        # Set initial game state
        self.game_start_time = time.time()
        self.last_wave_time = self.game_start_time
        self.game_state = GameState.PLAYING
        self.ui.show_ui = True

        # Main game loop
        while self.game_state != GameState.GAME_OVER:
            self.dt = self.clock.tick() / 1000.0
            self.update_hand_position()
            self.update_game_elements()

            # Handle quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = GameState.GAME_OVER

            pygame.display.update()

        self.game_over()

    def init_hand_tracking(self):
        """
        Initializes hand tracking using OpenCV and MediaPipe.
        """
        # Set up webcam
        self.webcam = cv2.VideoCapture(0)
        if not self.webcam.isOpened():
            print("ERROR: Could not open webcam.")
            return False

        # Set webcam resolution
        TRACKING_WIDTH, TRACKING_HEIGHT = 320, 240
        self.webcam.set(3, TRACKING_WIDTH)
        self.webcam.set(4, TRACKING_HEIGHT)

        # Initialize MediaPipe hand tracking
        self.hand_model = mp.solutions.hands
        self.hand = self.hand_model.Hands(
            min_tracking_confidence=0.3, min_detection_confidence=0.3, max_num_hands=1)

        # Initialize hand tracking variables
        self.last_hand_update_time = 0
        self.hand_update_interval = 1 / self.MAX_FPS
        self.smoothing_factor = 0.1
        self.prediction_factor = 0.5
        self.prev_x, self.prev_y = self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2
        self.velocity_x, self.velocity_y = 0, 0
        self.velocity_decay = 0.5

        return True

    def update_hand_position(self):
        """
        Updates the hand position using webcam input and hand tracking.
        """
        self.last_hand_update_time += self.dt
        if self.last_hand_update_time >= self.hand_update_interval:
            control, frame = self.webcam.read()
            if control:
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = self.hand.process(rgb)

                if result.multi_hand_landmarks:
                    for handLandmark in result.multi_hand_landmarks:
                        # Get index finger tip position
                        index_finger_tip = handLandmark.landmark[8]
                        new_x = int(index_finger_tip.x * self.SCREEN_WIDTH)
                        new_y = int(index_finger_tip.y * self.SCREEN_HEIGHT)

                        # Calculate velocity
                        dx = new_x - self.prev_x
                        dy = new_y - self.prev_y

                        # Apply velocity decay
                        self.velocity_x = self.velocity_x * \
                            self.velocity_decay + dx * \
                            (1 - self.velocity_decay)
                        self.velocity_y = self.velocity_y * \
                            self.velocity_decay + dy * \
                            (1 - self.velocity_decay)

                        # Predict future position
                        predicted_x = new_x + self.prediction_factor * self.velocity_x
                        predicted_y = new_y + self.prediction_factor * self.velocity_y

                        # Apply smoothing
                        x = int(self.smoothing_factor * predicted_x +
                                (1 - self.smoothing_factor) * self.prev_x)
                        y = int(self.smoothing_factor * predicted_y +
                                (1 - self.smoothing_factor) * self.prev_y)

                        self.prev_x, self.prev_y = x, y

    def update_game_elements(self):
        """
        Updates all game elements and draws them on the screen.
        """
        self.draw_background()
        self.play_background_music()

        # Update player position if not exploding
        if not self.player.is_exploding:
            self.player.x, self.player.y = self.prev_x, self.prev_y

        if self.game_state == GameState.PLAYING:
            if not self.explosion_in_progress:
                self.update_asteroids()
                self.spawn_shields()
                self.handle_shield_collisions()
                self.update_score()
            if self.explosion_in_progress and self.are_all_elements_cleared():
                self.game_over()
                return

        # Update and draw all sprites
        self.all_sprites.update()
        for sprite in self.all_sprites:
            if sprite not in self.explosions:
                self.screen.blit(sprite.image, sprite.rect)

        # Draw explosion sprites on top
        self.explosions.draw(self.screen)

        self.update_ui()
        self.handle_alert()

        pygame.display.flip()

    def draw_background(self):
        """
        Draws the scrolling background.
        """
        self.screen.blit(self.bg, (0, self.scroll))
        self.screen.blit(self.bg, (0, self.scroll - self.bg_height))
        self.scroll += self.scroll_speed * self.dt
        if self.scroll >= self.bg_height:
            self.scroll = 0

    def play_background_music(self):
        """
        Plays background music if it's not already playing.
        """
        if not pygame.mixer.get_busy():
            self.sounds['bg_track'].play(loops=-1, fade_ms=800)

    def update_score(self):
        """
        Updates the player's score based on survival time.
        """
        if self.game_start_time is not None:
            current_time = time.time()
            self.score = int(current_time - self.game_start_time)

    def update_ui(self):
        """
        Updates and draw the user interface elements.
        """
        self.ui.update_score(self.score)
        self.ui.update_health_bar(self.player.health)
        self.ui.update_shield_bar(self.player.shield)
        self.ui.draw(self.screen)

    def handle_alert(self):
        """
        Handles the display of alert messages.
        """
        if self.alert_timer > 0:
            self.alert_timer -= self.dt
            if self.alert_timer <= 0:
                self.alert_text = ""
            else:
                if (self.alert_timer * 2) % 2 > 1:
                    self.draw_alert_text()

    def draw_alert_text(self):
        """
        Draws the alert text with a black border.
        """
        font = self.game_font
        text_surface = font.render(self.alert_text, True, (255, 255, 255))
        text_rect = text_surface.get_frect(
            center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))

        # Draw black border
        for dx, dy in [(-3, -3), (-3, 0), (-3, 3), (0, -3), (0, 3), (3, -3), (3, 0), (3, 3)]:
            border_rect = text_rect.move(dx, dy)
            border_surface = font.render(self.alert_text, True, (0, 0, 0))
            self.screen.blit(border_surface, border_rect)

        # Draw white text
        self.screen.blit(text_surface, text_rect)

    def cleanup_and_exit(self):
        """
        Performs thorough cleanup operations and exits the game.
        """
        # Stop all sounds
        pygame.mixer.stop()

        # Clear all sprite groups
        self.all_sprites.empty()
        self.asteroids.empty()
        self.shields.empty()
        self.explosions.empty()

        # Release webcam if it exists
        if hasattr(self, 'webcam'):
            self.webcam.release()

        cv2.destroyAllWindows()
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()