import pygame
import sys
import os
import math
try:
    import imageio
except ImportError:
    print("imageio module not found. Please install it with: pip install imageio")
    sys.exit(1)

# Import TheTypingGame module
try:
    import TheTypingGame
    TYPING_GAME_AVAILABLE = True
    print("TheTypingGame module loaded successfully")
except ImportError as e:
    print(f"Could not load TheTypingGame module: {e}")
    TYPING_GAME_AVAILABLE = False
except Exception as e:
    print(f"Error loading TheTypingGame module: {e}")
    TYPING_GAME_AVAILABLE = False

# Initialize pygame
pygame.init()

# Screen dimensions and display
# Prefer reusing the existing window created by Pixel Typers
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
existing_screen = pygame.display.get_surface()
if existing_screen:
    screen = existing_screen
    SCREEN_WIDTH, SCREEN_HEIGHT = existing_screen.get_size()
else:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Selection!")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
BACKGROUND_COLOR = (20, 30, 48)  # Hex #141E30 converted to RGB

# Font setup
font_path = os.path.join('fonts', 'fs-pixel-sans-unicode-regular.ttf')
try:
    title_font = pygame.font.Font(font_path, 48)
    button_font = pygame.font.Font(font_path, 36)
except:
    title_font = pygame.font.SysFont('Arial', 48)
    button_font = pygame.font.SysFont('Arial', 36)

# Game states
SELECTION_SCREEN = 0  # Practice/Multiplayer selection
DIFFICULTY_SCREEN = 1  # Difficulty selection (Easy/Normal/Hard)

# Button positioning and sizing (Practice/Multiplayer scaled up 30%)
BUTTON_WIDTH = 600 # 180 * 1.3 (30% increase)
BUTTON_HEIGHT = 120  # 60 * 1.3 (30% increase)
BUTTON_SPACING = 60  # Increased spacing for better visual separation
# Center the two stacked buttons (as a group) vertically
BUTTON_START_Y = (SCREEN_HEIGHT - (2 * BUTTON_HEIGHT + BUTTON_SPACING)) // 2

# Difficulty button specifications
DIFFICULTY_BUTTON_WIDTH = 300
DIFFICULTY_BUTTON_HEIGHT = 80
DIFFICULTY_BUTTON_SPACING = 40
# Center the three difficulty buttons vertically
DIFFICULTY_START_Y = (SCREEN_HEIGHT - (3 * DIFFICULTY_BUTTON_HEIGHT + 2 * DIFFICULTY_BUTTON_SPACING)) // 2

# Back button specifications (44x44 points with 16pt padding)
BACK_BUTTON_SIZE = 44
BACK_BUTTON_PADDING = 16

# Initialize buttons
def initialize_buttons():
    """Initialize all buttons including back button, PracticeBTN and MultiplayerBTN."""
    buttons = []
    
    def center_button_rect_by_image(button):
        """Center the button horizontally based on its current image width."""
        try:
            if button and button.current_image:
                image_width = button.current_image.get_width()
                # Update rect width to image width and center horizontally
                button.rect.width = image_width
                button.rect.x = (SCREEN_WIDTH - image_width) // 2
        except Exception:
            # If anything goes wrong, keep existing centering by rect
            pass
    
    # Back Button - positioned in top-left corner with 16pt padding
    back_btn = InteractiveButton(
        BACK_BUTTON_PADDING,  # 16px from left
        BACK_BUTTON_PADDING,  # 16px from top
        BACK_BUTTON_SIZE,     # 44x44 points
        BACK_BUTTON_SIZE,
        'images/Back Button 1.png',  # Use the back button image
        'BackButton'
    )
    buttons.append(back_btn)
    
    # Calculate position for vertically centered buttons
    # Buttons will be stacked vertically with spacing
    center_x = (SCREEN_WIDTH - BUTTON_WIDTH) // 2
    
    # PracticeBTN - top button in vertical layout
    practice_btn = InteractiveButton(
        center_x, 
        BUTTON_START_Y, 
        BUTTON_WIDTH, 
        BUTTON_HEIGHT, 
        'images/PracticeBTN.png',
        'PracticeBTN'
    )
    center_button_rect_by_image(practice_btn)
    buttons.append(practice_btn)
    
    # MultiplayerBTN - bottom button in vertical layout
    multiplayer_btn = InteractiveButton(
        center_x, 
        BUTTON_START_Y + BUTTON_HEIGHT + BUTTON_SPACING, 
        BUTTON_WIDTH, 
        BUTTON_HEIGHT, 
        'images/MultiplayerBTN.png',
        'MultiplayerBTN'
    )
    center_button_rect_by_image(multiplayer_btn)
    buttons.append(multiplayer_btn)
    
    return buttons

