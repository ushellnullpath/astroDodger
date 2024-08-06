import pygame
import time
import sqlite3
from datetime import datetime
import os
from os.path import join


def load_images():
    """
    Returns a dictionary of the game's images.
    """
    return {
        'spaceship': [pygame.image.load(join('images', 'spaceship', f'spaceship_{state}.png')).convert_alpha() for state in ['Idle', 'Flying_1', 'Flying_2', 'Flying_3']],
        'asteroids': [pygame.image.load(join('images', 'asteroids', f'asteroid_{size}.png')).convert_alpha() for size in ['L', 'M', 'S']],
        'shields': [pygame.image.load(join('images', f'sp_Shield{i}.png')).convert_alpha() for i in range(1, 3)],
        'explosions': [pygame.image.load(join('images', 'explosion', f'sp_Explosion_{i}.png')).convert_alpha() for i in range(1, 10)]
    }


def load_sounds():
    """
    Returns a dictionary of the game's sounds.
    """
    return {
        'bg_track': pygame.mixer.Sound(join('sounds', 'Waiting Time.wav')),
        'input': pygame.mixer.Sound(join('sounds', 'Inputs.wav')),
        'asteroid_impact': pygame.mixer.Sound(join('sounds', 'Retro Impact 20.wav')),
        'shield_pickUp': pygame.mixer.Sound(join('sounds', 'Retro PickUp 18.wav')),
        'alert': pygame.mixer.Sound(join('sounds', 'Warning.wav')),
        'explosion': pygame.mixer.Sound(join('sounds', 'Retro Explosion Short 15.wav'))
    }


def load_and_scale_imgs(filepath, scale_factor):
    """
    Loads an image from a file and scales it by the given factor.
    """
    original = pygame.image.load(filepath).convert_alpha()
    new_size = (int(original.get_width() * scale_factor),
                int(original.get_height() * scale_factor))
    return pygame.transform.scale(original, new_size)


def cycle_player_imgs(current_index, images):
    """
    Cycles through player images to create animation effect.
    """
    new_index = (current_index + 1) % len(images)
    return new_index, images[new_index]


def load_custom_cursor(filepath, scale_factor=1):
    """
    Loads and scales a custom cursor image.
    """
    cursor_img = pygame.image.load(filepath).convert_alpha()
    cursor_img = pygame.transform.scale(cursor_img,
                                        (int(cursor_img.get_width() * scale_factor),
                                         int(cursor_img.get_height() * scale_factor)))
    return cursor_img


def draw_custom_cursor(screen, cursor_img):
    """
    Draws the custom cursor at the current mouse position.
    """
    mouse_pos = pygame.mouse.get_pos()
    screen.blit(cursor_img, mouse_pos)


