import pygame
import sys
import os
import math
try:
    import imageio
except ImportError:
    print("imageio module not found. Please install it with: pip install imageio")
    sys.exit(1)

# Import Gameplay module with error handling
try:
    import Gameplay
    GAMEPLAY_MODULE_AVAILABLE = True
    print("Gameplay module loaded successfully")
except ImportError as e:
    print(f"Could not load Gameplay module: {e}")
    GAMEPLAY_MODULE_AVAILABLE = False
except Exception as e:
    print(f"Error loading Gameplay module: {e}")
    GAMEPLAY_MODULE_AVAILABLE = False

# Initialize pygame
pygame.init()

# Screen dimensions based on the image
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Typers")

# Colors
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 120, 255)  # Blue color for buttons

# For button fading effect
button_fade_speed = 5  # Speed of color transition
button_color_value = 255  # Start with full yellow
button_fade_direction = -1  # Start by fading to black (-1), then to yellow (1)

# Game states
TITLE_SCREEN = 0
GAME_SCREEN = 1
SETTINGS_SCREEN = 2
TRANSITION_SCREEN = -1  # Special state for transitions
current_state = TITLE_SCREEN

# Settings
music_enabled = True
sound_enabled = True
settings_popup_alpha = 0  # For fade-in effect of settings popup
settings_popup_speed = 15
settings_popup_max_alpha = 200  # Maximum alpha for dimming background

# For fade transitions
transitioning = False
transition_target = GAME_SCREEN  # Target state after transition
fade_alpha = 255  # Alpha value for fade effect (0-255)
fade_speed = 8  # Speed of fade animation
fading_out = False  # Flag to indicate if elements are fading out
fading_in = False  # Flag to indicate if elements are fading in
title_visible_during_transition = True  # Keep title visible during transitions

# Loading animation properties
loading_animation_active = False
loading_dots = 0
loading_animation_speed = 30  # milliseconds between dot updates
last_loading_update = 0
# Gameplay launch state
gameplay_launch_initiated = False

# Load the GIF background
background_color = (20, 20, 40)  # Fallback color
background_path = os.path.join('images', 'BACKGROUND PIXELTYPERS.gif')
try:
    # Using imageio to handle GIF animation
    gif = imageio.mimread(background_path)
    # Convert to pygame surfaces
    pygame_frames = []
    for frame in gif:
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        # Scale to fit screen if needed
        frame_surface = pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame_frames.append(frame_surface)
    current_frame = 0
    total_frames = len(pygame_frames)
    frame_delay = 100  # milliseconds between frames
    last_frame_time = pygame.time.get_ticks()
    has_background_gif = True
    print("Successfully loaded background GIF with", total_frames, "frames")
except Exception as e:
    print("Could not load background GIF:", e)
    has_background_gif = False

# Load main menu text box and back button
try:
    menu_box_img = pygame.image.load(os.path.join('images', 'MainMenuTXTBOX.png')).convert_alpha()
    menu_box_img = pygame.transform.scale(menu_box_img, (400, 350))  # Adjust size as needed
    has_menu_box = True
    
    # Load back button image
    back_button_img = pygame.image.load(os.path.join('images', 'Back Button 1.png')).convert_alpha()
    # Get original dimensions to preserve aspect ratio
    original_width, original_height = back_button_img.get_size()
    aspect_ratio = original_width / original_height
    # Set target height and calculate width to maintain aspect ratio
    target_height = 35  # Scaled down from 50
    target_width = int(target_height * aspect_ratio)
    back_button_img = pygame.transform.scale(back_button_img, (target_width, target_height))
    has_back_button = True
except Exception as e:
    print("Could not load images:", e)
    has_menu_box = False
    has_back_button = False

# Font for the title and buttons
font_path = os.path.join('fonts', 'fs-pixel-sans-unicode-regular.ttf')
try:
    # Use the custom pixel font
    title_font = pygame.font.Font(font_path, 72)  # Pixel font, size 72
    button_font = pygame.font.Font(font_path, 36)  # Pixel font, size 36
    menu_font = pygame.font.Font(font_path, 28)  # Smaller font for menu items
