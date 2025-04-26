#

import contextily as ctx
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import tempfile

from providers import PROVIDERS
from util import get_distinct_colors

# Function to create the animation
def generate_animation(
        df,
        *,
        mode="track",
        duration=15,
        fps=24,
        start_time=None,
        end_time=None,
        dpi=150,
        trail_duration=3600,
        marker_size=8,
        line_width=2,
        map_style="USTopo",
        fig_width=8,
        lat_min=None,
        lat_max=None,
        lon_min=None,
        lon_max=None,
        title="",
        show_time=True,
        show_legend=False,
        show_coordinates=False
    ):
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
        st.error("Invalid mode specified. Use 'track' or 'file'.")
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
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
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
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    
    # Save the animation as an MP4 file
    writer = animation.FFMpegWriter(fps=fps, metadata=dict(artist="GPX Visualizer"), bitrate=1800)
    anim.save(temp_file.name, writer=writer, dpi=dpi)
    
    # Close the matplotlib figure to free up memory
    plt.close(fig)
    
    return temp_file.name