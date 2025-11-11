import pygame
import sys
import os
import time
try:
    import imageio
    import numpy as np
except ImportError:
    print("imageio or numpy module not found. Please install it with: pip install imageio numpy")
    imageio = None
    np = None

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL/Pillow not available, using imageio for GIF loading")

# Initialize pygame
pygame.init()

# Screen dimensions and display
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
existing_screen = pygame.display.get_surface()
if existing_screen:
    screen = existing_screen
    SCREEN_WIDTH, SCREEN_HEIGHT = existing_screen.get_size()
else:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Typers - Typing Game")

# Colors (matching Gameplay.py)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
BACKGROUND_COLOR = (20, 30, 48)  # Hex #141E30 - same as Gameplay.py
GREEN = (0, 255, 0)
RED = (255, 0, 0)
UNTYPED_COLOR = (150, 150, 150)  # Gray color for untyped text (semi-transparent look)

# Font setup
font_path = os.path.join('fonts', 'fs-pixel-sans-unicode-regular.ttf')
try:
    title_font = pygame.font.Font(font_path, 48)
    button_font = pygame.font.Font(font_path, 36)
    text_font = pygame.font.Font(font_path, 36)  # Font for the paragraph text
    ui_font = pygame.font.Font(font_path, 24)  # Font for UI elements
    stats_font = pygame.font.Font(font_path, 28)  # Font for WPM
    combo_font = pygame.font.Font(font_path, 40)  # Font for COMBO (larger)
except:
    title_font = pygame.font.SysFont('Arial', 48)
    button_font = pygame.font.SysFont('Arial', 36)
    text_font = pygame.font.SysFont('Arial', 36)
    ui_font = pygame.font.SysFont('Arial', 24)
    stats_font = pygame.font.SysFont('Arial', 28)
    combo_font = pygame.font.SysFont('Arial', 40)

# Back button specifications
BACK_BUTTON_SIZE = 44
BACK_BUTTON_PADDING = 16

# Paragraphs for different difficulties
EASY_PARAGRAPH = "The quick brown fox jumps over the lazy dog. This is a simple sentence for beginners to practice typing. Each word is easy to read and type correctly."

NORMAL_PARAGRAPH = "Pixelated games are cool because they bring a mix of nostalgia and creativity their simple blocky art style reminds players of old classic games while still feeling Fresh and Fun today they show that even without realistic graphics games can be full of life emotion and beauty pixel art lets players use their imagination and brings a special charm that modern styles sometimes miss making every scene and character Feel unique and memorable"

HARD_PARAGRAPH = "Programming requires meticulous attention to detail and logical thinking. Developers must understand complex algorithms and data structures to create efficient software solutions. The process involves writing clean code, debugging errors, and optimizing performance. Collaboration with team members is essential for building large scale applications that meet user requirements and industry standards."

def get_paragraph_for_difficulty(difficulty):
    """Get paragraph text based on difficulty."""
    if difficulty == "Easy":
        return EASY_PARAGRAPH
    elif difficulty == "Normal":
        return NORMAL_PARAGRAPH
    else:  # Hard
        return HARD_PARAGRAPH

def get_time_limit_for_difficulty(difficulty):
    """Get time limit in seconds based on difficulty."""
    # Easy: 1:00 (60s). Normal & Hard: 1:30 (90s).
    if difficulty == "Easy":
        return 60
    else:
        return 90

