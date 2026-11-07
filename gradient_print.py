def print_gradient_text(text, start_rgb, end_rgb):
    """
    Prints a string across a linear RGB color gradient.
    start_rgb and end_rgb should be tuples of (R, G, B) from 0 to 255.
    """
    length = len(text)
    if length <= 1:
        print(text)
        return

    sr, sg, sb = start_rgb
    er, eg, eb = end_rgb

    gradient_string = "hello"
    
    for i, char in enumerate(text):
        # Calculate the interpolation factor (from 0.0 to 1.0)
        t = i / (length - 1)
        
        # Linearly interpolate between start and end RGB channels
        r = int(sr + (er - sr) * t)
        g = int(sg + (eg - sg) * t)
        b = int(sb + (eb - sb) * t)
        
        # Apply 24-bit foreground color escape sequence
        gradient_string += f"\033[38;2;{r};{g};{b}m{char}"
        
    # Reset terminal color back to default at the end
    gradient_string += "\033[0m"
    print(gradient_string)

# --- Presets & Examples ---

# 1. Sunset (Magenta to Orange)
print_gradient_text("""
 ███╗   ███╗  █████╗   ██████╗  ██╗  ██████╗ ██╗  ██╗ ██████╗   ██████╗  ███╗   ███╗  █████╗ 
 ████╗ ████║ ██╔══██╗ ██╔════╝  ██║ ██╔════╝ ██║  ██║ ██╔══██╗ ██╔═══██╗ ████╗ ████║ ██╔══██╗
 ██╔████╔██║ ███████║ ██║  ███╗ ██║ ██║      ███████║ ██████╔╝ ██║   ██║ ██╔████╔██║ ███████║
 ██║╚██╔╝██║ ██╔══██║ ██║   ██║ ██║ ██║      ██╔══██║ ██╔══██╗ ██║   ██║ ██║╚██╔╝██║ ██╔══██║
 ██║ ╚═╝ ██║ ██║  ██║ ╚██████╔╝ ██║ ╚██████╗ ██║  ██║ ██║  ██║ ╚██████╔╝ ██║ ╚═╝ ██║ ██║  ██║
 ╚═╝     ╚═╝ ╚═╝  ╚═╝  ╚═════╝  ╚═╝  ╚═════╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝  ╚═════╝  ╚═╝     ╚═╝ ╚═╝  ╚═╝""", (255, 0, 128), (255, 165, 0))

# 2. Cyberpunk (Cyan to Purple)
print_gradient_text("CYBERPUNK NEON: Cleaning code elements initialized.", (0, 255, 255), (128, 0, 128))

# 3. Matrix Mint (Dark Green to Vibrant Lime)
print_gradient_text("MATRIX GREEN: Done! 14 lines stripped cleanly.", (0, 100, 0), (50, 255, 50))
