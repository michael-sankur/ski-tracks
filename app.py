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
from util import get_distinct_colors
from generate_map import generate_map
from generate_animation import generate_animation    


# Helper function to create a download link
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}" class="btn btn-primary">Download {file_label}</a>'
    return href


# Streamlit app
def main():
    # st.set_page_config(page_title="GPX Track Visualizer", layout="wide")

    st.set_page_config(page_title="GPX Track Visualizer", layout="wide")
    
    left_col, middle_col, right_col = st.columns([1, 6, 1])

    with middle_col:
    
        st.title("GPX Track Visualizer")
        st.write("Upload GPX files to visualize tracks on a map and create animations")
        
        # File uploader
        uploaded_files = st.file_uploader("Upload GPX files", type=["gpx"], accept_multiple_files=True)
        
        if uploaded_files:
            with st.spinner("Processing GPX files..."):
                combined_df = load_gpx_files(uploaded_files)
            
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
                    custom_title = st.text_input("Custom Title", "GPX Tracks Visualization", key="static_title")
                
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
                
                # Generate the preview map
                if st.button("Generate Static Map"):
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
                    
                    col1, col2, col3 = st.columns([1, 4, 1])
                    with col2:
                        if fig:
                            st.pyplot(fig)

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
                    anim_title = st.text_input("Animation Title", "GPX Tracks Animation", key="anim_title")
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

                
                # Generate the animation
                if st.button("Generate Animation"):
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

                            col1, col2, col3 = st.columns([1, 4, 1])
                            with col2:
                            
                                # Display the animation
                                st.success("Animation generated successfully!")
                                
                                # Display the video
                                video_file = open(animation_file, 'rb')
                                video_bytes = video_file.read()
                                st.video(video_bytes, loop=True)
                                
                                # Provide download link
                                if anim_title == "":
                                    st.markdown(get_binary_file_downloader_html(animation_file, "animation"), unsafe_allow_html=True)
                                else:
                                    st.markdown(get_binary_file_downloader_html(animation_file, anim_title), unsafe_allow_html=True)
                                
                                # Clean up
                                video_file.close()
                            
                        except Exception as e:
                            st.error(f"Error generating animation: {e}")

                st.divider()

            else:
                st.error("No valid data found in the uploaded GPX files")

if __name__ == "__main__":
    main()