def initialize_difficulty_buttons():
    """Initialize difficulty selection buttons (Easy, Normal, Hard) and back button."""
    buttons = []
    
    def center_button_rect_by_image(button):
        """Center the button horizontally based on its current image width."""
        try:
            if button and button.current_image:
                image_width = button.current_image.get_width()
                # Update rect width to image width and center horizontally
                button.rect.width = image_width
                button.rect.x = (SCREEN_WIDTH - image_width) // 2
        except Exception:
            # If anything goes wrong, keep existing centering by rect
            pass
    
    # Back Button - positioned in top-left corner with 16pt padding
    back_btn = InteractiveButton(
        BACK_BUTTON_PADDING,  # 16px from left
        BACK_BUTTON_PADDING,  # 16px from top
        BACK_BUTTON_SIZE,     # 44x44 points
        BACK_BUTTON_SIZE,
        'images/Back Button 1.png',  # Use the back button image
        'BackButton'
    )
    buttons.append(back_btn)
    
    # Calculate position for vertically centered difficulty buttons
    center_x = (SCREEN_WIDTH - DIFFICULTY_BUTTON_WIDTH) // 2
    
    # Easy button - top button
    easy_btn = InteractiveButton(
        center_x,
        DIFFICULTY_START_Y,
        DIFFICULTY_BUTTON_WIDTH,
        DIFFICULTY_BUTTON_HEIGHT,
        'images/EasyBTN.png',
        'EasyBTN'
    )
    center_button_rect_by_image(easy_btn)
    buttons.append(easy_btn)
    
    # Normal button - middle button
    normal_btn = InteractiveButton(
        center_x,
        DIFFICULTY_START_Y + DIFFICULTY_BUTTON_HEIGHT + DIFFICULTY_BUTTON_SPACING,
        DIFFICULTY_BUTTON_WIDTH,
        DIFFICULTY_BUTTON_HEIGHT,
        'images/Normal BTN.png',
        'NormalBTN'
    )
    center_button_rect_by_image(normal_btn)
    buttons.append(normal_btn)
    
    # Hard button - bottom button
    hard_btn = InteractiveButton(
        center_x,
        DIFFICULTY_START_Y + 2 * (DIFFICULTY_BUTTON_HEIGHT + DIFFICULTY_BUTTON_SPACING),
        DIFFICULTY_BUTTON_WIDTH,
        DIFFICULTY_BUTTON_HEIGHT,
        'images/Hard BTN.png',
        'HardBTN'
    )
    center_button_rect_by_image(hard_btn)
    buttons.append(hard_btn)
    
    return buttons

