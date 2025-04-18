import os
import tempfile
import gpxpy
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import streamlit as st
from matplotlib.lines import Line2D
import base64
from io import BytesIO
import tempfile

from load_gpx import load_gpx_files
from providers import PROVIDERS
from generate_map import generate_map
from generate_animation import generate_animation


# Initialize session state variables
if 'combined_df' not in st.session_state:
    st.session_state.combined_df = None
if 'static_map_generated' not in st.session_state:
    st.session_state.static_map_generated = False
if 'animation_generated' not in st.session_state:
    st.session_state.animation_generated = False
if 'animation_file' not in st.session_state:
    st.session_state.animation_file = None
if 'static_map_fig' not in st.session_state:
    st.session_state.static_map_fig = None
if 'animation_bytes' not in st.session_state:
    st.session_state.animation_bytes = None
    
# Add parameter tracking
if 'static_params_hash' not in st.session_state:
    st.session_state.static_params_hash = ""
if 'anim_params_hash' not in st.session_state:
    st.session_state.anim_params_hash = ""
if 'current_static_params' not in st.session_state:
    st.session_state.current_static_params = {}
if 'current_anim_params' not in st.session_state:
    st.session_state.current_anim_params = {}
    

# Helper function to create a download link
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}" class="btn btn-primary">Download {file_label}</a>'
    return href


# Callback when files are uploaded
def on_files_uploaded():
    st.session_state.static_map_generated = False
    st.session_state.animation_generated = False
    st.session_state.static_map_fig = None
    st.session_state.animation_bytes = None
    if st.session_state.animation_file is not None:
        try:
            os.unlink(st.session_state.animation_file)
            st.session_state.animation_file = None
        except:
            pass