def gamertag_screen(game, screen_width, screen_height, input_sound, game_font):
    """
    Displays the gamertag input screen and handle user input.
    """
    pygame.mouse.set_visible(False)
    input_box = pygame.Rect(screen_width // 2 - 150,
                            screen_height // 2 - 20, 300, 40)
    color = pygame.Color('white')
    text = ''
    done = False
    instruction = 'PRESS "ENTER" TO CONFIRM'
    MAX_CHARS = 14

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                # Play sound for all key presses
                input_sound.play()
                if event.key == pygame.K_RETURN:
                    if text:
                        done = True
                    else:
                        instruction = 'PLEASE ENTER A "GAMERTAG" TO CONTINUE'
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                    instruction = 'PRESS "ENTER" TO CONFIRM'
                else:
                    if len(text) < MAX_CHARS:
                        text += event.unicode
                        instruction = 'PRESS "ENTER" TO CONFIRM'
                    else:
                        instruction = f'MAX {MAX_CHARS} CHARACTERS ALLOWED'

        # Draw background
        game.screen.blit(game.bg, (0, 0))

        # Render the prompt
        prompt_text = game_font.render(
            "Enter your gamertag:", True, (255, 255, 255))
        prompt_rect = prompt_text.get_rect(
            center=(screen_width // 2, screen_height // 2 - 50))
        game.screen.blit(prompt_text, prompt_rect)

        # Render the rounded input box
        pygame.draw.rect(game.screen, color, input_box, border_radius=10)

        # Render and center the text in the input box
        txt_surface = game_font.render(text, True, (0, 0, 0))
        txt_rect = txt_surface.get_rect(center=input_box.center)
        game.screen.blit(txt_surface, txt_rect)

        # Render the instruction
        instruction_text = game_font.render(instruction, True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(
            center=(screen_width // 2, screen_height // 2 + 50))
        game.screen.blit(instruction_text, instruction_rect)

        # Draw custom cursor
        draw_custom_cursor(game.screen, game.cursor_img)
        pygame.display.flip()

    pygame.mouse.set_visible(True)
    return text


def loading_screen(game, screen_width, screen_height):
    """
    Displays a loading screen (currently a placeholder screen) with a progress bar.
    """
    loading_text_base = "Loading"
    dot_update_timer = 0
    loading_dots = 0
    last_update_time = time.time()

    # Define progress bar properties
    progress = 0
    progress_bar_width = 400
    progress_bar_height = 20
    progress_bar_rect = pygame.Rect(
        (screen_width - progress_bar_width) // 2,
        screen_height // 2,
        progress_bar_width,
        progress_bar_height
    )

    # Simulate loading steps
    loading_steps = [
        ("Loading images", 0.3),
        ("Loading sounds", 0.2),
        ("Initializing game objects", 0.2),
        ("Preparing game environment", 0.3)
    ]
    current_step = 0

    while not game.loading_complete:
        current_time = time.time()
        dt = game.dt if game.dt > 0 else current_time - last_update_time
        last_update_time = current_time

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Update dot animation
        dot_update_timer += dt
        if dot_update_timer > 0.5:
            loading_dots = (loading_dots + 1) % 4
            dot_update_timer = 0

        # Update progress
        if current_step < len(loading_steps):
            step_text, step_duration = loading_steps[current_step]
            progress += dt / step_duration
            if progress >= 1:
                progress = 0
                current_step += 1

        # Render loading screen
        game.screen.blit(game.bg, (0, 0))

        # Render current step text
        if current_step < len(loading_steps):
            step_text = loading_steps[current_step][0]
            step_surface = game.game_font.render(
                step_text, True, (255, 255, 255))
            step_rect = step_surface.get_rect(
                center=(screen_width // 2, screen_height // 2 - 50))
            game.screen.blit(step_surface, step_rect)

        # Render progress bar
        pygame.draw.rect(game.screen, (100, 100, 100), progress_bar_rect)
        progress_width = int((current_step + progress) /
                             len(loading_steps) * progress_bar_width)
        pygame.draw.rect(game.screen, (255, 255, 255),
                         (progress_bar_rect.left, progress_bar_rect.top,
                          progress_width, progress_bar_rect.height))

        # Render loading text with animated dots
        loading_text = f"{loading_text_base}{'.' * loading_dots}"
        loading_surface = game.game_font.render(
            loading_text, True, (255, 255, 255))
        loading_rect = loading_surface.get_rect(
            midtop=(screen_width // 2, progress_bar_rect.bottom + 20))
        game.screen.blit(loading_surface, loading_rect)

        # Draw custom cursor if enabled
        if game.show_cursor:
            draw_custom_cursor(game.screen, game.cursor_img)

        pygame.display.flip()

        # Check if loading is complete
        if current_step == len(loading_steps):
            game.loading_complete = True

    # Ensure the progress bar is fully filled at the end
    game.screen.blit(game.bg, (0, 0))
    pygame.draw.rect(game.screen, (100, 100, 100), progress_bar_rect)
    pygame.draw.rect(game.screen, (255, 255, 255), progress_bar_rect)
    loading_text = f"{loading_text_base}{'.' * loading_dots}"
    loading_surface = game.game_font.render(
        loading_text, True, (255, 255, 255))
    loading_rect = loading_surface.get_rect(
        midtop=(screen_width // 2, progress_bar_rect.bottom + 20))
    game.screen.blit(loading_surface, loading_rect)
    pygame.display.flip()


def game_over_screen(game, screen_width, screen_height, input_sound, game_font):
    """
    Displays the game over screen with high scores and play again option to the user.
    """
    pygame.mouse.set_visible(False)
    done = False
    blink_timer = 0
    blink_interval = 3
    show_message = True
    high_score_hover = False
    show_top_scores = False
    high_score_clicked = False

    # Ensure high scores directory exists
    folder_path = 'high_scores'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Set up SQLite database
    db_path = os.path.join(folder_path, 'high_scores.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS high_scores
                      (gamertag TEXT PRIMARY KEY, score INTEGER, timestamp TEXT)''')
    conn.commit()

    def save_local_high_score(gamertag, score):
        """Save or update the player's high score in the local database."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''INSERT INTO high_scores (gamertag, score, timestamp) 
                          VALUES (?, ?, ?)
                          ON CONFLICT(gamertag) 
                          DO UPDATE SET score = MAX(score, excluded.score),
                                        timestamp = CASE 
                                            WHEN score < excluded.score THEN excluded.timestamp
                                            ELSE timestamp
                                        END''',
                       (gamertag, score, timestamp))
        conn.commit()

    def get_top_5_high_scores():
        """Retrieve the top 5 high scores from the local database."""
        cursor.execute(
            "SELECT gamertag, score, timestamp FROM high_scores ORDER BY score DESC LIMIT 5")
        return cursor.fetchall()

    # Automatically save the current score locally
    save_local_high_score(game.gamertag, game.score)

    while not done:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                input_sound.play()
                if event.key == pygame.K_SPACE:
                    done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if high_score_hover and not high_score_clicked:
                    show_top_scores = True
                    high_score_clicked = True

        # Draw background
        game.screen.blit(game.bg, (0, 0))

        # Display player's score
        score_text = game_font.render(
            f"YOUR SCORE:{game.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(topleft=(20, 20))
        game.screen.blit(score_text, score_rect)

        # Display high scores button
        high_score_text = game_font.render(
            "HIGH SCORES", True, (255, 255, 255))
        high_score_rect = high_score_text.get_rect(
            topright=(screen_width - 20, 20))

        high_score_hover = high_score_rect.collidepoint(mouse_pos)

        # Add hover effect to high scores button
        if high_score_hover and not high_score_clicked:
            for dx, dy in [(-3, -3), (-3, 0), (-3, 3), (0, -3), (0, 3), (3, -3), (3, 0), (3, 3)]:
                border_rect = high_score_rect.move(dx, dy)
                border_surface = game_font.render(
                    "HIGH SCORES", True, (0, 0, 0))
                game.screen.blit(border_surface, border_rect)
        game.screen.blit(high_score_text, high_score_rect)

        if show_top_scores:
            # Display top 5 high scores
            top_scores = get_top_5_high_scores()
            title_text = game_font.render(
                "TOP 5 HIGH SCORES OF ALL TIME", True, (255, 255, 255))
            title_rect = title_text.get_rect(
                center=(screen_width // 2, screen_height // 2 - 100))
            game.screen.blit(title_text, title_rect)

            for i, (gamertag, score, timestamp) in enumerate(top_scores):
                score_text = game_font.render(
                    f"{i+1}. {gamertag}: {score} ({timestamp})", True, (255, 255, 255))
                score_rect = score_text.get_rect(
                    center=(screen_width // 2, screen_height // 2 - 50 + i * 30))
                game.screen.blit(score_text, score_rect)
        else:
            # Display "GAME OVER" text
            game_over_text = game_font.render(
                "GAME OVER", True, (255, 255, 255))
            game_over_rect = game_over_text.get_rect(
                center=(screen_width // 2, screen_height // 2))
            game.screen.blit(game_over_text, game_over_rect)

        # Blinking "PRESS SPACEBAR TO PLAY" message
        blink_timer += game.dt
        if blink_timer > blink_interval:
            blink_timer = 0
            show_message = not show_message
        if show_message:
            instruction_text = game_font.render(
                'PRESS "SPACEBAR" TO PLAY', True, (255, 255, 255))
            instruction_rect = instruction_text.get_rect(
                midbottom=(screen_width // 2, screen_height - 20))
            # Add shadow effect to the text
            for dx, dy in [(-3, -3), (-3, 0), (-3, 3), (0, -3), (0, 3), (3, -3), (3, 0), (3, 3)]:
                border_rect = instruction_rect.move(dx, dy)
                border_surface = game_font.render(
                    'PRESS "SPACEBAR" TO PLAY', True, (0, 0, 0))
                game.screen.blit(border_surface, border_rect)
            game.screen.blit(instruction_text, instruction_rect)

        # Draw custom cursor
        draw_custom_cursor(game.screen, game.cursor_img)
        pygame.display.flip()

    pygame.mouse.set_visible(True)
    conn.close()
    return True