# Button class for interactive buttons
class InteractiveButton:
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
            # Load normal state image
            if os.path.exists(base_image_path):
                original_image = pygame.image.load(base_image_path).convert_alpha()
                # Scale to fit the button dimensions while maintaining aspect ratio
                self.normal_image = self.scale_image_keep_aspect(original_image, self.rect.width, self.rect.height)
                self.current_image = self.normal_image
                print(f"Loaded {self.button_name} button image successfully")
                
                # For actual button images, we'll use the same image for all states
                # but apply visual effects for hover and pressed states
                self.hover_image = self.normal_image.copy()
                self.pressed_image = self.normal_image.copy()
                
                # Apply subtle effects for different states
                if self.hover_image:
                    # Slightly brighten hover image
                    brighten = pygame.Surface(self.hover_image.get_size(), pygame.SRCALPHA)
                    brighten.fill((50, 50, 50, 50))  # Semi-transparent white
                    self.hover_image.blit(brighten, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                
                if self.pressed_image:
                    # Slightly darken pressed image
                    darken = pygame.Surface(self.pressed_image.get_size(), pygame.SRCALPHA)
                    darken.fill((0, 0, 0, 50))  # Semi-transparent black
                    self.pressed_image.blit(darken, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                
            else:
                print(f"Warning: {base_image_path} not found, using fallback rectangle")
                self.create_fallback_images()
                
        except Exception as e:
            print(f"Error loading {self.button_name} button image: {e}")
            self.create_fallback_images()
    
    def scale_image_keep_aspect(self, image, target_width, target_height):
        """Scale image while maintaining aspect ratio."""
        original_width, original_height = image.get_size()
        aspect_ratio = original_width / original_height
        
        # Calculate scaling to fit target dimensions
        if aspect_ratio > 1:  # Wider than tall
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
            if new_height > target_height:
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
        else:  # Taller than wide or square
            new_height = target_height
            new_width = int(target_height * aspect_ratio)
            if new_width > target_width:
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
        
        return pygame.transform.scale(image, (new_width, new_height))
    
    def create_fallback_images(self):
        """Create fallback rectangle images if image files are not available."""
        # Create colored rectangles for different states
        self.normal_image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.hover_image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.pressed_image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        if self.button_name == "BackButton":
            # Create circular back button fallback (clean design, no text)
            center = (self.rect.width // 2, self.rect.height // 2)
            radius = min(self.rect.width, self.rect.height) // 2 - 4
            
            # Normal state - circular button
            pygame.draw.circle(self.normal_image, (60, 70, 90), center, radius)  # Darker gray-blue
            pygame.draw.circle(self.normal_image, (80, 90, 110), center, radius, width=2)
            
            # Hover state - lighter circle
            pygame.draw.circle(self.hover_image, (80, 90, 120), center, radius)
            pygame.draw.circle(self.hover_image, (100, 110, 130), center, radius, width=2)
            
            # Pressed state - darker circle
            pygame.draw.circle(self.pressed_image, (40, 50, 70), center, radius)
            pygame.draw.circle(self.pressed_image, (60, 70, 90), center, radius, width=2)
            
            # Draw arrow for back button (clean arrow design)
            arrow_size = radius // 2
            arrow_points = [
                (center[0] - arrow_size // 3, center[1]),
                (center[0] - arrow_size, center[1] - arrow_size // 2),
                (center[0] - arrow_size, center[1] + arrow_size // 2)
            ]
            
            pygame.draw.polygon(self.normal_image, WHITE, arrow_points)
            pygame.draw.polygon(self.hover_image, WHITE, arrow_points)
            pygame.draw.polygon(self.pressed_image, WHITE, arrow_points)
            
        else:
            # Normal rectangular buttons for Practice and Multiplayer
            # Normal state - blue rectangle
            pygame.draw.rect(self.normal_image, BLUE, self.normal_image.get_rect(), border_radius=10)
            pygame.draw.rect(self.normal_image, (0, 80, 200), self.normal_image.get_rect(), width=3, border_radius=10)
            
            # Hover state - lighter blue rectangle
            pygame.draw.rect(self.hover_image, (0, 150, 255), self.hover_image.get_rect(), border_radius=10)
            pygame.draw.rect(self.hover_image, (0, 180, 255), self.hover_image.get_rect(), width=3, border_radius=10)
            
            # Pressed state - darker blue rectangle
            pygame.draw.rect(self.pressed_image, (0, 60, 150), self.pressed_image.get_rect(), border_radius=10)
            pygame.draw.rect(self.pressed_image, (0, 40, 100), self.pressed_image.get_rect(), width=3, border_radius=10)
        
        self.current_image = self.normal_image
    
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
                print(f"{self.button_name} button pressed")
                return False
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed:
                self.is_pressed = False
                self.update_image_state()
                if self.rect.collidepoint(event.pos):
                    print(f"{self.button_name} button clicked")
                    return True
        
        return False
    
    def update_image_state(self):
        """Update the current image based on button state."""
        if self.normal_image is None:
            return
            
        if self.is_pressed:
            self.current_image = self.pressed_image if self.pressed_image else self.normal_image
        elif self.is_hovered:
            self.current_image = self.hover_image if self.hover_image else self.normal_image
        else:
            self.current_image = self.normal_image
    
    def draw(self, screen_surface):
        """Draw the button on the screen."""
        if self.current_image:
            # Center the image within the button rect if it's smaller
            image_rect = self.current_image.get_rect()
            if image_rect.width < self.rect.width or image_rect.height < self.rect.height:
                # Center the image
                draw_x = self.rect.x + (self.rect.width - image_rect.width) // 2
                draw_y = self.rect.y + (self.rect.height - image_rect.height) // 2
                screen_surface.blit(self.current_image, (draw_x, draw_y))
            else:
                screen_surface.blit(self.current_image, self.rect)
        
        # Only draw fallback text if using fallback images (no actual button image)
        # Do not render text for buttons that have images (BackButton, difficulty buttons, etc.)
        buttons_with_images = ["BackButton", "EasyBTN", "NormalBTN", "HardBTN", "PracticeBTN", "MultiplayerBTN"]
        image_path = os.path.join('images', f'{self.button_name}.png')
        if self.normal_image and not os.path.exists(image_path):
            # Do not render fallback text for buttons that should only show images
            if self.button_name not in buttons_with_images:
                text_color = WHITE if self.enabled else GRAY
                text_surface = button_font.render(self.button_name.replace('BTN', ''), True, text_color)
                text_rect = text_surface.get_rect(center=self.rect.center)
                screen_surface.blit(text_surface, text_rect)
    
    def set_enabled(self, enabled):
        """Enable or disable the button."""
        self.enabled = enabled
        if not enabled:
            self.is_hovered = False
            self.is_pressed = False
            self.update_image_state()

def main():
    """Main function for the Gameplay module."""
    print("Gameplay.py main() function called")
    
    # Do not change working directory; rely on relative paths from the launcher
    
    clock = pygame.time.Clock()
    running = True
    
    # Initialize with selection screen
    current_state = SELECTION_SCREEN
    buttons = initialize_buttons()
    print(f"Initialized {len(buttons)} buttons: {[btn.button_name for btn in buttons]}")
    
    # Simple game loop for demonstration
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Keyboard shortcut to go back
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    if current_state == DIFFICULTY_SCREEN:
                        # Go back to selection screen
                        print("Keyboard back pressed - returning to selection screen")
                        current_state = SELECTION_SCREEN
                        buttons = initialize_buttons()
                    else:
                        # Go back to main menu
                        print("Keyboard back pressed - returning to Pixel Typers main menu")
                        return "BACK_TO_MAIN"
            
            # Handle button events
            for button in buttons:
                if button.handle_event(event):
                    # Button was clicked - handle specific button actions
                    print(f"Button clicked: {button.button_name}")
                    
                    # Handle back button click
                    if button.button_name == "BackButton":
                        if current_state == DIFFICULTY_SCREEN:
                            # Go back to selection screen
                            print("Back button clicked - returning to selection screen")
                            current_state = SELECTION_SCREEN
                            buttons = initialize_buttons()
                        else:
                            # Go back to main menu
                            print("Back button clicked - returning to Pixel Typers main menu")
                            return "BACK_TO_MAIN"
                    
                    # Handle practice button click
                    elif button.button_name == "PracticeBTN":
                        print("Practice button clicked - showing difficulty selection")
                        current_state = DIFFICULTY_SCREEN
                        buttons = initialize_difficulty_buttons()
                        print(f"Switched to difficulty screen with {len(buttons)} buttons")
                    
                    # Handle multiplayer button click
                    elif button.button_name == "MultiplayerBTN":
                        print("Multiplayer button clicked - multiplayer mode selected")
                        # Add multiplayer mode functionality here in future phases
                    
                    # Handle difficulty button clicks
                    elif button.button_name in ["EasyBTN", "NormalBTN", "HardBTN"]:
                        difficulty = button.button_name.replace("BTN", "")
                        print(f"Difficulty button clicked: {difficulty}")
                        
                        # Launch typing game with selected difficulty
                        if TYPING_GAME_AVAILABLE:
                            print(f"Launching typing game with difficulty: {difficulty}")
                            result = TheTypingGame.main(difficulty)
                            
                            # Handle return from typing game
                            if result == "BACK_TO_DIFFICULTY":
                                print("Returned from typing game to difficulty selection")
                                # Stay on difficulty screen
                                current_state = DIFFICULTY_SCREEN
                                buttons = initialize_difficulty_buttons()
                            else:
                                # If game ended normally, return to difficulty selection
                                current_state = DIFFICULTY_SCREEN
                                buttons = initialize_difficulty_buttons()
                        else:
                            print("ERROR: TheTypingGame module not available")
        
        # Clear screen with custom background color
        screen.fill(BACKGROUND_COLOR)
        
        # Draw buttons based on current state
        for button in buttons:
            button.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    print("Gameplay.py main() function completed")
    return None  # Return None if no specific action was taken

# Entry point for the gameplay module
def run_gameplay():
    """Entry point that can be called from Pixel Typers.py"""
    try:
        result = main()
        return result  # Return "BACK_TO_MAIN" if back button was clicked
    except Exception as e:
        print(f"Error in gameplay module: {e}")
        return None

def test_buttons():
    """Test function to verify button functionality."""
    print("Testing button functionality...")
    
    # Test button creation
    buttons = initialize_buttons()
    print(f"Created {len(buttons)} buttons:")
    for btn in buttons:
        print(f"  - {btn.button_name}: {btn.rect}")
    
    # Test button states
    print("\nTesting button states:")
    for btn in buttons:
        print(f"  {btn.button_name}:")
        print(f"    - Enabled: {btn.enabled}")
        print(f"    - Has images: {btn.normal_image is not None}")
        print(f"    - Position: ({btn.rect.x}, {btn.rect.y})")
    
    # Test button images
    practice_image_path = "images/PracticeBTN.png"
    multiplayer_image_path = "images/MultiplayerBTN.png"
    back_image_path = "images/Back Button 1.png"
    
    print(f"\nPractice button image exists: {os.path.exists(practice_image_path)}")
    print(f"Multiplayer button image exists: {os.path.exists(multiplayer_image_path)}")
    print(f"Back button image exists: {os.path.exists(back_image_path)}")
    
    # Test button positions (vertically aligned, higher positioning)
    practice_button = next((btn for btn in buttons if btn.button_name == "PracticeBTN"), None)
    multiplayer_button = next((btn for btn in buttons if btn.button_name == "MultiplayerBTN"), None)
    back_button = next((btn for btn in buttons if btn.button_name == "BackButton"), None)
    
    if practice_button and multiplayer_button and back_button:
        expected_x = (SCREEN_WIDTH - BUTTON_WIDTH) // 2  # Both buttons centered horizontally
        expected_practice_y = BUTTON_START_Y
        expected_multiplayer_y = BUTTON_START_Y + BUTTON_HEIGHT + BUTTON_SPACING
        
        print(f"\nButton positioning test:")
        print(f"Practice button position: ({practice_button.rect.x}, {practice_button.rect.y}) (expected: ({expected_x}, {expected_practice_y}))")
        print(f"Multiplayer button position: ({multiplayer_button.rect.x}, {multiplayer_button.rect.y}) (expected: ({expected_x}, {expected_multiplayer_y}))")
        print(f"Back button position: ({back_button.rect.x}, {back_button.rect.y}) (expected: ({BACK_BUTTON_PADDING}, {BACK_BUTTON_PADDING}))")
        print(f"Vertical spacing: {multiplayer_button.rect.y - (practice_button.rect.y + practice_button.rect.height)} (expected: {BUTTON_SPACING})")
        print(f"Buttons positioned higher: Start Y = {BUTTON_START_Y} (Screen height // 4)")
    
    print("\nButton test completed. Run main() to start the game.")

# Run test if script is executed directly
if __name__ == "__main__":
    test_buttons()
    main()
    # Uncomment the line below to run button tests
    # test_buttons()
    main()