class InteractiveButton:
    """Simple button class for pause/back button."""
    def __init__(self, x, y, width, height, image_path, button_name):
        self.rect = pygame.Rect(x, y, width, height)
        self.button_name = button_name
        self.normal_image = None
        self.hover_image = None
        self.pressed_image = None
        self.current_image = None
        self.is_hovered = False
        self.is_pressed = False
        self.enabled = True
        
        # Load button images
        self.load_images(image_path)
    
    def load_images(self, base_image_path):
        """Load button images for different states."""
        try:
            if os.path.exists(base_image_path):
                original_image = pygame.image.load(base_image_path).convert_alpha()
                self.normal_image = pygame.transform.scale(original_image, (self.rect.width, self.rect.height))
                self.current_image = self.normal_image
                
                # Create hover and pressed states
                self.hover_image = self.normal_image.copy()
                self.pressed_image = self.normal_image.copy()
                
                # Apply effects
                if self.hover_image:
                    brighten = pygame.Surface(self.hover_image.get_size(), pygame.SRCALPHA)
                    brighten.fill((50, 50, 50, 50))
                    self.hover_image.blit(brighten, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                
                if self.pressed_image:
                    darken = pygame.Surface(self.pressed_image.get_size(), pygame.SRCALPHA)
                    darken.fill((0, 0, 0, 50))
                    self.pressed_image.blit(darken, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        except Exception as e:
            print(f"Error loading button image: {e}")
    
    def handle_event(self, event):
        """Handle mouse events for the button."""
        if not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.update_image_state()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.is_pressed = True
                self.update_image_state()
                return False
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed:
                self.is_pressed = False
                self.update_image_state()
                if self.rect.collidepoint(event.pos):
                    return True
        
        return False
    
    def update_image_state(self):
        """Update the current image based on button state."""
        if self.is_pressed:
            self.current_image = self.pressed_image if self.pressed_image else self.normal_image
        elif self.is_hovered:
            self.current_image = self.hover_image if self.hover_image else self.normal_image
        else:
            self.current_image = self.normal_image
    
    def draw(self, screen_surface):
        """Draw the button on the screen."""
        if self.current_image:
            screen_surface.blit(self.current_image, self.rect)

def draw_pause_button(screen, x, y, size):
    """Draw a simple pause button (two vertical lines)."""
    line_width = 4
    line_height = size - 10
    spacing = 6
    
    # Left line
    pygame.draw.rect(screen, WHITE, (x, y + 5, line_width, line_height))
    # Right line
    pygame.draw.rect(screen, WHITE, (x + line_width + spacing, y + 5, line_width, line_height))

def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width."""
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        word_surface = font.render(word, True, WHITE)
        word_width = word_surface.get_width()
        space_width = font.size(' ')[0]
        
        if current_width + word_width + space_width > max_width and current_line:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
        else:
            current_line.append(word)
            current_width += word_width + space_width
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def render_colored_text(screen, text, font, start_x, start_y, max_width, typed_chars, cursor_index=None):
    """Render text with different colors based on typing status."""
    current_x = start_x
    current_y = start_y
    line_height = font.get_height()
    cursor_pos = None  # Store cursor position
    
    for i, char in enumerate(text):
        # Determine color based on typing status
        if i < len(typed_chars):
            # Character has been typed
            if typed_chars[i]:
                color = WHITE  # Correctly typed - turn white
            else:
                # Incorrectly typed - keep it gray (don't turn red)
                color = UNTYPED_COLOR
        else:
            # Not yet typed - gray/transparent
            color = UNTYPED_COLOR
        
        # Check if we need to wrap to next line
        char_surface = font.render(char, True, color)
        char_width = char_surface.get_width()
        
        # Check if adding this character would exceed the max width
        # Wrap at spaces to prevent overflow
        if char == ' ' and current_x + char_width > start_x + max_width:
            # Move to next line
            current_x = start_x
            current_y += line_height
        elif char != ' ' and current_x + char_width > start_x + max_width:
            # If a non-space character would overflow, wrap to next line anyway
            current_x = start_x
            current_y += line_height
        
        # Store cursor position if this is the current character to type
        if cursor_index is not None and i == cursor_index:
            cursor_pos = (current_x, current_y, char_width, line_height)
        
        screen.blit(char_surface, (current_x, current_y))
        current_x += char_width
    
    return cursor_pos  # Return cursor position for drawing the indicator

def render_user_input(screen, user_input, expected_text, font, start_x, start_y, max_width):
    """Render what the user has typed so far, overlaid on the sentence."""
    # Use the same positioning logic as render_colored_text to ensure perfect alignment
    # We need to match the exact position of each character in the expected text
    current_x = start_x
    current_y = start_y
    line_height = font.get_height()
    
    # Track position in expected text for alignment
    expected_index = 0
    
    for i, typed_char in enumerate(user_input):
        # Determine color - compare with expected character
        if expected_index < len(expected_text):
            expected_char = expected_text[expected_index]
            is_correct = (typed_char == expected_char)
            color = WHITE if is_correct else RED
        else:
            # Extra characters typed
            color = RED
        
        # Get the width of the expected character (for alignment) and typed character (for rendering)
        expected_char_surface = font.render(expected_char if expected_index < len(expected_text) else ' ', True, UNTYPED_COLOR)
        expected_char_width = expected_char_surface.get_width()
        
        # Render the character the user typed
        typed_char_surface = font.render(typed_char, True, color)
        typed_char_width = typed_char_surface.get_width()
        
        # Check if we need to wrap to next line (use expected text's wrapping logic)
        # This ensures alignment with the original text
        if expected_index < len(expected_text):
            # Wrap at spaces or if character would overflow
            if expected_char == ' ' and current_x + expected_char_width > start_x + max_width:
                # Move to next line (matching the original text wrapping)
                current_x = start_x
                current_y += line_height
            elif expected_char != ' ' and current_x + expected_char_width > start_x + max_width:
                # If a non-space character would overflow, wrap to next line anyway
                current_x = start_x
                current_y += line_height
        
        # Render the typed character at the position where the expected character should be
        screen.blit(typed_char_surface, (current_x, current_y))
        
        # Advance position using expected character width to maintain alignment
        if expected_index < len(expected_text):
            current_x += expected_char_width
        else:
            # For extra characters, use typed character width
            current_x += typed_char_width
        
        expected_index += 1

def calculate_wpm(characters_typed, time_elapsed, typed_chars=None):
    """Calculate Words Per Minute.
    
    Args:
        characters_typed: Total characters typed (including mistakes)
        time_elapsed: Time elapsed in seconds
        typed_chars: Optional list of booleans indicating correct (True) or incorrect (False) characters
                    If provided, only correctly typed characters are counted for WPM
    """
    if time_elapsed <= 0:
        return 0
    
    # If we have the typed_chars list, count only correctly typed characters
    if typed_chars is not None:
        correct_chars = sum(1 for is_correct in typed_chars if is_correct)
        characters_typed = correct_chars
    
    # Standard: 5 characters = 1 word (including spaces)
    # This is the industry standard for typing tests
    words = characters_typed / 5.0
    
    # Convert seconds to minutes
    minutes = time_elapsed / 60.0
    
    # Calculate WPM, rounding to nearest integer for display
    if minutes > 0:
        wpm = words / minutes
        return round(wpm)  # Round to nearest integer for more accurate display
    return 0

def calculate_accuracy(total_chars, mistakes):
    """Calculate typing accuracy percentage."""
    if total_chars == 0:
        return 100.0
    correct_chars = total_chars - mistakes
    accuracy = (correct_chars / total_chars) * 100.0
    # Ensure accuracy doesn't go below 0
    return max(0.0, accuracy)

def main(difficulty="Normal"):
    """Main function for the typing game."""
    print(f"Starting typing game with difficulty: {difficulty}")
    
    clock = pygame.time.Clock()
    running = True
    game_started = False
    game_completed = False
    
    # Load flame image for combo >= 10
    flame_image = None
    flame_frames = []
    try:
        flame_path = os.path.join('images', 'flame-lit.gif')
        if os.path.exists(flame_path):
            # Preferred: use PIL + ImageSequence for correct frame handling/transparency
            try:
                from PIL import ImageSequence
                if PIL_AVAILABLE:
                    img = Image.open(flame_path)
                    for frame in ImageSequence.Iterator(img):
                        frame_rgba = frame.convert('RGBA')
                        size = frame_rgba.size  # (width, height)
                        raw = frame_rgba.tobytes()
                        surf = pygame.image.frombuffer(raw, size, 'RGBA').convert_alpha()
                        flame_frames.append(surf)
                # If PIL wasn't available, fall through to imageio below
            except Exception:
                pass

            # Fallback to imageio if PIL failed or not available
            if not flame_frames and imageio and np:
                try:
                    reader = imageio.get_reader(flame_path)
                    for frame in reader:
                        # frame is H x W x (3 or 4)
                        h, w = frame.shape[0], frame.shape[1]
                        if frame.shape[2] == 4:
                            surf = pygame.image.frombuffer(frame.tobytes(), (w, h), 'RGBA').convert_alpha()
                        else:
                            surf = pygame.image.frombuffer(frame.tobytes(), (w, h), 'RGB').convert()
                            surf = surf.convert_alpha()
                        flame_frames.append(surf)
                    reader.close()
                except Exception as e:
                    print(f"imageio failed to load GIF: {e}")

            if flame_frames:
                flame_image = flame_frames[0]
                print(f"Flame GIF loaded successfully with {len(flame_frames)} frames")
    except Exception as e:
        print(f"Could not load flame image: {e}")
    
    # Get paragraph text
    paragraph_text = get_paragraph_for_difficulty(difficulty)
    
    # Get time limit
    time_limit = get_time_limit_for_difficulty(difficulty)  # in seconds
    
    # Game state
    user_input = ""
    typed_chars = []  # List of booleans: True = correct, False = incorrect
    current_char_index = 0
    combo = 0
    highest_combo = 0  # Track the highest combo achieved
    total_mistakes = 0  # Current mistakes (can decrease with backspace)
    permanent_mistakes = 0  # Total mistakes ever made (never decreases, used for accuracy)
    start_time = None
    end_time = None
    time_ran_out = False
    
    # Backspace hold tracking
    backspace_held = False
    backspace_repeat_time = 0
    backspace_initial_delay = 500  # milliseconds before repeat starts
    backspace_repeat_delay = 50  # milliseconds between repeats
    
    # Flame animation tracking
    flame_frame_index = 0
    flame_animation_speed = 50  # milliseconds between frames (faster animation)
    last_flame_update = pygame.time.get_ticks()
    
    # Pause button (top-left)
    pause_button_rect = pygame.Rect(BACK_BUTTON_PADDING, BACK_BUTTON_PADDING, BACK_BUTTON_SIZE, BACK_BUTTON_SIZE)
    
    # Wrap text for display - use more conservative margins to ensure it fits
    margin = 80  # Increased margin on both sides
    max_text_width = SCREEN_WIDTH - (margin * 2)  # Ensure text fits with padding
    text_lines = wrap_text(paragraph_text, text_font, max_text_width)
    
    # Calculate text starting position (centered)
    text_start_y = SCREEN_HEIGHT // 2 - (len(text_lines) * text_font.get_height()) // 2
    
    # Game loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle pause button click
            if event.type == pygame.MOUSEBUTTONUP:
                if pause_button_rect.collidepoint(event.pos):
                    return "BACK_TO_DIFFICULTY"
            
            # Keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "BACK_TO_DIFFICULTY"
                
                # Handle text input (only if game not completed)
                if not game_completed:
                    if not game_started:
                        # Start the game on first keypress
                        game_started = True
                        start_time = time.time()
                    
                    # Ignore modifier keys (Shift, Ctrl, Alt, etc.)
                    if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LCTRL, pygame.K_RCTRL, 
                                     pygame.K_LALT, pygame.K_RALT, pygame.K_LMETA, pygame.K_RMETA,
                                     pygame.K_CAPSLOCK, pygame.K_TAB]:
                        continue
                    
                    if event.key == pygame.K_BACKSPACE:
                        # Start backspace hold
                        backspace_held = True
                        backspace_repeat_time = pygame.time.get_ticks() + backspace_initial_delay
                        # Delete immediately on first press
                        if user_input and current_char_index > 0:
                            user_input = user_input[:-1]
                            if typed_chars:
                                # Remove last typed character
                                # Note: permanent_mistakes is NOT decreased - mistakes count forever for accuracy
                                if not typed_chars[-1]:  # If it was a mistake
                                    total_mistakes -= 1  # Decrease current mistake count for combo/display
                                typed_chars.pop()
                                current_char_index -= 1
            
            # Handle key release for backspace
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_BACKSPACE:
                    backspace_held = False
            
            # Handle text input (only if game not completed and time hasn't run out)
            if event.type == pygame.KEYDOWN and not game_completed and not time_ran_out:
                if event.unicode and event.unicode.isprintable() and len(event.unicode) > 0:
                    # Only process actual printable characters (not modifier keys)
                    char = event.unicode
                    user_input += char
                    
                    # Check if character matches
                    if current_char_index < len(paragraph_text):
                        expected_char = paragraph_text[current_char_index]
                        is_correct = (char == expected_char)  # Case-sensitive comparison - capitalization matters!
                        typed_chars.append(is_correct)
                        
                        if not is_correct:
                            total_mistakes += 1
                            permanent_mistakes += 1  # Permanent mistake count (never decreases)
                            combo = 0  # Reset combo on mistake
                        else:
                            # Increment combo when we complete a word (type a space correctly)
                            if expected_char == ' ':
                                combo += 1
                                # Update highest combo
                                if combo > highest_combo:
                                    highest_combo = combo
                            # Also increment on last character if it's the end
                            elif current_char_index == len(paragraph_text) - 1:
                                combo += 1
                                # Update highest combo
                                if combo > highest_combo:
                                    highest_combo = combo
                        
                        current_char_index += 1
                        
                        # Check if paragraph is complete (can complete even with mistakes)
                        if current_char_index >= len(paragraph_text):
                            game_completed = True
                            end_time = time.time()
                            print(f"Level completed! Mistakes: {total_mistakes}, Total chars: {len(typed_chars)}")
        
        # Check timer
        if game_started and not game_completed and not time_ran_out:
            elapsed_time = time.time() - start_time if start_time else 0
            remaining_time = time_limit - elapsed_time
            
            if remaining_time <= 0:
                # Time ran out
                time_ran_out = True
                game_completed = True
                end_time = time.time()
                print(f"Time ran out! Completed {len(typed_chars)} characters")
        
        # Handle backspace repeat (when held down)
        if backspace_held and not game_completed and not time_ran_out:
            current_ticks = pygame.time.get_ticks()
            if current_ticks >= backspace_repeat_time:
                # Delete a character
                if user_input and current_char_index > 0:
                    user_input = user_input[:-1]
                    if typed_chars:
                        # Remove last typed character
                        # Note: permanent_mistakes is NOT decreased - mistakes count forever for accuracy
                        if not typed_chars[-1]:  # If it was a mistake
                            total_mistakes -= 1  # Decrease current mistake count for combo/display
                        typed_chars.pop()
                        current_char_index -= 1
                # Set next repeat time
                backspace_repeat_time = current_ticks + backspace_repeat_delay
        
        # Clear screen with background color
        screen.fill(BACKGROUND_COLOR)
        
        # Draw pause button (two vertical lines)
        draw_pause_button(screen, pause_button_rect.x, pause_button_rect.y, pause_button_rect.height)
        
        # Update flame animation continuously (even when not visible)
        if flame_frames:
            current_ticks = pygame.time.get_ticks()
            if current_ticks - last_flame_update >= flame_animation_speed:
                flame_frame_index = (flame_frame_index + 1) % len(flame_frames)
                last_flame_update = current_ticks
        
        # Draw COMBO counter (below pause button) - only show during active game
        if not game_completed:
            combo_text = combo_font.render(f"COMBO: {combo:02d}", True, WHITE)
            combo_text_rect = combo_text.get_rect()
            combo_x = BACK_BUTTON_PADDING
            combo_y = BACK_BUTTON_PADDING + BACK_BUTTON_SIZE + 10
            
            # Draw flame behind combo if combo >= 10
            if combo >= 5 and flame_frames:
                # Get current flame frame (animation already updated above)
                current_flame = flame_frames[flame_frame_index]
                
                # Calculate the number part width and position
                number_text = f"{combo:02d}"
                number_width = combo_font.size(number_text)[0]
                number_height = combo_font.size(number_text)[1]
                
                # Scale flame to fit the number size
                flame_scale = number_height * 1.2  # Scale to fit number height with some padding
                flame_scaled = pygame.transform.scale(current_flame, (int(flame_scale), int(flame_scale)))
                
                # Position flame centered behind the number
                # Find where the number starts (after "COMBO: ")
                label_text = "COMBO: "
                label_width = combo_font.size(label_text)[0]
                number_start_x = combo_x + label_width
                
                # Center flame behind the number
                flame_x = number_start_x + (number_width // 2) - (flame_scaled.get_width() // 2)
                flame_y = combo_y + (number_height // 2) - (flame_scaled.get_height() // 2)
                
                # Draw flame behind text
                screen.blit(flame_scaled, (flame_x, flame_y))
            
            # Draw combo text on top
            screen.blit(combo_text, (combo_x, combo_y))
        
        # Draw paragraph text with color coding
        if not game_completed:
            # Render text character by character with color coding
            text_x = (SCREEN_WIDTH - max_text_width) // 2
            cursor_pos = render_colored_text(screen, paragraph_text, text_font, text_x, text_start_y, max_text_width, typed_chars, current_char_index)
            
            # Draw gray cursor box at current typing position
            if cursor_pos is not None:
                cursor_x, cursor_y, cursor_width, cursor_height = cursor_pos
                # Draw a semi-transparent gray box behind the current character
                cursor_box = pygame.Surface((cursor_width, cursor_height), pygame.SRCALPHA)
                cursor_box.fill((100, 100, 100, 150))  # Gray with transparency
                screen.blit(cursor_box, (cursor_x, cursor_y))
            
            # Draw user's input ON TOP of the paragraph (overlaid) so they can see what they typed
            if user_input:
                # Render what the user has typed at the same position as the paragraph
                render_user_input(screen, user_input, paragraph_text[:len(user_input)], text_font, text_x, text_start_y, max_text_width)
        else:
            # Game completed - show results
            # Calculate stats
            time_elapsed = end_time - start_time if start_time and end_time else 0
            wpm = calculate_wpm(len(typed_chars), time_elapsed, typed_chars)
            
            # Calculate accuracy: how accurate they typed WITHOUT mistakes
            # For every mistake (even if erased), they lose accuracy
            total_chars_typed = len(typed_chars)
            if total_chars_typed > 0:
                # Use permanent mistakes - mistakes count even if erased with backspace
                # Accuracy = (correct characters / total characters) * 100
                # correct_chars = total_chars_typed - permanent_mistakes
                correct_chars = total_chars_typed - permanent_mistakes
                accuracy = (correct_chars / total_chars_typed) * 100.0
            else:
                accuracy = 0.0
            
            # Ensure accuracy is between 0 and 100
            accuracy = max(0.0, min(100.0, accuracy))
            
            # Draw completion message (larger font)
            if time_ran_out:
                completion_text = title_font.render("Typing Incomplete", True, RED)
            else:
                completion_text = title_font.render("Typing Complete!", True, GREEN)
            completion_rect = completion_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
            screen.blit(completion_text, completion_rect)
            
            # Draw WPM (larger font)
            wpm_text = button_font.render(f"WPM: {wpm}", True, WHITE)
            wpm_rect = wpm_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(wpm_text, wpm_rect)
            
            # Draw Accuracy (larger font)
            accuracy_text = button_font.render(f"Accuracy: {accuracy:.1f}%", True, WHITE)
            accuracy_rect = accuracy_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            screen.blit(accuracy_text, accuracy_rect)
            
            # Draw Highest Combo (larger font)
            highest_combo_text = button_font.render(f"Highest Combo: {highest_combo:02d}", True, WHITE)
            highest_combo_rect = highest_combo_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            screen.blit(highest_combo_text, highest_combo_rect)
            
            # Draw instructions
            instruction_text = ui_font.render("Press ESC or click pause to return", True, GRAY)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
            screen.blit(instruction_text, instruction_rect)
        
        # Draw timer (top-right) - only show during active game
        if game_started and not game_completed:
            elapsed_time = time.time() - start_time if start_time else 0
            remaining_time = max(0, time_limit - elapsed_time)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            timer_text = f"{minutes:01d}:{seconds:02d}"
            
            # Blink white to red when <= 10 seconds
            if remaining_time <= 10:
                # Blink effect: alternate between white and red
                blink_cycle = int(pygame.time.get_ticks() / 500) % 2  # Switch every 500ms
                timer_color = RED if blink_cycle == 0 else WHITE
            else:
                timer_color = WHITE
            
            timer_surface = stats_font.render(timer_text, True, timer_color)
            timer_rect = timer_surface.get_rect(topright=(SCREEN_WIDTH - BACK_BUTTON_PADDING, BACK_BUTTON_PADDING))
            screen.blit(timer_surface, timer_rect)
        
        # Draw WPM in bottom-left (only during typing)
        if game_started and not game_completed:
            time_elapsed = time.time() - start_time if start_time else 0
            wpm = calculate_wpm(len(typed_chars), time_elapsed, typed_chars)
            wpm_text = stats_font.render(f"WPM", True, WHITE)
            screen.blit(wpm_text, (BACK_BUTTON_PADDING, SCREEN_HEIGHT - 60))  # Moved up 20px
            wpm_value_text = stats_font.render(f"{wpm}", True, WHITE)
            screen.blit(wpm_value_text, (BACK_BUTTON_PADDING, SCREEN_HEIGHT - 40))  # Moved up 20px
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    return None

# Entry point
if __name__ == "__main__":
    result = main("Normal")
    print(f"Game ended with result: {result}")
