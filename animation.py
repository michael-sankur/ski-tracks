# Animation options and display section for Streamlit app

import contextily as ctx
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import tempfile
from typing import Any, Dict, List, Optional

from custom_map_bounds import get_custom_map_bounds, get_default_map_bounds
from custom_time_range import get_custom_time_range
# from generate_animation import generate_animation
from providers import PROVIDERS
from util import get_distinct_colors, get_params_hash


def show_animation_options(
    df_selected_tracks: pd.DataFrame,
    default_lat_padding:float=0.125,
    default_lon_padding:float=0.125
) -> Dict:
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

        anim_lat_min, anim_lat_max, anim_lon_min, anim_lon_max = get_default_map_bounds(
            df_selected_tracks,
            lat_padding=anim_lat_padding,
            lon_padding=anim_lon_padding
        )
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
        df_selected_tracks: pd.DataFrame,
        anim_params: Dict[str, Any],
        selected_tracks: List[str],
        session_key_prefix:str="anim"
) -> None:
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


#

from click import Option
import contextily as ctx
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import tempfile
from typing import Optional

from providers import PROVIDERS
from util import get_distinct_colors

# Function to create the animation
def generate_animation(
    df:pd.DataFrame,
    *,
    mode:str="track",
    duration:int=15,
    fps:int=24,
    start_time:Optional[int]=None,
    end_time:Optional[int]=None,
    dpi:int=150,
    trail_duration:int=24*3600,
    marker_size:int=8,
    line_width:int=2,
    map_style:str="USTopo",
    fig_width:int=8,
    lat_min:Optional[float]=None,
    lat_max:Optional[float]=None,
    lon_min:Optional[float]=None,
    lon_max:Optional[float]=None,
    title:str="",
    show_time:bool=True,
    show_legend:bool=False,
    show_coordinates:bool=False
) -> Optional[str]:
    """
    Create an animation of GPX tracks and return it as an HTML5 video element
    """
    # Determine time range if not specified
    if start_time is None:
        start_time = df["elapsed_seconds"].min()
    if end_time is None:
        end_time = df["elapsed_seconds"].max()

    track_names = []
    if mode == "track":
        track_names = df["track_name"].unique()
    elif mode == "file":
        track_names = df["file_name"].unique()
    else:
        st.error("Invalid mode specified.")
        return None

    colors = get_distinct_colors(len(track_names))
    color_map = dict(zip(track_names, colors))
    
    # Determine the latitude and longitude difference of the tracks
    track_lat_delta = df["latitude"].max() - df["latitude"].min()
    track_lon_delta = df["longitude"].max() - df["longitude"].min()
    
    # Calculate default latitude and longitude bounds if not provided
    anim_lat_min = lat_min if lat_min else df["latitude"].min() - 0.125 * track_lat_delta
    anim_lat_max = lat_max if lat_min else df["latitude"].max() + 0.125 * track_lat_delta
    anim_lon_min = lon_min if lon_min else df["longitude"].min() - 0.125 * track_lon_delta
    anim_lon_max = lon_max if lon_max else df["longitude"].max() + 0.125 * track_lon_delta
    
    fig_lat_diff = anim_lat_max - anim_lat_min
    fig_lon_diff = anim_lon_max - anim_lon_min
    
    fig_lat_lon_ratio = fig_lat_diff / fig_lon_diff
    
    fig_height = np.round(fig_width * fig_lat_lon_ratio, 2)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # Set limits
    ax.set_xlim(anim_lon_min, anim_lon_max)
    ax.set_ylim(anim_lat_min, anim_lat_max)
    
    provider = PROVIDERS.get(map_style, ctx.providers.USGS.USTopo)
    
    # Add terrain basemap if requested
    
    try:
        # Add the basemap
        ctx.add_basemap(
            ax, 
            source=provider,
            crs="EPSG:4326",  # WGS84 coordinate system used by GPS
            attribution_size=4,
        )
        
        # Make sure the GPX tracks will be visible on top of the map
        
    except Exception as e:
        print(f"Could not add terrain map: {e}. Continuing without terrain.")
    
    # Add a timestamp text
    time_text = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=12, 
                        bbox=dict(facecolor="white", alpha=1.0, edgecolor="none"))
    
    # Create a legend with the track names
    if show_legend and len(track_names) > 1:
        legend_elements = [Line2D([0], [0], color=color_map[name], lw=2, label=name) 
                           for name in track_names]
        ax.legend(handles=legend_elements, loc="upper right")

    ax.set_xlabel("")
    ax.set_ylabel("")
    if show_coordinates:
        pass
    else:
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    
    # Create line objects for each track
    lines = {}
    points = {}
    
    for track_name in track_names:
        track_data = df[df["track_name"] == track_name]
        line, = ax.plot([], [], lw=line_width, color=color_map[track_name], alpha=0.7)
        point, = ax.plot([], [], "o", markersize=marker_size, color=color_map[track_name])
        lines[track_name] = line
        points[track_name] = point
    
    # Initialize with first frame
    def init():
        for line in lines.values():
            line.set_data([], [])
        for point in points.values():
            point.set_data([], [])
        time_text.set_text("")
        return list(lines.values()) + list(points.values()) + [time_text]
    
    # Update function for each frame
    def update(frame):
        animation_time_normalized = min(frame / (fps * duration), 1.0)
        current_time_seconds = start_time + (end_time - start_time) * animation_time_normalized
        
        if show_time:
            # Format the time as HH:MM
            display_time_seconds = (np.floor(current_time_seconds / (5*60))) * (5*60)
            time_str = pd.to_datetime(display_time_seconds, unit="s").strftime("%H:%M")
            time_text.set_text(f"Time: {time_str}")
        else:
            time_text.set_text("")

        # ax.set_title(f"{animation_time_normalized}, {current_time_seconds}, {start_time}, {end_time}", fontsize=14, fontweight="bold")
        
        for track_name in track_names:
            # Get data for the current track
            track_data = df[df["track_name"] == track_name]

            mask_start_time = track_data["elapsed_seconds"] >= start_time
            track_data = track_data[mask_start_time]
            
            # Get data up to current time
            mask_current_time = track_data["elapsed_seconds"] <= current_time_seconds
            visible_data = track_data[mask_current_time]
            
            if not visible_data.empty:

                if trail_duration < (end_time - start_time) and len(visible_data) >= 1:
                    min_visible_time = max(start_time, current_time_seconds - trail_duration)
                    trail_mask = visible_data["elapsed_seconds"] >= min_visible_time
                    trail_data = visible_data[trail_mask]
                else:
                    trail_data = visible_data
                
                # Update the line
                lines[track_name].set_data(trail_data["longitude"], trail_data["latitude"])
                
                # Update the current position point
                current_pos = visible_data.iloc[-1]
                points[track_name].set_data([current_pos["longitude"]], [current_pos["latitude"]])
                
            else:
                lines[track_name].set_data([], [])
                points[track_name].set_data([], [])
        
        return list(lines.values()) + list(points.values()) + [time_text]
    
    # Calculate animation duration and frames
    frames = fps * duration + 1
    
    # Create the animation
    anim = animation.FuncAnimation(
        fig, update, frames=frames, init_func=init, blit=True, interval=1000/fps
    )
    
    # Save the animation to a temporary file and return it
    temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    
    # Save the animation as an MP4 file
    writer = animation.FFMpegWriter(fps=fps, metadata=dict(artist="GPX Visualizer"), bitrate=1800)
    anim.save(temp_file.name, writer=writer, dpi=dpi)
    
    # Close the matplotlib figure to free up memory
    plt.close(fig)
    
    return temp_file.name