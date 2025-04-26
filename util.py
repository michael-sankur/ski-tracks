#

import base64
import hashlib
import json
import matplotlib.colors as mcolors
import os
import streamlit as st


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

def get_binary_file_downloader_html(bin_file, file_label="File"):
    """Create HTML for a download link for binary file"""
    with open(bin_file, "rb") as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f"""<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}" class="btn btn-primary">Download {file_label}</a>"""
    return href

def get_params_hash(params):
    """Generate a hash of a parameter dictionary"""
    params_str = json.dumps(params, sort_keys=True)
    return hashlib.md5(params_str.encode()).hexdigest()

def check_params_changed(current_params, hash_key):
    """Check if parameters have changed from last generation"""
    current_hash = get_params_hash(current_params)
    params_changed = current_hash != st.session_state[hash_key]
    return params_changed, current_hash