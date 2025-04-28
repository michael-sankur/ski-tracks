import streamlit as st
import custom_time_range
from providers import PROVIDERS
from generate_animation import generate_animation

import numpy as np
import pandas as pd

from custom_map_bounds import get_custom_map_bounds
from custom_time_range import get_custom_time_range
from util import get_params_hash


def show_animation_options(
    df_selected_tracks,
    default_lat_padding=0.125,
    default_lon_padding=0.125
):
    """
    Show the animation options section in the Streamlit app.
    Parameters:
        df_selected_tracks (pd.DataFrame): DataFrame containing the selected GPX tracks.
        default_lat_padding (float): Default latitude padding for map bounds.
        default_lon_padding (float): Default longitude padding for map bounds.
    """

    st.header("Generate an Animation")
    st.write("Create an animated visualization of the GPX tracks over time. You can customize the animation settings such as duration, FPS, and map style.")
    
    anim_col_01, anim_col_02, anim_col_03 = st.columns(3)
    
    with anim_col_01:
        st.subheader("Map Settings")
        anim_fig_width = st.number_input("Animation width (inches):", min_value=6.0, max_value=18.0, value=12.0, step=0.5, format="%.1f", key="anim_fig_width")
        anim_map_style = st.selectbox("Map Style", list(PROVIDERS.keys()), index=12, key="anim_map_style")
        anim_lat_padding = st.number_input("Latitude Padding", min_value=0.0, max_value=1.0, value=0.125, step=0.005, format="%.3f",key="anim_lat_padding")
        anim_lon_padding = st.number_input("Longitude Padding", min_value=0.0, max_value=1.0, value=0.125, step=0.005, format="%.3f", key="anim_lon_padding")

        track_lat_delta = df_selected_tracks["latitude"].max() - df_selected_tracks["latitude"].min()
        track_lon_delta = df_selected_tracks["longitude"].max() - df_selected_tracks["longitude"].min()

        anim_lat_min = df_selected_tracks["latitude"].min() - anim_lat_padding*track_lat_delta
        anim_lat_max = df_selected_tracks["latitude"].max() + anim_lat_padding*track_lat_delta
        anim_lon_min = df_selected_tracks["longitude"].min() - anim_lon_padding*track_lon_delta
        anim_lon_max = df_selected_tracks["longitude"].max() + anim_lon_padding*track_lon_delta
        if df_selected_tracks is not None and not df_selected_tracks.empty:
            anim_lat_min, anim_lat_max, anim_lon_min, anim_lon_max = get_custom_map_bounds(
                df_selected_tracks,
                prefix="anim",
                lat_padding=anim_lat_padding,
                lon_padding=anim_lon_padding
            )

    with anim_col_02:
        st.subheader("Data Settings")

        anim_show_time = st.checkbox("Show time", value=True, key="anim_show_time")
        anim_show_legend = st.checkbox("Show legend", value=False, key="anim_show_legend")            
        # anim_show_start_end_points = st.checkbox("Show start and end points", value=False, key="anim_show_start_end")
        anim_show_start_end_points = False
        anim_show_coordinates = st.checkbox("Show coordinates", value=False, key="anim_show_coordinates")
        anim_line_width = st.slider("Line Width", min_value=1, max_value=6, value=3, step=1, key="anim_line_width")
        anim_marker_size = st.slider("Marker Size", min_value=2, max_value=12, value=6, step=1, key="anim_marker_size")

        anim_start_seconds = 0
        anim_end_seconds = 24 * 3600
        if df_selected_tracks is not None and not df_selected_tracks.empty:
            anim_start_seconds, anim_end_seconds = get_custom_time_range(df_selected_tracks=df_selected_tracks, prefix="anim")
    
    with anim_col_03:
        st.subheader("Animation Settings")

        anim_duration = st.slider("Animation length (seconds)", min_value=10, max_value=60, value=20, step=2, key="anim_duration")
        anim_fps = st.slider("Frames per second", min_value=10, max_value=48, value=24, step=2, key="anim_fps")
        anim_num_days = int(max(np.ceil(df_selected_tracks["elapsed_seconds"].max() / (24*3600)), 1))
        anim_trail_duration = 60*60*st.slider(
            "Trail duration (hours)",
            min_value=0,
            max_value=int(anim_num_days*24),
            value=24,
            step=1,
            key="anim_trail_hours"
        )                    
        anim_dpi = st.slider("Resolution (DPI)", min_value=100, max_value=300, value=150, step=25, key="anim_dpi")
        
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        anim_title = st.text_input("Title", "", key="anim_title")

    # Return parameters as a dictionary
    return {
        "anim_map_style": anim_map_style,
        "anim_fig_width": anim_fig_width,
        "anim_lat_min": anim_lat_min,
        "anim_lat_max": anim_lat_max,
        "anim_lon_min": anim_lon_min,
        "anim_lon_max": anim_lon_max,
        "anim_show_time": anim_show_time,
        "anim_show_legend": anim_show_legend,
        # "anim_show_start_end_points": anim_show_start_end_points,
        "anim_show_coordinates": anim_show_coordinates,
        "anim_marker_size": anim_marker_size,
        "anim_line_width": anim_line_width,
        "anim_start_seconds": anim_start_seconds,
        "anim_end_seconds": anim_end_seconds,
        "anim_duration": anim_duration,
        "anim_fps": anim_fps,
        "anim_trail_duration": anim_trail_duration,
        "anim_dpi": anim_dpi,
        "anim_title": anim_title,
    }


