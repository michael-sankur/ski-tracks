# GPX Track Visualizer App


"""

- Select tracks from overall list

- Support for tracks longer than 1 day
-- If track spans over multiple days
-- Need to adjust duration for animation
-- Need to adjust custom time range slider
-- Display day + time, or only time with hours?
-- max(number of unique dates * 24, length of track in hours) for sliders etc


- Custom NSEW padding for map bounds
- Coordinates on map
- Calculate lat/lon bounds in app, pass into generate_map

- Custom NSEW padding for animation bounds
- Coordinates on animation
- Hide line or markers on animation with 0 value
- Progress bar for animation generation
- Calculate lat/lon bounds in app, pass into generate_animation

- Refresh df when files change


"""

import base64
import hashlib
import json
from tracemalloc import start
import numpy as np
import pandas as pd
import os
import streamlit as st

from parse_gpx import parse_gpx_files
from providers import PROVIDERS
from generate_map import generate_map
from generate_animation import generate_animation

from parse_gpx import parse_gpx_files
from state_management import initialize_session_state, on_files_uploaded
from track_selection import show_track_selection
from static_map_section import show_static_map_options, generate_display_static_map
from animation_section import show_animation_options, generate_display_animation
# from animation import show_animation_options, generate_animation_vizualization
from util import check_params_changed, get_binary_file_downloader_html


def on_files_uploaded():
    """
    Callback function executed when new files are uploaded.
    Resets visualization states and cleans up resources.
    """
    # Store current animation file path before resetting
    animation_file_path = st.session_state.get("animation_file")
    
    # Reset visualization flags
    st.session_state.stat_map_generated = False
    st.session_state.animation_generated = False
    
    # Reset binary data to release memory
    st.session_state.animation_bytes = None
    st.session_state.df_combined = None
    
    # Reset parameter tracking
    st.session_state.stat_params_hash = ""
    st.session_state.anim_params_hash = ""
    st.session_state.stat_current_params = {}
    st.session_state.anim_current_params = {}
    
    # Clean up temporary animation file if it exists
    if animation_file_path is not None:
        try:
            if os.path.exists(animation_file_path):
                os.unlink(animation_file_path)
                st.session_state.animation_file = None
        except OSError as e:
            st.warning(f"Could not delete temporary file: {e}")
    
    # Reset checkbox states to ensure track selection is refreshed
    if "checkbox_states" in st.session_state:
        del st.session_state.checkbox_states

def display_file_info(df_combined):
    with st.expander("File and Track Information", expanded=False):
        track_info = ""
        for file_name in sorted(df_combined["file_name"].unique()):
            track_info += f"File: {file_name} - {len(df_combined[df_combined['file_name'] == file_name]['track_name'].unique())} track(s)\n"
            for track_name in sorted(df_combined[df_combined["file_name"] == file_name]["track_name"].unique()):
                track_points = len(df_combined[df_combined["track_name"] == track_name])
                track_info += f"  - {track_name} - {track_points} points\n"
            track_info += "\n"
            
        st.text_area("", track_info, height=200, disabled=True)


# Streamlit app
def main():

    st.set_page_config(page_title="GPX Track Visualizer", layout="wide")

    # Initialize session state variables
    initialize_session_state()

    # Set up main layout with middle column at 75% width for content
    left_col, middle_col, right_col = st.columns([1, 6, 1])

    with middle_col:
    
        st.title("GPX Track Visualizer")
        st.write("Upload GPX files to visualize tracks on a map and create animations")

        st.divider()

        st.header("Upload GPX Files")
        st.write("Upload one or more GPX files containing GPS tracks.")
                
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload GPX files",
            type=["gpx"],
            accept_multiple_files=True, 
            on_change=on_files_uploaded
        )

        # Process GPX files
        df_combined = None
        if uploaded_files:
            if st.session_state.df_combined is None:
                with st.spinner("Processing GPX files..."):
                    df_combined = parse_gpx_files(uploaded_files)
                st.session_state.df_combined = df_combined
            else:
                df_combined = st.session_state.df_combined
            
            if df_combined is not None and not df_combined.empty:
                st.success(f"Loaded and parsed GPX file(s)")
                # Show file info in expander
                display_file_info(df_combined)
        
        st.divider()

        # Track selection section
        selected_tracks, df_selected_tracks = show_track_selection(df_combined)
        
        vis_mode = "track"  # Could be made configurable
        
        st.divider()

        # Static map section
        if df_selected_tracks is not None and not df_selected_tracks.empty:

            # Call with default key prefix "stat"
            stat_params = show_static_map_options(df_selected_tracks)
            
            # Generate the map
            generate_display_static_map(df_selected_tracks, stat_params, selected_tracks, session_key_prefix="stat")
            

        st.divider()

        if df_selected_tracks is not None and not df_selected_tracks.empty:
            anim_params = show_animation_options(df_selected_tracks)
            
            # # Check if parameters have changed
            # anim_params_changed, anim_current_hash = check_params_changed(
            #     anim_params, "anim_params_hash"
            # )
            
            # # Show notice if params changed since last generation
            # if anim_params_changed and st.session_state.anim_map_generated:
            #     st.info("Map parameters have changed. Click Generate Static Map to update the visualization.")
            
            # Generate the map
            generate_display_animation(df_selected_tracks, anim_params, selected_tracks)
            
            # # Update hash if map was generated
            # if st.session_state.anim_map_generated:
            #     st.session_state.anim_params_hash = anim_current_hash
            #     st.session_state.current_anim_params = anim_params

        st.divider()

if __name__ == "__main__":
    main()
