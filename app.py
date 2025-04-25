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
import numpy as np
import pandas as pd
import os
import streamlit as st

from parse_gpx import parse_gpx_files
from providers import PROVIDERS
from generate_map import generate_map
from generate_animation import generate_animation


# Initialize session state variables
if "combined_df" not in st.session_state:
    st.session_state.combined_df = None
if "stat_map_generated" not in st.session_state:
    st.session_state.stat_map_generated = False
if "animation_generated" not in st.session_state:
    st.session_state.animation_generated = False
if "animation_file" not in st.session_state:
    st.session_state.animation_file = None
if "stat_map_fig" not in st.session_state:
    st.session_state.stat_map_fig = None
if "animation_bytes" not in st.session_state:
    st.session_state.animation_bytes = None
    
# Add parameter tracking
if "stat_params_hash" not in st.session_state:
    st.session_state.stat_params_hash = ""
if "anim_params_hash" not in st.session_state:
    st.session_state.anim_params_hash = ""
if "stat_current_params" not in st.session_state:
    st.session_state.stat_current_params = {}
if "anim_current_params" not in st.session_state:
    st.session_state.anim_current_params = {}
    

# Helper function to create a download link
def get_binary_file_downloader_html(bin_file, file_label="File"):
    with open(bin_file, "rb") as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f"""<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}" class="btn btn-primary">Download {file_label}</a>"""
    return href


# Callback when files are uploaded
def on_files_uploaded():
    st.session_state.stat_map_generated = False
    st.session_state.animation_generated = False
    st.session_state.stat_map_fig = None
    st.session_state.animation_bytes = None
    if st.session_state.animation_file is not None:
        try:
            os.unlink(st.session_state.animation_file)
            st.session_state.animation_file = None
        except:
            pass


