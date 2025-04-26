import streamlit as st
from providers import PROVIDERS
from generate_animation import generate_animation

import numpy as np
import pandas as pd
import os
import tempfile
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

        # Custom map bounds
        anim_lat_min = 0
        anim_lat_max = 0
        anim_lon_min = 0
        anim_lon_max = 0
        with st.expander("Custom Latitude and Longitude Bounds", expanded=False):
            
            if df_selected_tracks is not None and not df_selected_tracks.empty:

                anim_track_lat_delta = df_selected_tracks["latitude"].max() - df_selected_tracks["latitude"].min()
                anim_track_lon_delta = df_selected_tracks["longitude"].max() - df_selected_tracks["longitude"].min()

                anim_lat_min_default = df_selected_tracks["latitude"].min() - anim_lat_padding*anim_track_lat_delta
                anim_lat_max_default = df_selected_tracks["latitude"].max() + anim_lat_padding*anim_track_lat_delta
                anim_lon_min_default = df_selected_tracks["longitude"].min() - anim_lon_padding*anim_track_lon_delta
                anim_lon_max_default = df_selected_tracks["longitude"].max() + anim_lon_padding*anim_track_lon_delta

                anim_custom_bounds_mode = st.radio(
                    label="Select custom bounds mode:",
                    options=["Use standard lat/lon padding", "Use custom NSEW padding", "Use custom latitude and longitude"],
                    index=0,
                    key="anim_custom_bounds_mode",
                    horizontal=True
                )
                if anim_custom_bounds_mode == "Use standard lat/lon padding":
                    anim_lat_min = anim_lat_min_default
                    anim_lat_max = anim_lat_max_default
                    anim_lon_min = anim_lon_min_default
                    anim_lon_max = anim_lon_max_default

                    st.write(f"Map latitude extents: {anim_lat_min:.4f} to {anim_lat_max:.4f}")
                    st.write(f"Map longitude extents: {anim_lon_min:.4f} to {anim_lon_max:.4f}")

                elif anim_custom_bounds_mode == "Use custom NSEW padding":
                    anim_north_padding = st.number_input("North Padding", min_value=0.0, max_value=1.0, value=anim_lat_padding, step=0.005, format="%.3f", key="anim_north_padding")
                    anim_south_padding = st.number_input("South Padding", min_value=0.0, max_value=1.0, value=anim_lat_padding, step=0.005, format="%.3f", key="anim_south_padding")
                    anim_east_padding = st.number_input("East Padding", min_value=0.0, max_value=1.0, value=anim_lon_padding, step=0.005, format="%.3f", key="anim_east_padding")
                    anim_west_padding = st.number_input("West Padding", min_value=0.0, max_value=1.0, value=anim_lon_padding, step=0.005, format="%.3f", key="anim_west_padding")

                    anim_lat_min = df_selected_tracks["latitude"].min() - anim_south_padding*anim_track_lat_delta
                    anim_lat_max = df_selected_tracks["latitude"].max() + anim_north_padding*anim_track_lat_delta
                    anim_lon_min = df_selected_tracks["longitude"].min() - anim_west_padding*anim_track_lon_delta
                    anim_lon_max = df_selected_tracks["longitude"].max() + anim_east_padding*anim_track_lon_delta

                    st.write(f"Map latitude extents: {anim_lat_min:.4f} to {anim_lat_max:.4f}")
                    st.write(f"Map longitude extents: {anim_lon_min:.4f} to {anim_lon_max:.4f}")
                elif anim_custom_bounds_mode == "Use custom latitude and longitude":                        
                    anim_lat_min = st.number_input("Min Latitude", value=anim_lat_min_default, format="%.4f", step=0.005, key="anim_lat_min")
                    anim_lat_max = st.number_input("Max Latitude", value=anim_lat_max_default, format="%.4f", step=0.005, key="anim_lat_max")
                    anim_lon_min = st.number_input("Min Longitude", value=anim_lon_min_default, format="%.4f", step=0.005, key="anim_lon_min")                        
                    anim_lon_max = st.number_input("Max Longitude", value=anim_lon_max_default, format="%.4f", step=0.005, key="anim_lon_max")
            else:
                st.write("No data available for custom bounds selection. Upload GPX files and select one or more tracks.")

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
        with st.expander("Custom Time Range", expanded=False):
            
            if df_selected_tracks is not None and not df_selected_tracks.empty:

                anim_num_days = np.ceil(df_selected_tracks["elapsed_seconds"].max() / (24*3600))
                anim_num_days = int(max(anim_num_days, 1))

                anim_data_time_min_hour = int(np.floor(df_selected_tracks["elapsed_seconds"].min() / 3600))
                anim_data_time_min_minute = int(np.floor((df_selected_tracks["elapsed_seconds"].min() % 3600) / 60))

                anim_data_time_max_hour = int(np.floor(df_selected_tracks["elapsed_seconds"].max() / 3600 - 24*(anim_num_days-1)))
                anim_data_time_max_minute = int(np.floor((df_selected_tracks["elapsed_seconds"].max() % 3600) / 60))

                st.write(f"Data time range: Day {1} at {anim_data_time_min_hour:02d}:{anim_data_time_min_minute:02d}  -  Day {anim_num_days} at {anim_data_time_max_hour:02d}:{anim_data_time_max_minute:02d}")

                anim_min_time = df_selected_tracks["elapsed_seconds"].min()
                anim_min_time_rounded = anim_min_time - (anim_min_time % (30*60))
                anim_max_time = df_selected_tracks["elapsed_seconds"].max()
                anim_max_time_rounded = anim_max_time - (anim_max_time % (30*60)) + 30*60

                anim_time_options = []
                for hour in range(anim_num_days*24 + 1):
                    for minute in [0, 15, 30, 45]:
                        if hour == anim_num_days*24 and minute > 0:
                            continue
                        anim_time_options.append(f"{hour:02d}:{minute:02d}")

                # Default to nearest 30-minute intervals
                anim_time_slider_default_start_idx = min(int(2*np.floor(anim_min_time_rounded / (30*60))), len(anim_time_options)-1)
                anim_time_slider_default_end_idx = min(int(2*np.ceil(anim_max_time_rounded / (30*60))), len(anim_time_options)-1)

                # Create a range slider using the select_slider
                anim_time_slider_selected_range = st.select_slider(
                    "Time range",
                    options=anim_time_options,
                    value=(anim_time_options[anim_time_slider_default_start_idx], anim_time_options[anim_time_slider_default_end_idx]),
                    key="anim_time_slider_range"
                )

                anim_start_time_selected, anim_end_time_selected = anim_time_slider_selected_range

                anim_start_hour, anim_start_minute = map(int, anim_start_time_selected.split(":"))
                anim_end_hour, anim_end_minute = map(int, anim_end_time_selected.split(":"))

                anim_start_seconds = 3600 * anim_start_hour + 60 * anim_start_minute
                anim_end_seconds = 3600 * anim_end_hour + 60 * anim_end_minute
            else:
                st.write("No data available for custom time range selection. Upload GPX files and select one or more tracks.")
    
    with anim_col_03:
        st.subheader("Animation Settings")

        anim_duration = st.slider("Animation length (seconds)", min_value=10, max_value=60, value=20, step=2, key="anim_duration")
        anim_fps = st.slider("Frames per second", min_value=10, max_value=48, value=24, step=2, key="anim_fps")            
        anim_trail_duration = 60*60*st.slider(
            "Trail duration (hours)",
            min_value=0,
            max_value=24,
            value=12,
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