except:
    # Fallback to default font if the custom font fails to load
    print("Could not load custom font. Using default font instead.")
    title_font = pygame.font.SysFont('Arial', 72)
    button_font = pygame.font.SysFont('Arial', 36)
    menu_font = pygame.font.SysFont('Arial', 28)

# Main menu buttons
menu_items = ["START GAME", "SETTINGS", "EXIT"]
menu_rects = []
menu_hover = [False] * len(menu_items)
menu_original_rects = []  # Store original rectangles for non-hover state

# Button dimensions
button_width = 200
button_height = 60
button_hover_scale = 1.15  # Scale factor for hover effect

# Calculate positions for menu items
# START GAME at the top center
start_rect = pygame.Rect(
    SCREEN_WIDTH // 2 - button_width // 2,
    SCREEN_HEIGHT // 3 + 20,
    button_width,
    button_height
)
menu_rects.append(start_rect)
menu_original_rects.append(start_rect.copy())  # Store original rect

# SETTINGS in the middle left
settings_rect = pygame.Rect(
    SCREEN_WIDTH // 2 - button_width // 2,
    SCREEN_HEIGHT // 2 + 40,
    button_width,
    button_height
)
menu_rects.append(settings_rect)
menu_original_rects.append(settings_rect.copy())  # Store original rect

# EXIT at the bottom
exit_rect = pygame.Rect(
    SCREEN_WIDTH // 2 - button_width // 2,
    SCREEN_HEIGHT // 2 + 140,
    button_width,
    button_height
)
menu_rects.append(exit_rect)
menu_original_rects.append(exit_rect.copy())  # Store original rect

# Button properties for title screen
button_text = "Click to Continue"
button_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 300, 50)
button_hover = False
button_fade_value = 255  # Start with full yellow (255)
button_fade_direction = -1  # Start by fading to black (-1), then to yellow (1)
button_fade_speed = 5  # Speed of color transition

def can_load_gameplay():
    """Check if the Gameplay module can be loaded properly."""
    try:
        # Check if Gameplay module is available
        if not GAMEPLAY_MODULE_AVAILABLE:
            return False, "Gameplay module not available"
        
        # Check if Gameplay has required attributes
        if not hasattr(Gameplay, 'main'):
            return False, "Gameplay module missing main() function"
        
        return True, "Gameplay module ready"
        
    except Exception as e:
        return False, f"Error checking Gameplay module: {e}"

def reset_transition_state():
    """Reset all transition-related variables to their initial state."""
    global transitioning, loading_animation_active, fade_alpha, fading_out, fading_in, current_state, gameplay_launch_initiated, transition_target
    transitioning = False
    loading_animation_active = False
    fade_alpha = 255
    fading_out = False
    fading_in = False
    current_state = GAME_SCREEN
    gameplay_launch_initiated = False
    transition_target = GAME_SCREEN
    print("Transition state reset to main menu")