# Streamlit app
def main():
    st.set_page_config(page_title="GPX Track Visualizer", layout="wide")
    
    left_col, middle_col, right_col = st.columns([1, 6, 1])

    with middle_col:
    
        st.title("GPX Track Visualizer")
        st.write("Upload GPX files to visualize tracks on a map and create animations")

        st.divider()

        st.header("Upload GPX Files")
        st.write("Upload one or more GPX files containing GPS tracks. The app will parse the files and create a visualization of the tracks on a map or create an animation of the tracks over time.")
                
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload GPX files",
            type=["gpx"],
            accept_multiple_files=True, 
            on_change=on_files_uploaded
        )

        if uploaded_files:
            # Only process GPX files if we have not processed them already or if they changed
            if st.session_state.combined_df is None:
                with st.spinner("Processing GPX files..."):
                    combined_df = parse_gpx_files(uploaded_files)
                st.session_state.combined_df = combined_df
            else:
                combined_df = st.session_state.combined_df
            
        if uploaded_files and combined_df is not None and not combined_df.empty:
            st.success(f"Loaded and parsed GPX file(s)")
            with st.expander("File and Track Information", expanded=False):
                track_info = ""
                for file_name in sorted(combined_df["file_name"].unique()):
                    track_info += f"File: {file_name} - {len(combined_df[combined_df["file_name"] == file_name]["track_name"].unique())} track(s)\n"
                    # track_info += "Tracks:\n"
                    for track_name in sorted(combined_df[combined_df["file_name"] == file_name]["track_name"].unique()):
                        track_points = len(combined_df[combined_df["track_name"] == track_name])
                        track_info += f"  - {track_name} - {track_points} points\n"
                    track_info += "\n"
                    
                    st.text_area("", track_info, height=200, disabled=True)
        
        st.divider()

        # options_list = []

        def show_checklist(options_list):
            # Create a list to store the status of each checkbox (True = checked)
            if 'checkbox_states' not in st.session_state:
                # Initialize all checkboxes as checked (True)
                st.session_state.checkbox_states = [True] * len(options_list)
            
            # Display checkboxes and update their states
            for k1, option in enumerate(options_list):
                st.session_state.checkbox_states[k1] = st.checkbox(
                    option, 
                    value=st.session_state.checkbox_states[k1],
                    key=f"checkbox_{k1}"
                )
            
            # Return only the selected options
            selected_options = [opt for opt, state in zip(options_list, st.session_state.checkbox_states) if state]
            return selected_options

        # Example usage
        st.title("Options Selection")

        # Your original list of options
        all_options = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"]

        # Show the checklist and get selected options
        if uploaded_files and combined_df is not None and not combined_df.empty:
            track_list = sorted(combined_df["track_name"].unique().tolist() if combined_df is not None else [])
            track_selected = show_checklist(track_list)

            # Display the selected options
            st.write("You selected:", track_selected)

        st.divider()

        # Visualization mode selection
        st.subheader("Visualization Mode")
        vis_mode = st.radio(
            label="Select Visualization Mode",
            index=0,
            options=["Visualize files", "Visualize tracks"],
            key="visualization_mode",
            captions=[
                "Combine all tracks within each file into a single track. Select if you export one trip per file. If an trip is split into multiple tracks, they will be combined into a single track.",
                "Keep each track in GPX files separate. Select if you export multiple trips per file. If a trip is split into multiple tracks, they will be NOT combined into a single track, and be treated as multiple trips."
            ]
        )
        vis_mode = "file" if vis_mode == "Visualize files" else "track"

        # Create an expandable container for the file/track information
        if uploaded_files and combined_df is not None and not combined_df.empty:        
            with st.expander("File and Track Information", expanded=False):
                if vis_mode == "file":
                    file_info = ""
                    for file_name in sorted(combined_df["file_name"].unique()):
                        file_info += f"File {file_name}.gpx combined into a track of {len(combined_df[combined_df["file_name"] == file_name])} points\n"

                    st.text_area("", file_info, height=200, disabled=True)
                
                elif vis_mode == "track":
                    track_info = ""
                    for file_name in sorted(combined_df["file_name"].unique()):
                        track_info += f"File: {file_name}\n"
                        for track_name in sorted(combined_df[(combined_df["file_name"] == file_name)]["track_name"].unique()):
                            # Filter by both file_name AND track_name
                            track_points = combined_df[(combined_df["file_name"] == file_name) & 
                                                    (combined_df["track_name"] == track_name)]
                            
                            # Format the times to be more readable (optional)
                            min_seconds = track_points["elapsed_seconds"].min()
                            max_seconds = track_points["elapsed_seconds"].max()
                            
                            track_info += f"  - {track_name} - {len(track_points)} points - {min_seconds:.1f}s to {max_seconds:.1f}s\n"
                        track_info += "\n"
                    
                    # Display in a text area which is scrollable by default
                    st.text_area("", track_info, height=200, disabled=True)

        st.divider()

        # Static Map Visualization
        st.header("Generate Static Visualization")

        # stat_title = st.text_input("Title", "", key="stat_title")
        stat_map_settings_column, stat_vis_settings_column = st.columns(2)
        
        with stat_map_settings_column:
            st.subheader("Map Settings")
            stat_fig_width = st.number_input("Figure Width (inches):", min_value=6.0, max_value=18.0, value=12.0, step=0.5, format="%.1f", key="stat_fig_width")
            stat_map_style = st.selectbox("Map Style", list(PROVIDERS.keys()), index=12, key="stat_map_style")            
            stat_lat_padding = st.number_input("Latitude Padding", min_value=0.0, max_value=1.0, value=0.125, step=0.005, format="%.3f",key="stat_lat_padding")
            stat_lon_padding = st.number_input("Longitude Padding", min_value=0.0, max_value=1.0, value=0.125, step=0.005, format="%.3f",key="stat_lon_padding")

            

            # Custom map bounds
            stat_use_custom_bounds = False
            with st.expander("Custom Latitude and Longitude Bounds", expanded=False):
                if uploaded_files and combined_df is not None and not combined_df.empty:
                    stat_use_custom_bounds = st.checkbox("Use Custom Bounds", value=False, key="stat_custom_bounds")

                    stat_track_lat_delta = combined_df["latitude"].max() - combined_df["latitude"].min()
                    stat_track_lon_delta = combined_df["longitude"].max() - combined_df["longitude"].min()

                    stat_lat_min_default = combined_df["latitude"].min() - stat_lat_padding*stat_track_lat_delta
                    stat_lat_max_default = combined_df["latitude"].max() + stat_lat_padding*stat_track_lat_delta
                    stat_lon_min_default = combined_df["longitude"].min() - stat_lon_padding*stat_track_lon_delta
                    stat_lon_max_default = combined_df["longitude"].max() + stat_lon_padding*stat_track_lon_delta
                    
                    if stat_use_custom_bounds:                        
                        stat_lat_min = st.number_input("Min Latitude", value=stat_lat_min_default, format="%.4f", step=0.005, key="stat_lat_min")
                        stat_lat_max = st.number_input("Max Latitude", value=stat_lat_max_default, format="%.4f", step=0.005, key="stat_lat_max")
                        stat_lon_min = st.number_input("Min Longitude", value=stat_lon_min_default, format="%.4f", step=0.005, key="stat_lon_min")                        
                        stat_lon_max = st.number_input("Max Longitude", value=stat_lon_max_default, format="%.4f", step=0.005, key="stat_lon_max")
                    else:
                        stat_lat_min = stat_lat_min_default
                        stat_lat_max = stat_lat_max_default
                        stat_lon_min = stat_lon_min_default
                        stat_lon_max = stat_lon_max_default
        
        with stat_vis_settings_column:
            st.subheader("Visualization Options")
            stat_show_start_end_points = st.checkbox("Show start and end points", value=True, key="stat_show_start_end")
            stat_show_legend = st.checkbox("Show legend", value=False, key="stat_show_legend")
            stat_show_coordinates = st.checkbox("Show coordinates", value=False, key="stat_show_coordinates")

            stat_line_width = st.slider("Line Width", min_value=1, max_value=4, value=2, step=1, key="stat_line_width")
            stat_marker_size = st.slider("Marker Size", min_value=1, max_value=8, value=4, step=1, key="stat_marker_size")

            # stat_start_seconds = 0
            # stat_end_seconds = 24 * 3600

            with st.expander("Custom Time Range", expanded=False):
                
                if uploaded_files and combined_df is not None and not combined_df.empty:

                    stat_num_days = np.floor(combined_df["elapsed_seconds"].max() / (24*3600)) + 1
                    stat_num_days = int(max(stat_num_days, 1))

                    stat_start_seconds = 0
                    stat_end_seconds = stat_num_days * 24 * 3600

                    data_time_min_hour = int(np.floor(combined_df["elapsed_seconds"].min() / 3600))
                    data_time_min_minute = int(np.floor((combined_df["elapsed_seconds"].min() % 3600) / 60))

                    data_time_max_hour = int(np.ceil(combined_df["elapsed_seconds"].max() / 3600 - 24*(stat_num_days-1)))
                    data_time_max_minute = int(np.ceil((combined_df["elapsed_seconds"].max() % 3600) / 60))


                    st.write(f"Data time range: Day {1} at {data_time_min_hour}:{data_time_min_minute}  -  Day {stat_num_days} at {data_time_max_hour}:{data_time_max_minute}")

                    stat_min_time = combined_df["elapsed_seconds"].min()
                    stat_min_time_rounded = stat_min_time - (stat_min_time % (30*60))
                    stat_max_time = combined_df["elapsed_seconds"].max()
                    stat_max_time_rounded = stat_max_time - (stat_max_time % (30*60)) + 30*60

                    stat_time_options = []
                    for hour in range(stat_num_days*24 + 1):
                        for minute in [0, 15, 30, 45]:
                            if hour == stat_num_days*24 and minute > 0:
                                continue
                            stat_time_options.append(f"{hour:02d}:{minute:02d}")

                    # Default to nearest 30-minute intervals
                    stat_default_start_idx = int(2*np.floor(stat_min_time_rounded / (30*60)))
                    stat_default_end_idx = int(2*np.ceil(stat_max_time_rounded / (30*60)))


                    # Create a range slider using the select_slider
                    stat_selected_range = st.select_slider(
                        "Time range",
                        options=stat_time_options,
                        value=(stat_time_options[stat_default_start_idx], stat_time_options[stat_default_end_idx]),
                        key="stat_time_range"
                    )

                    stat_start_time, stat_end_time = stat_selected_range

                    stat_start_hour, stat_start_minute = map(int, stat_start_time.split(":"))
                    stat_end_hour, stat_end_minute = map(int, stat_end_time.split(":"))

                    stat_start_seconds = 3600 * stat_start_hour + 60 * stat_start_minute
                    stat_end_seconds = 3600 * stat_end_hour + 60 * stat_end_minute

                    st.write(stat_start_seconds, stat_end_seconds)
                else:
                    stat_time_options = []
                    for hour in range(25):
                        for minute in [0, 15, 30, 45]:
                            if hour == 24 and minute > 0:
                                continue
                            stat_time_options.append(f"{hour:02d}:{minute:02d}")
                    stat_selected_range = st.select_slider(
                            "Time range",
                            options=stat_time_options,
                            value=(stat_time_options[0], stat_time_options[-1]),
                            key="stat_time_range"
                        )
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            stat_title = st.text_input("Title", "", key="stat_title")
        
            # Create a dictionary of all static map parameters
            stat_params = {
                "vis_mode": vis_mode,
                "map_style": stat_map_style,
                "fig_width": stat_fig_width,
                "lat_padding": stat_lat_padding,
                "lon_padding": stat_lon_padding,
                "use_custom_bounds": stat_use_custom_bounds,
                "lat_min": stat_lat_min if stat_use_custom_bounds else None,
                "lat_max": stat_lat_max if stat_use_custom_bounds else None,
                "lon_min": stat_lon_min if stat_use_custom_bounds else None,
                "lon_max": stat_lon_max if stat_use_custom_bounds else None,            
                "show_start_end_points": stat_show_start_end_points,
                "show_legend": stat_show_legend,            
                "show_coordinates": stat_show_coordinates,
                "line_width": stat_line_width,
                "marker_size": stat_marker_size,
                "custom_title": stat_title,
                "start_seconds": stat_start_seconds,
                "end_seconds": stat_end_seconds,
            }
            
            # Generate a hash of these parameters
            stat_params_str = json.dumps(stat_params, sort_keys=True)
            stat_current_hash = hashlib.md5(stat_params_str.encode()).hexdigest()
            
            # Check if parameters have changed since last generation
            stat_params_changed = stat_current_hash != st.session_state.stat_params_hash
            
            # Display a note if parameters have changed since last generation
            if stat_params_changed and st.session_state.stat_map_generated:
                st.info("Map parameters have changed. Click Generate Static Map to update the visualization.")

            stat_generate_clicked = st.button("Generate Static Map", disabled=not(uploaded_files and combined_df is not None and not combined_df.empty))
            
            # Always show the map if it was previously generated
            if stat_generate_clicked or st.session_state.stat_map_generated:
                # Regenerate the map only if button was clicked or it is the first time
                if stat_generate_clicked or st.session_state.stat_map_fig is None:
                    with st.spinner("Generating map..."):
                        fig = generate_map(
                            combined_df,
                            mode=vis_mode,
                            map_style=stat_map_style,
                            fig_width=int(stat_fig_width),
                            lat_padding=stat_lat_padding,
                            lon_padding=stat_lon_padding,
                            lat_min=stat_lat_min,
                            lat_max=stat_lat_max,
                            lon_min=stat_lon_min,
                            lon_max=stat_lon_max,                            
                            show_start_end_points=stat_show_start_end_points,
                            show_legend=stat_show_legend,
                            show_coordinates=stat_show_coordinates,
                            line_width=stat_line_width,
                            start_end_marker_size=stat_marker_size,
                            title=stat_title,
                            start_time=stat_start_seconds,
                            end_time=stat_end_seconds
                        )
                        st.session_state.stat_map_fig = fig
                        st.session_state.stat_map_generated = True
                        # Update the hash
                        st.session_state.stat_params_hash = stat_current_hash
                        # Record the current parameters so we know we are showing the latest
                        st.session_state.current_stat_params = stat_params
                
                # Display the map outside the regeneration condition
                # This ensures it's always shown if it exists
                if st.session_state.stat_map_fig:
                    # col1, col2, col3 = st.columns([1, 4, 1])
                    # with col2:
                    st.pyplot(st.session_state.stat_map_fig)

        st.divider()

        st.header("Generate an Animation")
        st.write("Create an animated visualization of the GPX tracks over time. You can customize the animation settings such as duration, FPS, and map style.")
        
        # anim_title = st.text_input("Animation title", "", key="anim_title")
        anim_col_01, anim_col_02, anim_col_03 = st.columns(3)
        
        with anim_col_01:
            st.subheader("Map Settings")
            anim_fig_width = st.number_input("Animation width (inches):", min_value=6.0, max_value=18.0, value=12.0, step=0.5, format="%.1f", key="anim_fig_width")
            anim_map_style = st.selectbox("Map Style", list(PROVIDERS.keys()), index=12, key="anim_map_style")
            anim_lat_padding = st.number_input("Latitude Padding", min_value=0.0, max_value=1.0, value=0.125, step=0.005, format="%.3f",key="anim_lat_padding")
            anim_lon_padding = st.number_input("Longitude Padding", min_value=0.0, max_value=1.0, value=0.125, step=0.005, format="%.3f", key="anim_lon_padding")

            # Custom map bounds
            anim_use_custom_bounds = False
            with st.expander("Custom Latitude and Longitude Bounds", expanded=False):
                if uploaded_files and combined_df is not None and not combined_df.empty:
                    anim_use_custom_bounds = st.checkbox("Use custom Bounds", value=False, key="anim_custom_bounds")

                    anim_track_lat_delta = combined_df["latitude"].max() - combined_df["latitude"].min()
                    anim_track_lon_delta = combined_df["longitude"].max() - combined_df["longitude"].min()

                    anim_lat_min_default = combined_df["latitude"].min() - anim_lat_padding*anim_track_lat_delta
                    anim_lat_max_default = combined_df["latitude"].max() + anim_lat_padding*anim_track_lat_delta
                    anim_lon_min_default = combined_df["longitude"].min() - anim_lon_padding*anim_track_lon_delta
                    anim_lon_max_default = combined_df["longitude"].max() + anim_lon_padding*anim_track_lon_delta
                    
                    if anim_use_custom_bounds:                        
                        anim_lat_min = st.number_input("Min Latitude", value=anim_lat_min_default, format="%.6f", key="anim_lat_min")
                        anim_lat_max = st.number_input("Max Latitude", value=anim_lat_max_default, format="%.6f", key="anim_lat_max")
                        anim_lon_min = st.number_input("Min Longitude", value=anim_lon_min_default, format="%.6f", key="anim_lon_min")                        
                        anim_lon_max = st.number_input("Max Longitude", value=anim_lon_max_default, format="%.6f", key="anim_lon_max")
                    else:
                        anim_lat_min = anim_lat_min_default
                        anim_lat_max = anim_lat_max_default
                        anim_lon_min = anim_lon_min_default
                        anim_lon_max = anim_lon_max_default

        with anim_col_02:
            st.subheader("Data Settings")

            anim_show_time = st.checkbox("Show time", value=True, key="anim_show_time")
            anim_show_legend = st.checkbox("Show legend", value=False, key="anim_show_legend")            
            anim_show_start_end_points = st.checkbox("Show start and end points", value=False, key="anim_show_start_end")
            anim_show_coordinates = st.checkbox("Show coordinates", value=False, key="anim_show_coordinates")
            anim_line_width = st.slider("Line Width", min_value=1, max_value=4, value=2, step=1, key="anim_line_width")
            anim_marker_size = st.slider("Marker Size", min_value=1, max_value=8, value=4, step=1, key="anim_marker_size")

            anim_start_seconds = 0
            anim_end_seconds = 24 * 3600

            with st.expander("Custom Time Range", expanded=False):
                
                if uploaded_files and combined_df is not None and not combined_df.empty:

                    anim_num_days = np.floor(combined_df["elapsed_seconds"].max() / (24*3600)) + 1
                    anim_num_days = int(max(anim_num_days, 1))

                    anim_start_seconds = 0
                    anim_end_seconds = anim_num_days * 24 * 3600

                    data_time_min_hour = int(np.floor(combined_df["elapsed_seconds"].min() / 3600))
                    data_time_min_minute = int(np.floor((combined_df["elapsed_seconds"].min() % 3600) / 60))

                    data_time_max_hour = int(np.ceil(combined_df["elapsed_seconds"].max() / 3600 - 24*(anim_num_days-1)))
                    data_time_max_minute = int(np.ceil((combined_df["elapsed_seconds"].max() % 3600) / 60))


                    st.write(f"Data time range: Day {1} at {data_time_min_hour}:{data_time_min_minute}  -  Day {anim_num_days} at {data_time_max_hour}:{data_time_max_minute}")

                    anim_min_time = combined_df["elapsed_seconds"].min()
                    anim_min_time_rounded = anim_min_time - (anim_min_time % (30*60))
                    anim_max_time = combined_df["elapsed_seconds"].max()
                    anim_max_time_rounded = anim_max_time - (anim_max_time % (30*60)) + 30*60

                    anim_time_options = []
                    for hour in range(anim_num_days*24 + 1):
                        for minute in [0, 15, 30, 45]:
                            if hour == anim_num_days*24 and minute > 0:
                                continue
                            anim_time_options.append(f"{hour:02d}:{minute:02d}")

                    # Default to nearest 30-minute intervals
                    anim_default_start_idx = int(2*np.floor(anim_min_time_rounded / (30*60)))
                    anim_default_end_idx = int(2*np.ceil(anim_max_time_rounded / (30*60)))


                    # Create a range slider using the select_slider
                    anim_selected_range = st.select_slider(
                        "Time range",
                        options=anim_time_options,
                        value=(anim_time_options[anim_default_start_idx], anim_time_options[anim_default_end_idx]),
                        key="anim_time_range"
                    )

                    anim_start_time, anim_end_time = anim_selected_range

                    anim_start_hour, anim_start_minute = map(int, anim_start_time.split(":"))
                    anim_end_hour, anim_end_minute = map(int, anim_end_time.split(":"))

                    anim_start_seconds = 3600 * anim_start_hour + 60 * anim_start_minute
                    anim_end_seconds = 3600 * anim_end_hour + 60 * anim_end_minute

                    st.write(anim_start_seconds, anim_end_seconds)
        
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
            
            # Create a dictionary of all animation parameters
            anim_params = {
                "map_style": anim_map_style,
                "fig_width": anim_fig_width,
                "duration": anim_duration,
                "fps": anim_fps,
                "marker_size": anim_marker_size,
                "line_width": anim_line_width,
                "lat_padding": anim_lat_padding,
                "lon_padding": anim_lon_padding,
                "title": anim_title,
                "show_time": anim_show_time,
                "show_legend": anim_show_legend,
                "trail_duration": anim_trail_duration,
                "use_custom_bounds": anim_use_custom_bounds,
                "lat_min": anim_lat_min if anim_use_custom_bounds else None,
                "lat_max": anim_lat_max if anim_use_custom_bounds else None,
                "lon_min": anim_lon_min if anim_use_custom_bounds else None,
                "lon_max": anim_lon_max if anim_use_custom_bounds else None,
                "start_time": anim_start_seconds,
                "end_time": anim_end_seconds,
                "dpi": anim_dpi
            }
            
            # Generate a hash of these parameters
            anim_params_str = json.dumps(anim_params, sort_keys=True)
            anim_current_hash = hashlib.md5(anim_params_str.encode()).hexdigest()
            
            # Check if parameters have changed since last generation
            anim_params_changed = anim_current_hash != st.session_state.anim_params_hash
            
            # Display a note if parameters have changed since last generation
            if anim_params_changed and st.session_state.animation_generated:
                st.info("Animation parameters have changed. Click Generate Animation to update the visualization.")

            # if uploaded_files and combined_df is not None and not combined_df.empty:
            
            # Generate animation button
            anim_gen_clicked = st.button("Generate Animation", disabled=not(uploaded_files and combined_df is not None and not combined_df.empty))
            
            # Display the animation if button clicked or if it was previously generated
            if anim_gen_clicked or st.session_state.animation_generated:
                # Regenerate only if button was explicitly clicked or if first time
                anim_needs_regeneration = (anim_gen_clicked or st.session_state.animation_bytes is None)
                
                # Generate the animation if needed
                if anim_needs_regeneration:
                    with st.spinner("Generating animation... This may take a while depending on duration and quality settings."):
                        try:
                            animation_file = generate_animation(
                                combined_df,
                                duration=anim_duration,
                                fps=anim_fps,
                                start_time=anim_start_seconds,
                                end_time=anim_end_seconds,
                                dpi=anim_dpi,
                                trail_duration=anim_trail_duration,
                                marker_size=anim_marker_size,
                                line_width=anim_line_width,
                                add_terrain=True,
                                map_style=anim_map_style,
                                fig_width=int(anim_fig_width),
                                lat_padding=anim_lat_padding,
                                lon_padding=anim_lon_padding,
                                lat_min=anim_lat_min,
                                lat_max=anim_lat_max,
                                lon_min=anim_lon_min,
                                lon_max=anim_lon_max,
                                title=anim_title,
                                show_time=anim_show_time,
                                show_legend=anim_show_legend
                            )
                            
                            # Store the animation file path and load the bytes
                            st.session_state.animation_file = animation_file
                            with open(animation_file, "rb") as video_file:
                                st.session_state.animation_bytes = video_file.read()
                            
                            st.session_state.animation_generated = True
                            # Update the hash and store current parameters
                            st.session_state.anim_params_hash = anim_current_hash
                            st.session_state.current_anim_params = anim_params
                            
                        except Exception as e:
                            st.error(f"Error generating animation: {e}")
                            st.session_state.animation_generated = False
                            st.session_state.animation_bytes = None
                
                # Display the animation if it was successfully generated
                if st.session_state.animation_generated and st.session_state.animation_bytes is not None:
                    st.success("Animation generated successfully!")
                    
                    # Display the video using the stored bytes
                    st.video(st.session_state.animation_bytes, loop=True)
                    
                    # Provide download link
                    if anim_title == "":
                        download_label = "animation"
                    else:
                        download_label = anim_title
                        
                    if st.session_state.animation_file:
                        st.markdown(get_binary_file_downloader_html(st.session_state.animation_file, download_label), 
                                    unsafe_allow_html=True)

        st.divider()

if __name__ == "__main__":
    main()