def generate_display_animation(
        df_selected_tracks,
        anim_params,
        selected_tracks,
        session_key_prefix="anim"
):
    """Generate animation based on parameters"""
    
    # Use the appropriate session state variables based on the prefix
    animation_generated_key = f"{session_key_prefix}_generated"
    animation_file_key = "animation_file"  # Keep as global for file management
    animation_bytes_key = "animation_bytes"  # Keep as global for binary data
    params_hash_key = f"{session_key_prefix}_params_hash"
    current_params_key = f"{session_key_prefix}_current_params"
    
    # Initialize session state variables if they don't exist
    if animation_generated_key not in st.session_state:
        st.session_state[animation_generated_key] = False
    if animation_file_key not in st.session_state:
        st.session_state[animation_file_key] = None
    if animation_bytes_key not in st.session_state:
        st.session_state[animation_bytes_key] = None
    if params_hash_key not in st.session_state:
        st.session_state[params_hash_key] = ""
    if current_params_key not in st.session_state:
        st.session_state[current_params_key] = {}
    
    # Get parameter hash for comparison
    current_hash = get_params_hash(anim_params)
    params_changed = current_hash != st.session_state[params_hash_key]
    
    # Show parameter change notification if applicable
    if params_changed and st.session_state[animation_generated_key]:
        st.info("Animation parameters have changed. Click 'Generate Animation' to update the visualization.")
    
    # Create button for generating animation
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        generate_anim_clicked = st.button(
            "Generate Animation",
            disabled=(df_selected_tracks is None or df_selected_tracks.empty))
    
        # Create a container for the animation display
        animation_container = st.container()
        
        # Generate new animation if button clicked
        if generate_anim_clicked:
            with st.spinner("Generating animation..."):
                try:
                    # Get the animation parameters (removing the prefix for function call)
                    animation_params = {k.replace("anim_", ""): v for k, v in anim_params.items()}
                    
                    animation_file = generate_animation(
                        df_selected_tracks,
                        mode="track",
                        map_style=anim_params["anim_map_style"],
                        lat_min=anim_params["anim_lat_min"],
                        lat_max=anim_params["anim_lat_max"],
                        lon_min=anim_params["anim_lon_min"],
                        lon_max=anim_params["anim_lon_max"],
                        fig_width=anim_params["anim_fig_width"],
                        duration=anim_params["anim_duration"],
                        fps=anim_params["anim_fps"],
                        start_time=anim_params["anim_start_seconds"],
                        end_time=anim_params["anim_end_seconds"],
                        dpi=anim_params["anim_dpi"],
                        trail_duration=anim_params["anim_trail_duration"],
                        marker_size=anim_params["anim_marker_size"],
                        line_width=anim_params["anim_line_width"],
                        title=anim_params["anim_title"],
                        show_time=anim_params["anim_show_time"],
                        show_legend=anim_params["anim_show_legend"],
                        show_coordinates=anim_params["anim_show_coordinates"]
                    )
                    
                    # Store the animation file path and load the bytes
                    st.session_state[animation_file_key] = animation_file
                    with open(animation_file, "rb") as video_file:
                        st.session_state[animation_bytes_key] = video_file.read()
                    
                    # Update session state
                    st.session_state[animation_generated_key] = True
                    st.session_state[params_hash_key] = current_hash
                    st.session_state[current_params_key] = anim_params.copy()
                    
                except Exception as e:
                    st.error(f"Error generating animation: {e}")
                    st.session_state[animation_generated_key] = False
                    st.session_state[animation_bytes_key] = None
        
        # Display the animation in the container
        with animation_container:
            if st.session_state[animation_bytes_key] is not None:
                st.video(st.session_state[animation_bytes_key])
                
                # Add download button
                if st.session_state[animation_file_key] is not None:
                    from util import get_binary_file_downloader_html
                    download_html = get_binary_file_downloader_html(
                        st.session_state[animation_file_key], 
                        "Animation"
                    )
                    st.markdown(download_html, unsafe_allow_html=True)
                    
            elif not st.session_state[animation_generated_key]:
                st.info("Click 'Generate Animation' to create visualization")
