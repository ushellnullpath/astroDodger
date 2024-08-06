astroDodger is a space-themed vertical scroller game where players control a spaceship using hand gestures to dodge incoming asteroids and aim for high scores. Developed with Python, Pygame, OpenCV, and MediaPipe, astroDodger adds a unique twist to classic dodger gameplay by incorporating hand tracking for an immersive gaming experience.

When the game is first run, it has a gamertag screen where you can add your gamertag.

![Untitled0](https://github.com/user-attachments/assets/0a32bee8-bb19-48f1-bc02-7153030eb628)


In the main game, avoid asteroids, survive asteroid waves, collect shields to stay alive, and aim for a high score.

![Untitled1](https://github.com/user-attachments/assets/9018f6b3-b1ac-4c95-9dae-a0b64e94885d)

![Untitled2](https://github.com/user-attachments/assets/8b36f0c5-21aa-49a4-91e1-506aedaf28c6)


The game over screen shows your score as well as the top 5 high scores when you click the 'High Scores' button.

![Untitled3](https://github.com/user-attachments/assets/4c306917-3749-4150-b111-88be799f50b9)

![Untitled4](https://github.com/user-attachments/assets/df392802-cfd3-41c6-9596-cf281e141610)


Your scores are saved in an SQLite database every time you achieve a score. If you enter the same gamertag, it will update the score if it is higher.

![Untitled5](https://github.com/user-attachments/assets/19064609-ab3f-478f-828d-ce88eec93f7c)


## Features

- Hand Gesture Controls: Navigate your spaceship using hand movements captured by your webcam.
- Dynamic Asteroid Waves: Encounter increasingly challenging waves of asteroids as you progress.
- Power-Up System: Collect shields to protect your spaceship from damage.
- Scoring System: Compete for high scores based on survival time.

## How to Play

1. Start the game and enter your gamertag.
2. Use your hand to control the spaceship's movement
|-> (ensure your webcam is enabled and you are in a well-lit room).
3. Dodge incoming asteroids to survive.
4. Collect shield power-ups to protect your ship.
5. Survive as long as possible to achieve a high score!

## Installation

1. Ensure you have Python 3.x installed on your system.
2. Clone this repository: git clone https://github.com/ushellnullpath/astroDodger
3. Navigate to the project directory: cd astroDodger
4. Install the required dependencies: pip install -r requirements.txt
5. Execute the main game file: python main.py

## Controls

Use your hand movements in front of the webcam to control the spaceship.
The game tracks your index finger to determine the ship's position.

## Development

astroDodger was developed using:

- Python 3.x
- Pygame for game mechanics and rendering
- OpenCV and MediaPipe for hand tracking
- Tkinter for the start menu
- SQLite for saving scores

## Future Enhancements (not sure when though...)

- [ ] Implement multiple difficulty levels
- [ ] Add additional animations
- [ ] Introduce an online multiplayer mode
- [ ] Develop an online leaderboard system

- LAST UPDATED (D/M/Y): 06/08/2024

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Credits:
[Sound FX](https://kronbits.itch.io/freesfx)
[Keys FX](https://pixabay.com/sound-effects/menu-buttom-190020)
[Music](https://pixabay.com/music/video-games-waiting-time-175800)
[Font](https://www.fontspace.com/press-start-2p-font-f11591)