def transition_to_gameplay():
    """Handle the transition to Gameplay.py module with proper error handling."""
    global loading_animation_active, loading_dots, last_loading_update
    
    try:
        # Check if Gameplay module can be loaded
        can_load, message = can_load_gameplay()
        if not can_load:
            print(f"ERROR: {message}")
            return False
        
        # Attempt to run the Gameplay module
        print("Loading Gameplay module...")
        
        # Run the Gameplay module's main function and capture result
        print("Running Gameplay.main()...")
        gameplay_result = Gameplay.main()
        
        print("Gameplay module finished with result:", gameplay_result)
        # Propagate explicit back signal; otherwise return True
        return gameplay_result if gameplay_result == "BACK_TO_MAIN" else True
        
    except Exception as e:
        print(f"ERROR: Failed to load Gameplay module: {e}")
        return False

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Mouse events
        if event.type == pygame.MOUSEMOTION:
            # Check if mouse is over the button
            if current_state == TITLE_SCREEN:
                if button_rect.collidepoint(event.pos):
                    button_hover = True
                else:
                    button_hover = False
            
            # Check if mouse is over any menu items
            elif current_state == GAME_SCREEN:
                for i, rect in enumerate(menu_rects):
                    # Check if mouse is over the original button area
                    was_hovering = menu_hover[i]
                    menu_hover[i] = menu_original_rects[i].collidepoint(event.pos)
                    
                    # If hover state changed, update the button rectangle
                    if was_hovering != menu_hover[i]:
                        if menu_hover[i]:
                            # Enlarge the button
                            center_x = menu_original_rects[i].centerx
                            center_y = menu_original_rects[i].centery
                            new_width = int(button_width * button_hover_scale)
                            new_height = int(button_height * button_hover_scale)
                            menu_rects[i] = pygame.Rect(
                                center_x - new_width // 2,
                                center_y - new_height // 2,
                                new_width,
                                new_height
                            )
                        else:
                            # Restore original size
                            menu_rects[i] = menu_original_rects[i].copy()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Only process clicks if not transitioning
            if not transitioning:
                # Check if button is clicked
                if current_state == TITLE_SCREEN and button_rect.collidepoint(event.pos):
                    # Start fade animation to main menu
                    transitioning = True
                    transition_target = GAME_SCREEN
                    # Reset fade values
                    fade_alpha = 255
                    fading_out = True
                    fading_in = False
                    # Keep title visible, fade out other elements
                    current_state = TRANSITION_SCREEN  # Use the defined constant for transition
                    print("Transitioning to main menu with fade!")
                
                # Check if any menu item is clicked
                elif current_state == GAME_SCREEN and not transitioning:
                    for i, rect in enumerate(menu_rects):
                        if rect.collidepoint(event.pos):
                            if i == 0:  # START GAME
                                print("Starting game!")
                                # Start transition to Gameplay.py
                                transitioning = True
                                transition_target = "GAMEPLAY"  # Special target for Gameplay module
                                # Reset fade values
                                fade_alpha = 255
                                fading_out = True
                                fading_in = False
                                # Keep title visible, fade out other elements
                                current_state = TRANSITION_SCREEN
                                # Prepare gameplay launch flags
                                gameplay_launch_initiated = False
                                print("Transitioning to Gameplay.py with fade!")
                            elif i == 1:  # SETTINGS
                                # Switch directly to settings screen with popup effect
                                current_state = SETTINGS_SCREEN
                                # Reset settings popup alpha for fade-in effect
                                settings_popup_alpha = 0
                                print("Opening settings popup!")
                            elif i == 2:  # EXIT
                                running = False
                                print("Exiting game!")
                            elif i == 0:  # START GAME
                                print("Loading Gameplay module...")
                                # Ensure pygame is properly initialized for Gameplay
                                if not pygame.get_init():
                                    pygame.init()
                                # Import and run the Gameplay module
                                try:
                                    import Gameplay
                                    print("Running Gameplay.main()...")
                                    Gameplay.main()
                                    print("Gameplay module loaded successfully!")
                                except ImportError:
                                    print("Gameplay module not found!")
                                except Exception as e:
                                    print("Error running Gameplay module:", e)
                
                # Handle clicks in Settings screen
                elif current_state == SETTINGS_SCREEN:
                    # Back button (arrow in top-left of the popup)
                    # Calculate popup dimensions to match rendering code
                    popup_width, popup_height = 400, 300
                    popup_rect = pygame.Rect(
                        SCREEN_WIDTH//2 - popup_width//2,
                        SCREEN_HEIGHT//2 - popup_height//2,
                        popup_width, 
                        popup_height
                    )
                    # Position back button inside the popup
                    back_rect = pygame.Rect(
                        popup_rect.left + 20,  # 20px from left edge of popup
                        popup_rect.top + 20,   # 20px from top edge of popup
                        50, 50
                    )
                    if back_rect.collidepoint(event.pos):
                        # Instantly return to main menu
                        current_state = GAME_SCREEN
                        print("Returning to main menu!")
                    
                    # Music checkbox
                    music_checkbox_rect = pygame.Rect(SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 - 50, 30, 30)
                    if music_checkbox_rect.collidepoint(event.pos):
                        music_enabled = not music_enabled
                        print(f"Music {'enabled' if music_enabled else 'disabled'}")
                    
                    # Sound checkbox
                    sound_checkbox_rect = pygame.Rect(SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 + 30, 30, 30)
                    if sound_checkbox_rect.collidepoint(event.pos):
                        sound_enabled = not sound_enabled
                        print(f"Sound {'enabled' if sound_enabled else 'disabled'}")
    
    # Display background (either GIF animation or solid color)
    if has_background_gif:
        # Check if it's time to advance to the next frame
        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time > frame_delay:
            current_frame = (current_frame + 1) % total_frames
            last_frame_time = current_time
        
        # Display the current frame
        screen.blit(pygame_frames[current_frame], (0, 0))
    else:
        # Fallback to solid color if GIF couldn't be loaded
        screen.fill(background_color)
    
    # Draw based on current state
    if current_state == TITLE_SCREEN:
        # Draw title
        title_text = title_font.render("PIXEL TYPERS", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        screen.blit(title_text, title_rect)
        
        # Handle button fading effect when hovered
        if button_hover:
            # Update fade value based on direction and speed
            button_fade_value += button_fade_direction * button_fade_speed
            
            # Change direction when reaching limits
            if button_fade_value <= 0:  # Fully black
                button_fade_value = 0
                button_fade_direction = 1  # Start fading to yellow
            elif button_fade_value >= 255:  # Fully yellow
                button_fade_value = 255
                button_fade_direction = -1  # Start fading to black
            
            # Create fading color between yellow and black
            button_color = (button_fade_value, button_fade_value, 0)  # R and G fade together
        else:
            # Reset to yellow when not hovering
            button_color = YELLOW
            button_fade_value = 255
            button_fade_direction = -1
        
        # No background rectangle - making it transparent
        
        # Draw button text with fading color
        button_surface = button_font.render(button_text, True, button_color)
        button_text_rect = button_surface.get_rect(center=button_rect.center)
        screen.blit(button_surface, button_text_rect)
    
    elif current_state == GAME_SCREEN:
        # Main Menu Screen
        # Draw title (always visible, not affected by fade)
        title_text = title_font.render("PIXEL TYPERS", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//6))
        screen.blit(title_text, title_rect)
        
        # Draw menu items with blue button boxes and fade effect
        for i, (item, rect) in enumerate(zip(menu_items, menu_rects)):
            # Determine button color based on transition state
            if transitioning and i == 0:  # START GAME button during transition
                button_color = (80, 100, 150)  # Disabled/darker blue
                text_color = GRAY  # Gray text for disabled state
            else:
                button_color = BLUE  # Normal blue
                # Change text color based on hover state
                text_color = YELLOW if menu_hover[i] else WHITE
            
            # Draw button box
            button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(button_surface, button_color, button_surface.get_rect(), border_radius=5)
            
            # Add a 3D effect with a darker border
            pygame.draw.rect(button_surface, (0, 80, 200), button_surface.get_rect(), width=3, border_radius=5)
            
            # Apply fade effect during transition
            if transitioning and not title_visible_during_transition:
                button_surface.set_alpha(fade_alpha)
            
            screen.blit(button_surface, rect)
            
            # Render text
            text_surface = menu_font.render(item, True, text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            
            # Apply fade effect to text during transition
            if transitioning and not title_visible_during_transition:
                text_surface.set_alpha(fade_alpha)
            
            # Draw text
            screen.blit(text_surface, text_rect)
    
    elif current_state == SETTINGS_SCREEN:
        # First draw the main menu in the background
        # Draw title
        title_text = title_font.render("PIXEL TYPERS", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//6))
        screen.blit(title_text, title_rect)
        
        # Draw menu items with blue button boxes
        for i, (item, rect) in enumerate(zip(menu_items, menu_rects)):
            # Draw blue button box
            pygame.draw.rect(screen, BLUE, rect, border_radius=5)
            pygame.draw.rect(screen, (0, 80, 200), rect, width=3, border_radius=5)
            
            # Render text
            text_surface = menu_font.render(item, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            
            # Draw text
            screen.blit(text_surface, text_rect)
        
        # Animate settings popup alpha
        if settings_popup_alpha < settings_popup_max_alpha:
            settings_popup_alpha += settings_popup_speed
            if settings_popup_alpha > settings_popup_max_alpha:
                settings_popup_alpha = settings_popup_max_alpha
        
        # Create a semi-transparent overlay to dim the background
        dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        dim_surface.fill((20, 30, 70))  # Dark blue color
        
        # Apply fade effect during transition
        if transitioning and not title_visible_during_transition:
            dim_surface.set_alpha(fade_alpha)
        else:
            dim_surface.set_alpha(settings_popup_alpha)
        
        screen.blit(dim_surface, (0, 0))
        
        # Draw settings popup with fade effect
        popup_width, popup_height = 400, 300
        popup_rect = pygame.Rect(
            SCREEN_WIDTH//2 - popup_width//2,
            SCREEN_HEIGHT//2 - popup_height//2,
            popup_width, 
            popup_height
        )
        
        # Create popup surface with fade effect
        popup_surface = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        pygame.draw.rect(popup_surface, (40, 60, 120), popup_surface.get_rect(), border_radius=10)
        pygame.draw.rect(popup_surface, (60, 80, 160), popup_surface.get_rect(), width=3, border_radius=10)
        
        # Apply fade effect during transition
        if transitioning and not title_visible_during_transition:
            popup_surface.set_alpha(fade_alpha)
        
        screen.blit(popup_surface, popup_rect)
        
        # Settings title with fade effect
        settings_text = button_font.render("SETTINGS", True, WHITE)
        settings_rect = settings_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        
        # Apply fade effect to settings title during transition
        if transitioning and not title_visible_during_transition:
            settings_text.set_alpha(fade_alpha)
        
        screen.blit(settings_text, settings_rect)
        
        # Back button (arrow in top-left of the popup) with fade effect
        back_rect = pygame.Rect(
            popup_rect.left + 20,  # 20px from left edge of popup
            popup_rect.top + 20,   # 20px from top edge of popup
            50, 50
        )
        if has_back_button:
            if transitioning and not title_visible_during_transition:
                # Create a surface for the back button with fade effect
                back_button_surface = pygame.Surface(back_button_img.get_size(), pygame.SRCALPHA)
                back_button_surface.blit(back_button_img, (0, 0))
                back_button_surface.set_alpha(fade_alpha)
                screen.blit(back_button_surface, back_rect)
            else:
                screen.blit(back_button_img, back_rect)
        else:
            # Fallback if image not available
            pygame.draw.rect(screen, BLUE, back_rect, border_radius=5)
            back_text = button_font.render("←", True, WHITE)
            back_text_rect = back_text.get_rect(center=back_rect.center)
            
            # Apply fade effect to back button text during transition
            if transitioning and not title_visible_during_transition:
                back_text.set_alpha(fade_alpha)
            
            screen.blit(back_text, back_text_rect)
        
        # Music option with fade effect
        music_text = menu_font.render("Music", True, WHITE)
        music_rect = music_text.get_rect(midright=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 35))
        
        # Apply fade effect to music text during transition
        if transitioning and not title_visible_during_transition:
            music_text.set_alpha(fade_alpha)
        
        screen.blit(music_text, music_rect)
        
        # Music checkbox with fade effect
        music_checkbox_rect = pygame.Rect(SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 - 50, 30, 30)
        
        # Apply fade effect to checkbox during transition
        if transitioning and not title_visible_during_transition:
            pygame.draw.rect(screen, (80, 100, 200), music_checkbox_rect, border_radius=3)
            if music_enabled:
                # Create checkmark surface with fade effect
                checkmark_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.line(checkmark_surface, WHITE, 
                                 (5, 15),
                                 (13, 25), 3)
                pygame.draw.line(checkmark_surface, WHITE, 
                                 (13, 25),
                                 (25, 5), 3)
                checkmark_surface.set_alpha(fade_alpha)
                screen.blit(checkmark_surface, music_checkbox_rect)
        else:
            pygame.draw.rect(screen, (80, 100, 200), music_checkbox_rect, border_radius=3)
            if music_enabled:
                # Draw checkmark normally
                pygame.draw.line(screen, WHITE, 
                                 (music_checkbox_rect.left + 5, music_checkbox_rect.centery),
                                 (music_checkbox_rect.centerx - 2, music_checkbox_rect.bottom - 5), 3)
                pygame.draw.line(screen, WHITE, 
                                 (music_checkbox_rect.centerx - 2, music_checkbox_rect.bottom - 5),
                                 (music_checkbox_rect.right - 5, music_checkbox_rect.top + 5), 3)
        
        # Sound option with fade effect
        sound_text = menu_font.render("Sound", True, WHITE)
        sound_rect = sound_text.get_rect(midright=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 45))
        
        # Apply fade effect to sound text during transition
        if transitioning and not title_visible_during_transition:
            sound_text.set_alpha(fade_alpha)
        
        screen.blit(sound_text, sound_rect)
        
        # Sound checkbox with fade effect
        sound_checkbox_rect = pygame.Rect(SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 + 30, 30, 30)
        
        # Apply fade effect to sound checkbox during transition
        if transitioning and not title_visible_during_transition:
            pygame.draw.rect(screen, (80, 100, 200), sound_checkbox_rect, border_radius=3)
            if sound_enabled:
                # Create checkmark surface with fade effect
                checkmark_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.line(checkmark_surface, WHITE, 
                                 (5, 15),
                                 (13, 25), 3)
                pygame.draw.line(checkmark_surface, WHITE, 
                                 (13, 25),
                                 (25, 5), 3)
                checkmark_surface.set_alpha(fade_alpha)
                screen.blit(checkmark_surface, sound_checkbox_rect)
        else:
            pygame.draw.rect(screen, (80, 100, 200), sound_checkbox_rect, border_radius=3)
            if sound_enabled:
                # Draw checkmark normally
                pygame.draw.line(screen, WHITE, 
                                 (sound_checkbox_rect.left + 5, sound_checkbox_rect.centery),
                                 (sound_checkbox_rect.centerx - 2, sound_checkbox_rect.bottom - 5), 3)
                pygame.draw.line(screen, WHITE, 
                                 (sound_checkbox_rect.centerx - 2, sound_checkbox_rect.bottom - 5),
                                 (sound_checkbox_rect.right - 5, sound_checkbox_rect.top + 5), 3)
    
    # Handle fade animations for transition state
    if current_state == TRANSITION_SCREEN or transitioning:
        if fading_out:
            # Fade out the current elements
            fade_alpha -= fade_speed
            if fade_alpha <= 0:
                fade_alpha = 0
                fading_out = False
                fading_in = True
                # Switch to target state
                if current_state == TRANSITION_SCREEN:
                    # Special handling for Gameplay transition
                    if transition_target == "GAMEPLAY":
                        # Show loading screen instead of regular fade-in
                        loading_animation_active = True
                        print("Showing loading screen for Gameplay.py...")
                    else:
                        current_state = transition_target
        
        elif fading_in and transition_target != "GAMEPLAY":
            # Fade in the new elements (only for non-gameplay transitions)
            fade_alpha += fade_speed
            if fade_alpha >= 255:
                fade_alpha = 255
                fading_in = False
                transitioning = False
                
                # Handle Gameplay module transition (this shouldn't happen here, but just in case)
                if transition_target == "GAMEPLAY":
                    print("Transition complete, loading Gameplay.py...")
                    result = transition_to_gameplay()
                    print(f"Gameplay returned: {result}")
                    # Always return to main menu after Gameplay finishes
                    reset_transition_state()
    
    # Handle loading screen for Gameplay.py transition
    if loading_animation_active and transition_target == "GAMEPLAY":
        # Create loading screen overlay
        loading_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        loading_surface.fill((0, 0, 0, 200))  # Semi-transparent black
        screen.blit(loading_surface, (0, 0))
        
        # Update loading dots animation
        current_time = pygame.time.get_ticks()
        if current_time - last_loading_update > loading_animation_speed:
            loading_dots = (loading_dots + 1) % 4  # Cycle through 0-3 dots
            last_loading_update = current_time
        
        # Draw loading text
        loading_text = button_font.render("Loading Gameplay Module", True, WHITE)
        loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
        screen.blit(loading_text, loading_rect)
        
        # Draw animated dots
        dots_text = "." * loading_dots + " " * (3 - loading_dots)
        dots_surface = button_font.render(dots_text, True, WHITE)
        dots_rect = dots_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
        screen.blit(dots_surface, dots_rect)
        
        # Attempt to load Gameplay module after showing loading screen
        if not gameplay_launch_initiated:
            gameplay_launch_initiated = True
            print("Loading Gameplay.py module...")
            result = transition_to_gameplay()
            print(f"Gameplay returned: {result}")
            # Always return to main menu after Gameplay finishes (whether back button was clicked or not)
            reset_transition_state()
            current_state = GAME_SCREEN
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()