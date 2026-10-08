"""
GameEngine: owns the puck, both paddles, the computer AI, scoring,
match timing, and round resets.
"""

import math
import random
import pygame

from game.puck import Puck
from game.paddle import Paddle
from game.ai import ComputerAI
from game.collisions import handle_paddle_collision
from game.renderer import WIDTH, HEIGHT, MARGIN, GOAL_TOP, GOAL_BOTTOM

PLAYER_SPEED = 6
PUCK_RADIUS = 12
PADDLE_RADIUS = 28
INITIAL_PUCK_SPEED = 4.5
MATCH_DURATION = 30.0
PUCK_SUBSTEPS = 4


class GameEngine:
    def __init__(self):
        self.puck = Puck(WIDTH / 2, HEIGHT / 2, PUCK_RADIUS)

        self.player = Paddle(
            x=WIDTH * 0.15, y=HEIGHT / 2, radius=PADDLE_RADIUS,
            min_x=MARGIN + PADDLE_RADIUS, max_x=WIDTH / 2 - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS, max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )

        self.computer = Paddle(
            x=WIDTH * 0.85, y=HEIGHT / 2, radius=PADDLE_RADIUS,
            min_x=WIDTH / 2 + PADDLE_RADIUS,
            max_x=WIDTH - MARGIN - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS,
            max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )

        self.ai = ComputerAI()

        self.player_score = 0
        self.computer_score = 0

        self.match_start_ticks = pygame.time.get_ticks()
        self.remaining_time = MATCH_DURATION
        self.match_over = False

        self._launch_puck()

    def _launch_puck(self):
        angle_choices = [0.3, 0.6, -0.3, -0.6]
        direction = random.choice([-1, 1])
        vy_factor = random.choice(angle_choices)

        self.puck.vx = INITIAL_PUCK_SPEED * direction
        self.puck.vy = INITIAL_PUCK_SPEED * vy_factor

    def handle_input(self, keys_pressed):
        if self.match_over:
            return

        dx = dy = 0

        if keys_pressed[pygame.K_UP]:
            dy -= PLAYER_SPEED
        if keys_pressed[pygame.K_DOWN]:
            dy += PLAYER_SPEED
        if keys_pressed[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT]:
            dx += PLAYER_SPEED

        self.player.move_by(dx, dy)

    def update(self):
        if self.match_over:
            return

        elapsed = (pygame.time.get_ticks() - self.match_start_ticks) / 1000.0
        self.remaining_time = max(0.0, MATCH_DURATION - elapsed)

        if self.remaining_time <= 0:
            self.remaining_time = 0.0
            self.match_over = True
            self.puck.vx = 0
            self.puck.vy = 0
            return

        self.ai.update(self.computer, self.puck)

        # Multiple smaller movement steps reduce puck tunnelling
        # through paddles at higher speeds.
        for _ in range(PUCK_SUBSTEPS):
            self.puck.move_by_scale(1 / PUCK_SUBSTEPS)
            self.puck.bounce_off_walls(HEIGHT, MARGIN)

            handle_paddle_collision(self.puck, self.player)
            handle_paddle_collision(self.puck, self.computer)

            if self._handle_goals():
                break

    def _handle_goals(self):
        # Left goal = computer scores
        if self.puck.x - self.puck.radius < MARGIN:
            if GOAL_TOP < self.puck.y < GOAL_BOTTOM:
                self.computer_score += 1
                self._reset_puck()
                return True
            else:
                self.puck.x = MARGIN + self.puck.radius
                self.puck.vx = abs(self.puck.vx)

        # Right goal = player scores
        elif self.puck.x + self.puck.radius > WIDTH - MARGIN:
            if GOAL_TOP < self.puck.y < GOAL_BOTTOM:
                self.player_score += 1
                self._reset_puck()
                return True
            else:
                self.puck.x = WIDTH - MARGIN - self.puck.radius
                self.puck.vx = -abs(self.puck.vx)

        return False

    def _reset_puck(self):
        self.puck.x = WIDTH / 2
        self.puck.y = HEIGHT / 2
        self._launch_puck()

    def _result_text(self):
        if self.player_score > self.computer_score:
            return "You Win!"

        if self.computer_score > self.player_score:
            return "Computer Wins!"

        return "Draw"

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_table(surface)

        renderer.draw_paddle(
            surface,
            self.player,
            renderer.COLOR_PLAYER
        )

        renderer.draw_paddle(
            surface,
            self.computer,
            renderer.COLOR_COMPUTER
        )

        renderer.draw_puck(surface, self.puck)

        renderer.draw_text(
            surface,
            font,
            f"You: {self.player_score}",
            (35, 28)
        )

        renderer.draw_text(
            surface,
            font,
            f"Computer: {self.computer_score}",
            (WIDTH - 185, 28)
        )

        time_left = math.ceil(self.remaining_time)

        renderer.draw_text(
            surface,
            font,
            f"Time: {time_left}s",
            (WIDTH // 2 - 50, 28)
        )

        if self.match_over:
            renderer.draw_banner(
                surface,
                font,
                f"{self._result_text()}  "
                f"{self.player_score}-{self.computer_score}"
            )