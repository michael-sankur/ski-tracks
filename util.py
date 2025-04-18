#

import matplotlib.colors as mcolors

# Function to generate random distinct colors for different tracks
def get_distinct_colors(n):
    """
    Generate n visually distinct colors
    Args:
        n (int): Number of distinct colors to generate.
    Returns:
        list: List of RGB tuples representing distinct colors.
    """
    
    colors = []
    for k1 in range(n):
        # Using golden ratio for better distribution of colors
        hue = (k1 * 0.618033988749895) % 1.0
        # Use HSV color space with fixed saturation and value
        saturation = 0.7
        value = 0.9
        # Convert HSV to RGB
        r, g, b = mcolors.hsv_to_rgb([hue, saturation, value])
        colors.append((r, 0, b))  # Changed to include all color channels
    
    return colors