# Streamlit app
def main():
    # st.set_page_config(page_title="GPX Track Visualizer", layout="wide")

    st.set_page_config(page_title="GPX Track Visualizer", layout="wide")
    
    left_col, middle_col, right_col = st.columns([1, 6, 1])

    with middle_col:
    
        st.title("GPX Track Visualizer")
        st.write("Upload GPX files to visualize tracks on a map and create animations")
        
        # File uploader
        uploaded_files = st.file_uploader("Upload GPX files", type=["gpx"], accept_multiple_files=True, 
                                         on_change=on_files_uploaded)
        
        if uploaded_files:
            # Only process GPX files if we haven't processed them already or if they changed
            if st.session_state.combined_df is None:
                with st.spinner("Processing GPX files..."):
                    combined_df = load_gpx_files(uploaded_files)
                st.session_state.combined_df = combined_df
            else:
                combined_df = st.session_state.combined_df
            
            if combined_df is not None and not combined_df.empty:
                st.success(f"Loaded {len(uploaded_files)} GPX files with {len(combined_df)} total track points")

                st.divider()
                
                st.subheader("Map Settings")
                col1, col2 = st.columns(2)
                
                with col1:
                    map_style = st.selectbox("Map Style", list(PROVIDERS.keys()), index=12, key="static_map_style")
                    fig_width = float(st.text_input("Figure Width (inches):", value="12", key="static_fig_width"))
                    show_start_end_points = st.checkbox("Show Start and End Points", value=True, key="static_show_start_end")
                    show_legend = st.checkbox("Show Legend", value=False, key="static_show_legend")
                    show_coordinates = st.checkbox("Show Coordinates", value=False, key="static_show_coordinates")

                
                with col2:
                    lat_buffer = float(st.text_input("Latitude Buffer", value="0.125", key="static_lat_buffer"))
                    lon_buffer = float(st.text_input("Longitude Buffer", value="0.125", key="static_lon_buffer"))
                    custom_title = st.text_input("Custom Title", "", key="static_title")
                
                # Advanced settings
                with st.expander("Advanced Map Settings", expanded=False):
                    st.subheader("Custom Latitude and Longitude Bounds")
                    use_custom_bounds = st.checkbox("Use Custom Bounds", value=False, key="static_custom_bounds")
                    
                    if use_custom_bounds:
                        lat_min_default = float(combined_df["latitude"].min())
                        lat_max_default = float(combined_df["latitude"].max())
                        lon_min_default = float(combined_df["longitude"].min())
                        lon_max_default = float(combined_df["longitude"].max())
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            lat_min = st.number_input("Min Latitude", value=lat_min_default, format="%.6f", key="static_lat_min")
                            lon_min = st.number_input("Min Longitude", value=lon_min_default, format="%.6f", key="static_lon_min")
                        
                        with col2:
                            lat_max = st.number_input("Max Latitude", value=lat_max_default, format="%.6f", key="static_lat_max")
                            lon_max = st.number_input("Max Longitude", value=lon_max_default, format="%.6f", key="static_lon_max")
                    else:
                        lat_min = None
                        lat_max = None
                        lon_min = None
                        lon_max = None
                
                # Generate a hash of the current static map parameters
                import hashlib
                import json
                
                # Create a dictionary of all static map parameters
                static_params = {
                    "map_style": map_style,
                    "fig_width": fig_width,
                    "lat_buffer": lat_buffer,
                    "lon_buffer": lon_buffer,
                    "lat_min": lat_min if use_custom_bounds else None,
                    "lat_max": lat_max if use_custom_bounds else None,
                    "lon_min": lon_min if use_custom_bounds else None,
                    "lon_max": lon_max if use_custom_bounds else None,
                    "custom_title": custom_title,
                    "show_start_end_points": show_start_end_points,
                    "show_legend": show_legend,
                    "use_custom_bounds": use_custom_bounds
                }
                
                # Generate a hash of these parameters
                static_params_str = json.dumps(static_params, sort_keys=True)
                current_hash = hashlib.md5(static_params_str.encode()).hexdigest()
                
                # Check if parameters have changed since last generation
                params_changed = current_hash != st.session_state.static_params_hash
                
                # Display a note if parameters have changed since last generation
                if params_changed and st.session_state.static_map_generated:
                    st.info("Map parameters have changed. Click 'Generate Static Map' to update the visualization.")

                # Generate the preview map button
                generate_map_clicked = st.button("Generate Static Map")
                
                # Always show the map if it was previously generated
                if generate_map_clicked or st.session_state.static_map_generated:
                    # Regenerate the map only if button was clicked or it's the first time
                    if generate_map_clicked or st.session_state.static_map_fig is None:
                        with st.spinner("Generating map..."):
                            fig = generate_map(
                                combined_df,
                                map_style=map_style,
                                fig_width=int(fig_width),
                                lat_buffer=lat_buffer,
                                lon_buffer=lon_buffer,
                                lat_min=lat_min,
                                lat_max=lat_max,
                                lon_min=lon_min,
                                lon_max=lon_max,
                                title=custom_title,
                                start_end_points=show_start_end_points,
                                show_legend=show_legend
                            )
                            st.session_state.static_map_fig = fig
                            st.session_state.static_map_generated = True
                            # Update the hash
                            st.session_state.static_params_hash = current_hash
                            # Record the current parameters so we know we're showing the latest
                            st.session_state.current_static_params = static_params
                    
                    col1, col2, col3 = st.columns([1, 4, 1])
                    with col2:
                        if st.session_state.static_map_fig:
                            st.pyplot(st.session_state.static_map_fig)

                st.divider()

                st.subheader("Animation Settings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    anim_map_style = st.selectbox("Map Style", list(PROVIDERS.keys()), index=12, key="anim_map_style")
                    anim_fig_width = float(st.text_input("Figure Width (inches):", value="8", key="anim_fig_width"))
                    anim_duration = st.slider("Animation Duration (seconds)", min_value=5, max_value=60, value=20, step=1, key="anim_duration")
                    anim_fps = st.slider("Frames Per Second", min_value=10, max_value=48, value=24, step=2, key="anim_fps")
                    marker_size = st.slider("Marker Size", min_value=1, max_value=4, value=2, step=1, key="marker_size")
                    line_width = st.slider("Line Width", min_value=1, max_value=4, value=1, step=1, key="line_width")
                
                with col2:
                    anim_lat_buffer = float(st.text_input("Latitude Buffer", value="0.125", key="anim_lat_buffer"))
                    anim_lon_buffer = float(st.text_input("Longitude Buffer", value="0.125", key="anim_lon_buffer"))
                    anim_title = st.text_input("Animation Title", "", key="anim_title")
                    show_time = st.checkbox("Show Time", value=True, key="show_time")
                    show_legend = st.checkbox("Show Legend", value=False, key="show_legend")
                    trail_duration = 60*60*st.slider("Trail Duration (hours) - set to 0 to disable disappering trails",
                                                    min_value=0, max_value=24, value=12, step=1, key="trail_minutes")
                
                # trail_duration = trail_minutes * 60  # Convert minutes to seconds
                if trail_duration == 0:
                    trail_duration = 24*3600
                
                # Advanced settings
                with st.expander("Advanced Animation Settings", expanded=False):
                    st.subheader("Custom Latitude and Longitude Bounds")
                    anim_use_custom_bounds = st.checkbox("Use Custom Bounds", value=False, key="anim_custom_bounds")
                    
                    if anim_use_custom_bounds:
                        anim_lat_min_default = float(combined_df["latitude"].min())
                        anim_lat_max_default = float(combined_df["latitude"].max())
                        anim_lon_min_default = float(combined_df["longitude"].min())
                        anim_lon_max_default = float(combined_df["longitude"].max())
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            anim_lat_min = st.number_input("Min Latitude", value=anim_lat_min_default, format="%.6f", key="anim_lat_min")
                            anim_lon_min = st.number_input("Min Longitude", value=anim_lon_min_default, format="%.6f", key="anim_lon_min")
                        
                        with col2:
                            anim_lat_max = st.number_input("Max Latitude", value=anim_lat_max_default, format="%.6f", key="anim_lat_max")
                            anim_lon_max = st.number_input("Max Longitude", value=anim_lon_max_default, format="%.6f", key="anim_lon_max")
                    else:
                        anim_lat_min = None
                        anim_lat_max = None
                        anim_lon_min = None
                        anim_lon_max = None
                    
                    st.subheader("Time Range")
                    # Get actual time range in the data
                    min_time = combined_df["elapsed_seconds"].min()
                    min_time = min_time - (min_time % (30*60))  # Round down to nearest minute
                    max_time = combined_df["elapsed_seconds"].max()
                    max_time = max_time - (max_time % (30*60)) + 30*60
                    
                    # Convert to hours:minutes for display
                    min_time_str = pd.to_datetime(min_time, unit='s').strftime('%H:%M')
                    max_time_str = pd.to_datetime(max_time, unit='s').strftime('%H:%M')
                    
                    st.write(f"Data time range: {min_time_str} to {max_time_str}")
                    custom_time_range = st.checkbox("Use Custom Time Range", value=False, key="custom_time_range")
                    
                    if custom_time_range:
                        col1, col2 = st.columns(2)
                        with col1:
                            start_hour = st.slider("Start Hour", min_value=0, max_value=23, 
                                                value=int(min_time/3600), step=1, key="start_hour")
                            start_minute = st.slider("Start Minute", min_value=0, max_value=59, 
                                                    value=int((min_time % 3600)/60), step=5, key="start_minute")
                        with col2:
                            end_hour = st.slider("End Hour", min_value=0, max_value=23, 
                                                value=int(max_time/3600), step=1, key="end_hour")
                            end_minute = st.slider("End Minute", min_value=0, max_value=59, 
                                                value=int((max_time % 3600)/60), step=5, key="end_minute")
                        
                        custom_start_time = start_hour * 3600 + start_minute * 60
                        custom_end_time = end_hour * 3600 + end_minute * 60
                    else:
                        custom_start_time = min_time
                        custom_end_time = max_time
                    
                    st.subheader("Quality Settings")
                    dpi = st.slider("DPI (resolution)", min_value=100, max_value=300, value=150, step=25, key="dpi")

                # Generate a hash of the current animation parameters
                import hashlib
                import json
                
                # Create a dictionary of all animation parameters
                anim_params = {
                    "map_style": anim_map_style,
                    "fig_width": anim_fig_width,
                    "duration": anim_duration,
                    "fps": anim_fps,
                    "marker_size": marker_size,
                    "line_width": line_width,
                    "lat_buffer": anim_lat_buffer,
                    "lon_buffer": anim_lon_buffer,
                    "title": anim_title,
                    "show_time": show_time,
                    "show_legend": show_legend,
                    "trail_duration": trail_duration,
                    "use_custom_bounds": anim_use_custom_bounds,
                    "lat_min": anim_lat_min if anim_use_custom_bounds else None,
                    "lat_max": anim_lat_max if anim_use_custom_bounds else None,
                    "lon_min": anim_lon_min if anim_use_custom_bounds else None,
                    "lon_max": anim_lon_max if anim_use_custom_bounds else None,
                    "custom_time_range": custom_time_range,
                    "start_time": custom_start_time if custom_time_range else None,
                    "end_time": custom_end_time if custom_time_range else None,
                    "dpi": dpi
                }
                
                # Generate a hash of these parameters
                anim_params_str = json.dumps(anim_params, sort_keys=True)
                current_anim_hash = hashlib.md5(anim_params_str.encode()).hexdigest()
                
                # Check if parameters have changed since last generation
                anim_params_changed = current_anim_hash != st.session_state.anim_params_hash
                
                # Display a note if parameters have changed since last generation
                if anim_params_changed and st.session_state.animation_generated:
                    st.info("Animation parameters have changed. Click 'Generate Animation' to update the visualization.")
                
                # Generate animation button
                animation_button_clicked = st.button("Generate Animation")
                
                # Display the animation if button clicked or if it was previously generated
                if animation_button_clicked or st.session_state.animation_generated:
                    # Regenerate only if button was explicitly clicked or if first time
                    needs_regeneration = (animation_button_clicked or st.session_state.animation_bytes is None)
                    
                    # Generate the animation if needed
                    if needs_regeneration:
                        with st.spinner("Generating animation... This may take a while depending on duration and quality settings."):
                            try:
                                animation_file = generate_animation(
                                    combined_df,
                                    duration=anim_duration,
                                    fps=anim_fps,
                                    start_time=custom_start_time,
                                    end_time=custom_end_time,
                                    dpi=dpi,
                                    trail_duration=trail_duration,
                                    marker_size=marker_size,
                                    line_width=line_width,
                                    add_terrain=True,
                                    map_style=anim_map_style,
                                    fig_width=int(anim_fig_width),
                                    lat_buffer=anim_lat_buffer,
                                    lon_buffer=anim_lon_buffer,
                                    lat_min=anim_lat_min,
                                    lat_max=anim_lat_max,
                                    lon_min=anim_lon_min,
                                    lon_max=anim_lon_max,
                                    title=anim_title,
                                    show_time=show_time,
                                    show_legend=show_legend
                                )
                                
                                # Store the animation file path and load the bytes
                                st.session_state.animation_file = animation_file
                                with open(animation_file, 'rb') as video_file:
                                    st.session_state.animation_bytes = video_file.read()
                                
                                st.session_state.animation_generated = True
                                # Update the hash and store current parameters
                                st.session_state.anim_params_hash = current_anim_hash
                                st.session_state.current_anim_params = anim_params
                                
                            except Exception as e:
                                st.error(f"Error generating animation: {e}")
                                st.session_state.animation_generated = False
                                st.session_state.animation_bytes = None
                    
                    # Display the animation if it was successfully generated
                    if st.session_state.animation_generated and st.session_state.animation_bytes is not None:
                        col1, col2, col3 = st.columns([1, 4, 1])
                        with col2:
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

            else:
                st.error("No valid data found in the uploaded GPX files")

if __name__ == "__main__":
    main()