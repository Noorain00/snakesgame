import pygame
import sys
import random
import os
import math
import json
from enum import Enum
from typing import List, Tuple, Optional

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    SETTINGS = "settings"

class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Constants
        self.CELL_SIZE = 25
        self.MIN_WIDTH, self.MIN_HEIGHT = 600, 400
        self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT = 1000, 700
        self.WIDTH, self.HEIGHT = self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT
        
        # Colors (Modern Dark Theme)
        self.COLORS = {
            'bg': (15, 15, 23),           # Dark navy
            'grid': (25, 25, 35),         # Subtle grid
            'snake_head': (102, 252, 241), # Cyan
            'snake_body': (56, 178, 172),  # Teal
            'snake_tail': (34, 116, 112),  # Dark teal
            'food': (239, 68, 68),         # Red (fallback)
            'food_glow': (239, 68, 68, 50), # Red with alpha
            'text_primary': (248, 250, 252), # White
            'text_secondary': (148, 163, 184), # Gray
            'accent': (139, 92, 246),       # Purple
            'success': (34, 197, 94),       # Green
            'warning': (251, 191, 36),      # Yellow
        }
        
        # Screen setup
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Snake Game - Professional Edition")
        self.clock = pygame.time.Clock()
        
        # Initialize grid dimensions
        self.update_grid_dimensions()
        
        # Fonts (will be updated on resize)
        self.update_fonts()
        
        # Load food image
        self.food_image = self.load_food_image()
        
        # Game state
        self.state = GameState.MENU
        self.reset_game()
        
        # Settings
        self.settings = self.load_settings()
        
        # Particles for visual effects
        self.particles = []
        self.food_particles = []
        
        # Animation timers
        self.menu_animation_time = 0
        self.game_over_animation_time = 0
        
        # Load high score
        self.high_score = self.load_high_score()
        
    def update_fonts(self):
        """Update font sizes based on current screen size"""
        base_size = min(self.WIDTH, self.HEIGHT)
        scale = base_size / 700.0  # Base scale on 700px height
        
        self.fonts = {
            'title': pygame.font.Font(None, max(32, int(64 * scale))),
            'large': pygame.font.Font(None, max(24, int(48 * scale))),
            'medium': pygame.font.Font(None, max(20, int(32 * scale))),
            'small': pygame.font.Font(None, max(16, int(24 * scale))),
            'tiny': pygame.font.Font(None, max(14, int(18 * scale)))
        }
        
    def load_food_image(self):
        image_path = os.path.join(os.path.dirname(__file__), "apple.png")
        if os.path.exists(image_path):
            try:
                food_image = pygame.image.load(image_path).convert_alpha()
                food_image = pygame.transform.scale(
                    food_image, (self.CELL_SIZE - 4, self.CELL_SIZE - 4)
                )
                return food_image
            except Exception as e:
                raise RuntimeError(f" Failed to load 'apple.png': {e}")
        else:
            raise FileNotFoundError(
                " 'apple.png' not found! Please place it in the same folder as window.py."
            )

    
    def update_grid_dimensions(self):
        """Update grid dimensions when screen is resized"""
        self.GRID_WIDTH = self.WIDTH // self.CELL_SIZE
        self.GRID_HEIGHT = self.HEIGHT // self.CELL_SIZE
    
    def handle_resize(self, new_width, new_height):
        """Handle window resize event properly"""
        # Enforce minimum size
        new_width = max(new_width, self.MIN_WIDTH)
        new_height = max(new_height, self.MIN_HEIGHT)
        
        # Make sure dimensions are multiples of CELL_SIZE for clean grid
        new_width = (new_width // self.CELL_SIZE) * self.CELL_SIZE
        new_height = (new_height // self.CELL_SIZE) * self.CELL_SIZE
        
        # Update screen dimensions
        self.WIDTH, self.HEIGHT = new_width, new_height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        
        # Update dependent properties
        self.update_grid_dimensions()
        self.update_fonts()
        
        # Reload food image with new size
        self.food_image = self.load_food_image()
        
        # If game is active, check if snake or food is out of bounds
        if self.state == GameState.PLAYING and hasattr(self, 'snake'):
            self.check_bounds_after_resize()
    
    def check_bounds_after_resize(self):
        """Check and fix snake/food positions after resize"""
        # Check if food is out of bounds
        if (self.food_pos[0] >= self.WIDTH or self.food_pos[1] >= self.HEIGHT):
            self.food_pos = self.spawn_food()
        
        # Check if any snake segment is out of bounds
        valid_snake = []
        for segment in self.snake:
            x, y = segment
            if x < self.WIDTH and y < self.HEIGHT and x >= 0 and y >= 0:
                valid_snake.append(segment)
        
        # If snake head is out of bounds, end game
        if not valid_snake or (self.snake and self.snake[0] not in valid_snake):
            self.game_over("Screen resized - snake out of bounds!")
        else:
            self.snake = valid_snake
            # If snake became empty, end game
            if not self.snake:
                self.game_over("Screen resized - snake out of bounds!")
    
    def load_settings(self) -> dict:
        """Load game settings from file"""
        default_settings = {
            'base_speed': 8,
            'speed_increase': True,
            'grid_visible': True,
            'particles': True,
            'sound': True
        }
        
        try:
            with open('snake_settings.json', 'r') as f:
                settings = json.load(f)
                return {**default_settings, **settings}
        except (FileNotFoundError, json.JSONDecodeError):
            return default_settings
    
    def save_settings(self):
        """Save current settings to file"""
        with open('snake_settings.json', 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def load_high_score(self) -> int:
        """Load high score from file"""
        try:
            with open('snake_highscore.txt', 'r') as f:
                return int(f.read().strip() or "0")
        except (FileNotFoundError, ValueError):
            return 0
    
    def save_high_score(self):
        """Save high score to file"""
        if self.score > self.high_score:
            self.high_score = self.score
            with open('snake_highscore.txt', 'w') as f:
                f.write(str(self.high_score))
    
    def reset_game(self):
        """Reset game to initial state"""
        self.update_grid_dimensions()
        center_x = (self.GRID_WIDTH // 2) * self.CELL_SIZE
        center_y = (self.GRID_HEIGHT // 2) * self.CELL_SIZE
        
        self.snake = [(center_x, center_y)]
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.food_pos = self.spawn_food()
        self.score = 0
        self.game_over_reason = ""
        self.particles = []
        self.food_particles = []
        self.game_over_animation_time = 0
    
    def spawn_food(self) -> Tuple[int, int]:
        """Spawn food at random position not occupied by snake"""
        self.update_grid_dimensions()
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            x = random.randint(0, max(0, self.GRID_WIDTH - 1)) * self.CELL_SIZE
            y = random.randint(0, max(0, self.GRID_HEIGHT - 1)) * self.CELL_SIZE
            if (x, y) not in self.snake:
                return (x, y)
            attempts += 1
        
        # Fallback: find any empty space
        for x in range(0, self.WIDTH, self.CELL_SIZE):
            for y in range(0, self.HEIGHT, self.CELL_SIZE):
                if (x, y) not in self.snake:
                    return (x, y)
        
        # If no space found, return safe position
        return (self.CELL_SIZE, self.CELL_SIZE)
    
    def create_particles(self, pos: Tuple[int, int], color: Tuple[int, int, int], count: int = 10):
        """Create particle explosion effect"""
        if not self.settings['particles']:
            return
            
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append({
                'pos': [pos[0] + self.CELL_SIZE // 2, pos[1] + self.CELL_SIZE // 2],
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'life': random.uniform(30, 60),
                'max_life': 60,
                'color': color
            })
    
    def create_food_particles(self, pos: Tuple[int, int]):
        """Create subtle particles around food"""
        if not self.settings['particles']:
            return
            
        if random.random() < 0.1:  # 10% chance per frame
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(15, 25)
            x = pos[0] + self.CELL_SIZE // 2 + math.cos(angle) * distance
            y = pos[1] + self.CELL_SIZE // 2 + math.sin(angle) * distance
            
            self.food_particles.append({
                'pos': [x, y],
                'vel': [math.cos(angle + math.pi) * 0.5, math.sin(angle + math.pi) * 0.5],
                'life': random.uniform(60, 90),
                'max_life': 90,
                'size': random.uniform(1, 3)
            })
    
    def update_particles(self):
        """Update all particle systems"""
        # Update explosion particles
        for particle in self.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['vel'][0] *= 0.95
            particle['vel'][1] *= 0.95
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # Update food particles
        for particle in self.food_particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.food_particles.remove(particle)
    
    def handle_menu_events(self, event):
        """Handle menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.state = GameState.PLAYING
                self.reset_game()
            elif event.key == pygame.K_s:
                self.state = GameState.SETTINGS
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                return False
        return True
    
    def handle_playing_events(self, event):
        """Handle gameplay events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
            elif event.key == pygame.K_r:
                self.reset_game()
            # Movement keys
            elif event.key in [pygame.K_UP, pygame.K_w] and self.direction[1] == 0:
                self.next_direction = (0, -self.CELL_SIZE)
            elif event.key in [pygame.K_DOWN, pygame.K_s] and self.direction[1] == 0:
                self.next_direction = (0, self.CELL_SIZE)
            elif event.key in [pygame.K_LEFT, pygame.K_a] and self.direction[0] == 0:
                self.next_direction = (-self.CELL_SIZE, 0)
            elif event.key in [pygame.K_RIGHT, pygame.K_d] and self.direction[0] == 0:
                self.next_direction = (self.CELL_SIZE, 0)
    
    def handle_paused_events(self, event):
        """Handle paused state events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
            elif event.key == pygame.K_m:
                self.state = GameState.MENU
            elif event.key == pygame.K_r:
                self.reset_game()
                self.state = GameState.PLAYING
    
    def handle_game_over_events(self, event):
        """Handle game over events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                self.reset_game()
                self.state = GameState.PLAYING
            elif event.key == pygame.K_m:
                self.state = GameState.MENU
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                return False
        return True
    
    def update_game(self):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
        
        # Update direction
        self.direction = self.next_direction if self.next_direction != (0, 0) else self.direction
        
        if self.direction == (0, 0):
            return
        
        # Move snake
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= self.WIDTH or 
            new_head[1] < 0 or new_head[1] >= self.HEIGHT):
            self.game_over("Hit the wall!")
            return
        
        # Check self collision
        if new_head in self.snake:
            self.game_over("Ate yourself!")
            return
        
        self.snake.insert(0, new_head)
        
        # Check food collision
        if new_head == self.food_pos:
            self.score += 1
            self.create_particles(self.food_pos, self.COLORS['success'], 15)
            self.food_pos = self.spawn_food()
        else:
            self.snake.pop()  # Remove tail
        
        # Create food particles
        self.create_food_particles(self.food_pos)
    
    def game_over(self, reason: str):
        """Handle game over"""
        self.game_over_reason = reason
        self.save_high_score()
        self.state = GameState.GAME_OVER
        if self.snake:  # Check if snake exists
            self.create_particles(self.snake[0], self.COLORS['food'], 20)
    
    def draw_grid(self):
        """Draw background grid"""
        if not self.settings['grid_visible']:
            return
            
        for x in range(0, self.WIDTH, self.CELL_SIZE):
            pygame.draw.line(self.screen, self.COLORS['grid'], (x, 0), (x, self.HEIGHT))
        for y in range(0, self.HEIGHT, self.CELL_SIZE):
            pygame.draw.line(self.screen, self.COLORS['grid'], (0, y), (self.WIDTH, y))
    
    def draw_snake(self):
        """Draw snake with gradient effect"""
        for i, segment in enumerate(self.snake):
            if i == 0:  # Head
                color = self.COLORS['snake_head']
                # Add glow effect for head
                pygame.draw.rect(self.screen, color, 
                               (segment[0] + 2, segment[1] + 2, 
                                self.CELL_SIZE - 4, self.CELL_SIZE - 4))
            else:  # Body
                # Gradient from body to tail
                ratio = (len(self.snake) - i) / len(self.snake)
                body_color = self.COLORS['snake_body']
                tail_color = self.COLORS['snake_tail']
                
                color = [
                    int(tail_color[j] + (body_color[j] - tail_color[j]) * ratio)
                    for j in range(3)
                ]
                
                pygame.draw.rect(self.screen, color,
                               (segment[0] + 1, segment[1] + 1,
                                self.CELL_SIZE - 2, self.CELL_SIZE - 2))
    
    def draw_food(self):
        """Draw food with image and pulsing glow effect"""
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 3
        
        # Draw glow effect
        glow_size = self.CELL_SIZE + 10 + int(pulse)
        glow_offset = (self.CELL_SIZE - glow_size) // 2
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        
        # Use food color for glow
        glow_color = (*self.COLORS['food'], 30 + int(pulse * 5))
        pygame.draw.circle(glow_surf, glow_color, 
                          (glow_size // 2, glow_size // 2), glow_size // 2)
        self.screen.blit(glow_surf, (self.food_pos[0] + glow_offset, 
                                   self.food_pos[1] + glow_offset))
        
        # Draw food image
        if self.food_image:
            # Apply pulsing scale effect
            scale_factor = 1.0 + pulse * 0.05
            scaled_size = int((self.CELL_SIZE - 4) * scale_factor)
            if scaled_size != self.CELL_SIZE - 4:
                scaled_food = pygame.transform.scale(self.food_image, (scaled_size, scaled_size))
            else:
                scaled_food = self.food_image
            
            # Center the scaled image
            offset_x = (self.CELL_SIZE - scaled_size) // 2
            offset_y = (self.CELL_SIZE - scaled_size) // 2
            
            self.screen.blit(scaled_food, (self.food_pos[0] + offset_x, 
                                         self.food_pos[1] + offset_y))
        else:
            # Fallback to colored rectangle if image failed to load
            size = self.CELL_SIZE - 4 + int(pulse)
            offset = (self.CELL_SIZE - size) // 2
            pygame.draw.rect(self.screen, self.COLORS['food'],
                            (self.food_pos[0] + offset, self.food_pos[1] + offset,
                             size, size))
    
    def draw_particles(self):
        """Draw all particles"""
        # Draw explosion particles
        for particle in self.particles:
            alpha = int((particle['life'] / particle['max_life']) * 255)
            color = (*particle['color'], alpha)
            
            surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (2, 2), 2)
            self.screen.blit(surf, particle['pos'])
        
        # Draw food particles
        for particle in self.food_particles:
            alpha = int((particle['life'] / particle['max_life']) * 100)
            color = (*self.COLORS['food'], alpha)
            
            surf = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, 
                             (int(particle['size']), int(particle['size'])), 
                             int(particle['size']))
            self.screen.blit(surf, particle['pos'])
    
    def draw_hud(self):
        """Draw HUD elements"""
        # Score
        score_text = self.fonts['medium'].render(f"Score: {self.score}", True, self.COLORS['text_primary'])
        self.screen.blit(score_text, (20, 20))
        
        # High score
        high_score_text = self.fonts['small'].render(f"Best: {self.high_score}", True, self.COLORS['text_secondary'])
        self.screen.blit(high_score_text, (20, 55))
        
        # Speed indicator
        current_speed = self.settings['base_speed'] + (self.score // 3 if self.settings['speed_increase'] else 0)
        speed_text = self.fonts['small'].render(f"Speed: {current_speed}", True, self.COLORS['text_secondary'])
        self.screen.blit(speed_text, (20, 80))
        
        # Screen size indicator
        size_text = self.fonts['tiny'].render(f"Size: {self.WIDTH}x{self.HEIGHT}", True, self.COLORS['text_secondary'])
        self.screen.blit(size_text, (20, 105))
        
        # Controls hint (properly aligned to right)
        controls_text = self.fonts['tiny'].render("ESC: Pause | R: Restart | Drag to resize", True, self.COLORS['text_secondary'])
        controls_rect = controls_text.get_rect()
        controls_rect.right = self.WIDTH - 10
        controls_rect.bottom = self.HEIGHT - 10
        self.screen.blit(controls_text, controls_rect)
    
    def draw_menu(self):
        """Draw main menu with proper centering"""
        self.menu_animation_time += 1
        
        # Animated background
        for i in range(0, self.WIDTH, 50):
            alpha = int(abs(math.sin((i + self.menu_animation_time) * 0.01)) * 30)
            color = (*self.COLORS['accent'], alpha)
            surf = pygame.Surface((2, self.HEIGHT), pygame.SRCALPHA)
            surf.fill(color)
            self.screen.blit(surf, (i, 0))
        
        # Title (properly centered)
        title_y = self.HEIGHT * 0.2 + math.sin(self.menu_animation_time * 0.02) * 10
        title_text = self.fonts['title'].render("SNAKE GAME", True, self.COLORS['snake_head'])
        title_rect = title_text.get_rect(center=(self.WIDTH // 2, title_y))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.fonts['medium'].render("Professional Edition", True, self.COLORS['text_secondary'])
        subtitle_rect = subtitle_text.get_rect(center=(self.WIDTH // 2, title_y + 60))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Menu options (properly centered)
        menu_items = [
            ("SPACE - Start Game", self.COLORS['text_primary']),
            ("S - Settings", self.COLORS['text_secondary']),
            ("ESC - Quit", self.COLORS['text_secondary']),
            ("Drag window edges to resize", self.COLORS['text_secondary'])
        ]
        
        start_y = self.HEIGHT * 0.5
        for i, (item, color) in enumerate(menu_items):
            text = self.fonts['medium'].render(item, True, color)
            rect = text.get_rect(center=(self.WIDTH // 2, start_y + i * 40))
            self.screen.blit(text, rect)
        
        # High score display (properly centered)
        if self.high_score > 0:
            hs_text = self.fonts['large'].render(f"High Score: {self.high_score}", True, self.COLORS['success'])
            hs_rect = hs_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT * 0.85))
            self.screen.blit(hs_text, hs_rect)
    
    def draw_pause(self):
        """Draw pause overlay with proper centering"""
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.fonts['title'].render("PAUSED", True, self.COLORS['warning'])
        pause_rect = pause_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        continue_text = self.fonts['medium'].render("Press SPACE to continue", True, self.COLORS['text_secondary'])
        continue_rect = continue_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 20))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_game_over(self):
        """Draw game over screen with proper centering"""
        self.game_over_animation_time += 1
        
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        alpha = min(150, self.game_over_animation_time * 3)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text (centered)
        go_text = self.fonts['title'].render("GAME OVER", True, self.COLORS['food'])
        go_rect = go_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 100))
        self.screen.blit(go_text, go_rect)
        
        # Reason (centered)
        reason_text = self.fonts['medium'].render(self.game_over_reason, True, self.COLORS['text_secondary'])
        reason_rect = reason_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50))
        self.screen.blit(reason_text, reason_rect)
        
        # Final score (centered)
        score_color = self.COLORS['success'] if self.score == self.high_score else self.COLORS['text_primary']
        score_text = self.fonts['large'].render(f"Final Score: {self.score}", True, score_color)
        score_rect = score_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        # New high score (centered)
        if self.score == self.high_score and self.score > 0:
            new_hs_text = self.fonts['medium'].render("NEW HIGH SCORE!", True, self.COLORS['warning'])
            new_hs_rect = new_hs_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 40))
            self.screen.blit(new_hs_text, new_hs_rect)
        
        # Options (centered)
        restart_text = self.fonts['medium'].render("R - Restart    M - Menu    ESC - Quit", True, self.COLORS['text_secondary'])
        restart_rect = restart_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                
                # Handle resize events first (applies to all states)
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.w, event.h)
                    continue
                
                # State-specific event handling
                if self.state == GameState.MENU:
                    running = self.handle_menu_events(event)
                elif self.state == GameState.PLAYING:
                    self.handle_playing_events(event)
                elif self.state == GameState.PAUSED:
                    self.handle_paused_events(event)
                elif self.state == GameState.GAME_OVER:
                    running = self.handle_game_over_events(event)
            
            # Update game logic
            self.update_game()
            self.update_particles()
            
            # Clear screen
            self.screen.fill(self.COLORS['bg'])
            
            # Draw game elements
            if self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
                self.draw_grid()
                self.draw_snake()
                self.draw_food()
                self.draw_particles()
                self.draw_hud()
                
                if self.state == GameState.PAUSED:
                    self.draw_pause()
                elif self.state == GameState.GAME_OVER:
                    self.draw_game_over()
                    
            elif self.state == GameState.MENU:
                self.draw_menu()
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            fps = self.settings['base_speed'] + (self.score // 3 if self.settings['speed_increase'] else 0)
            self.clock.tick(fps)
        
        # Cleanup
        self.save_settings()
        pygame.quit()
        sys.exit()

def main():
    """Main function"""
    try:
        game = SnakeGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()