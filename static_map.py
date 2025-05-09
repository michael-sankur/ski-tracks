#

import contextily as ctx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from providers import PROVIDERS
from typing import Any, Dict, List

from custom_map_bounds import get_custom_map_bounds, get_default_map_bounds
from custom_time_range import get_custom_time_range
from providers import PROVIDERS
from util import get_distinct_colors

def show_static_map_options(
    df_selected_tracks:pd.DataFrame,
    default_lat_padding:float=0.125,
    default_lon_padding:float=0.125
) -> Dict:
    """Display the static map options UI and return the selected parameters"""
    st.header("Generate Static Visualization")
    st.write("Create a static visualization of the selected GPX tracks on the same map.")

    # Split into columns for map and visualization settings
    map_col, vis_col = st.columns(2)
    
    with map_col:
        st.subheader("Map Settings")
        stat_map_style = st.selectbox("Map Style", list(PROVIDERS.keys()), index=12, key="stat_map_style")
        stat_fig_width = st.number_input("Figure Width (inches):", min_value=6.0, max_value=18.0, value=12.0, step=0.5, format="%.1f", key="stat_fig_width")     
        stat_lat_padding = st.number_input("Latitude Padding", min_value=0.0, max_value=1.0, value=default_lat_padding, step=0.005, format="%.3f",key="stat_lat_padding")
        stat_lon_padding = st.number_input("Longitude Padding", min_value=0.0, max_value=1.0, value=default_lon_padding, step=0.005, format="%.3f",key="stat_lon_padding")
        
        stat_lat_min, stat_lat_max, stat_lon_min, stat_lon_max = get_default_map_bounds(
            df_selected_tracks,
            lat_padding=stat_lat_padding,
            lon_padding=stat_lon_padding
        )
        if df_selected_tracks is not None and not df_selected_tracks.empty:
            stat_lat_min, stat_lat_max, stat_lon_min, stat_lon_max = get_custom_map_bounds(
                df_selected_tracks,
                prefix="stat",
                lat_padding=stat_lat_padding,
                lon_padding=stat_lon_padding
            )
    
    with vis_col:
        st.subheader("Visualization Options")
        stat_show_start_end_points = st.checkbox("Show start and end points", value=True, key="stat_show_start_end")
        stat_show_legend = st.checkbox("Show legend", value=False, key="stat_show_legend")
        stat_show_coordinates = st.checkbox("Show coordinates", value=False, key="stat_show_coordinates")

        stat_line_width = st.slider("Line width", min_value=1, max_value=6, value=3, step=1, key="stat_line_width")
        stat_marker_size = st.slider("Start and end point marker size", min_value=2, max_value=12, value=6, step=1, key="stat_marker_size")
        
        # Get time range
        # stat_start_seconds, stat_end_seconds = get_time_range(df_selected_tracks)

        stat_start_seconds = 0
        stat_end_seconds = 24 * 3600
        if df_selected_tracks is not None and not df_selected_tracks.empty:
            stat_start_seconds, stat_end_seconds = get_custom_time_range(df_selected_tracks=df_selected_tracks, prefix="stat")

            
    
    # Title input in center column
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        stat_title = st.text_input("Title", "", key="stat_title")
    
    # Return parameters as a dictionary
    return {
        "stat_map_style": stat_map_style,
        "stat_fig_width": stat_fig_width,
        "stat_lat_min": stat_lat_min,
        "stat_lat_max": stat_lat_max,
        "stat_lon_min": stat_lon_min,
        "stat_lon_max": stat_lon_max,
        "stat_show_start_end_points": stat_show_start_end_points,
        "stat_show_legend": stat_show_legend,            
        "stat_show_coordinates": stat_show_coordinates,
        "stat_line_width": stat_line_width,
        "stat_marker_size": stat_marker_size,
        "stat_title": stat_title,
        "stat_start_seconds": stat_start_seconds,
        "stat_end_seconds": stat_end_seconds,
    }

def generate_display_static_map(
        df_selected_tracks: pd.DataFrame,
        stat_params: Dict[str, Any],
        selected_tracks: List[str],
        session_key_prefix:str ="stat"
) -> None:
    """Generate static map based on parameters"""
    vis_mode = "track"  # Could be parameterized
    
    # Use the appropriate session state variables based on the prefix
    map_generated_key = f"{session_key_prefix}_map_generated"
    map_fig_key = f"{session_key_prefix}_map_fig"
    params_hash_key = f"{session_key_prefix}_params_hash"
    current_params_key = f"{session_key_prefix}_current_params"
    
    # Initialize session state variables if they don't exist
    if map_generated_key not in st.session_state:
        st.session_state[map_generated_key] = False
    if map_fig_key not in st.session_state:
        st.session_state[map_fig_key] = None
    if params_hash_key not in st.session_state:
        st.session_state[params_hash_key] = ""
    if current_params_key not in st.session_state:
        st.session_state[current_params_key] = {}
    
    # Get parameter hash for comparison
    from util import get_params_hash
    current_hash = get_params_hash(stat_params)
    params_changed = current_hash != st.session_state[params_hash_key]
    
    # Show parameter change notification if applicable
    if params_changed and st.session_state[map_generated_key]:
        st.info("Map parameters have changed. Click 'Generate Static Map' to update the visualization.")
    
    # Generate button - placed before the map
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        generate_stat_clicked = st.button(
            "Generate Static Map",
            disabled=(df_selected_tracks is None or df_selected_tracks.empty))
    
        # Create a container for the map display - this prevents flickering
        map_container = st.container()
        
        # Generate new map if button clicked
        if generate_stat_clicked:
            with st.spinner("Generating map..."):
                fig = generate_map(
                    df_selected_tracks,
                    mode=vis_mode,
                    map_style=stat_params["stat_map_style"],
                    fig_width=int(stat_params["stat_fig_width"]),
                    lat_min=stat_params["stat_lat_min"],
                    lat_max=stat_params["stat_lat_max"],
                    lon_min=stat_params["stat_lon_min"],
                    lon_max=stat_params["stat_lon_max"],
                    show_start_end_points=stat_params["stat_show_start_end_points"],
                    show_legend=stat_params["stat_show_legend"],
                    show_coordinates=stat_params["stat_show_coordinates"],
                    line_width=stat_params["stat_line_width"],
                    start_end_marker_size=stat_params["stat_marker_size"],
                    title=stat_params["stat_title"],
                    start_time=stat_params["stat_start_seconds"],
                    end_time=stat_params["stat_end_seconds"]
                )
                # Update session state with new map
                st.session_state[map_fig_key] = fig
                st.session_state[map_generated_key] = True
                st.session_state[params_hash_key] = current_hash
                st.session_state[current_params_key] = stat_params.copy()
        
        # Display the map in the container
        with map_container:
            if st.session_state[map_fig_key] is not None:
                st.pyplot(st.session_state[map_fig_key])
            elif not st.session_state[map_generated_key]:
                st.info("Click 'Generate Static Map' to create visualization")


def generate_map(
    df,
    *,
    mode="track",
    map_style="USTopo",
    fig_width=8, 
    lat_min=None,
    lat_max=None,
    lon_min=None,
    lon_max=None,
    title="",
    show_start_end_points=False,
    show_legend=False,
    show_coordinates=False,
    line_width=4,
    start_end_marker_size=8,
    start_time=0,
    end_time=24*3600
):
    """
    Generate a static map with GPX tracks plotted on it.
    Args:
        df (pd.DataFrame): DataFrame containing GPX track data with columns 'latitude', 'longitude', 'track_name', 'file_name', and 'elapsed_seconds'.
        mode (str): Mode of plotting, either "track" or "file".
        map_style (str): Style of the basemap to use.
        fig_width (float): Width of the figure in inches.
        lat_min, lat_max, lon_min, lon_max (float): Optional latitude and longitude bounds for the map.
        title (str): Title of the map.
        show_start_end_points (bool): Whether to show start and end points of tracks.
        show_legend (bool): Whether to show a legend for the tracks.
        show_coordinates (bool): Whether to show coordinates on the axes.
        line_width (float): Width of the lines representing tracks.
        start_end_marker_size (int): Size of markers for start and end points.
        start_time, end_time (int): Time range in seconds to filter tracks.
    Returns:
        fig (matplotlib.figure.Figure): The generated map figure.
    """

    try:

        # Determine the latitude and longitude difference of the tracks
        track_lat_delta = df["latitude"].max() - df["latitude"].min()
        track_lon_delta = df["longitude"].max() - df["longitude"].min()
        
        # Calculate default latitude and longitude bounds if not provided
        fig_lat_min = lat_min if lat_min else df["latitude"].min() - 0.125 * track_lat_delta
        fig_lat_max = lat_max if lat_min else df["latitude"].max() + 0.125 * track_lat_delta
        fig_lon_min = lon_min if lon_min else df["longitude"].min() - 0.125 * track_lon_delta
        fig_lon_max = lon_max if lon_max else df["longitude"].max() + 0.125 * track_lon_delta
        
        # Calculate figure aspect ratio and height from latitude and longitude bounds
        fig_lat_diff = fig_lat_max - fig_lat_min
        fig_lon_diff = fig_lon_max - fig_lon_min    
        fig_lat_lon_ratio = fig_lat_diff / fig_lon_diff
        fig_height = np.round(fig_width * fig_lat_lon_ratio, 2)
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Set limits
        ax.set_xlim(fig_lon_min, fig_lon_max)
        ax.set_ylim(fig_lat_min, fig_lat_max)
        
        provider = PROVIDERS.get(map_style, ctx.providers.USGS.USTopo)
    
        # Add the basemap
        ctx.add_basemap(
            ax, 
            source=provider,
            crs="EPSG:4326",
            attribution_size=2
        )

        ax.set_xlabel("")
        ax.set_ylabel("")
        
        
        # Generate colors for all tracks
        track_names = []
        if mode == "track":
            track_names = sorted(df["track_name"].unique())
        elif mode == "file":
            track_names = sorted(df["file_name"].unique())
        else:
            st.error("Invalid mode specified. Use 'track' or 'file'.")
            return None
        colors = get_distinct_colors(len(track_names))
        color_map = dict(zip(track_names, colors))

        # Plot all tracks with their full paths
        for track_name in track_names:
            track_data = df[
                (df["track_name"] == track_name) & 
                (df["elapsed_seconds"] >= start_time) & 
                (df["elapsed_seconds"] <= end_time)
            ]

            if len(track_data) == 0:
                continue
            else:

                # Sort by timestamp to ensure proper path drawing
                track_data = track_data.sort_values(by="elapsed_seconds")
                
                # Plot the full track
                ax.plot(
                    track_data["longitude"],
                    track_data["latitude"], 
                    color=color_map[track_name],
                    linewidth=line_width,
                    alpha=1.0,
                    label=track_name
                )
                
                if show_start_end_points:
                    # Mark the start point with a green circle
                    start_point = track_data.iloc[0]
                    ax.plot(start_point["longitude"], start_point["latitude"], 'go', markersize=start_end_marker_size)
                    
                    # Mark the end point with a red square
                    end_point = track_data.iloc[-1]
                    ax.plot(end_point["longitude"], end_point["latitude"], 'rs', markersize=start_end_marker_size)
        
        # Add legend if there are multiple tracks
        if show_legend:
            ax.legend(loc='upper right', fontsize=8)

        if show_coordinates:
            pass
        else:
            ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        
        if title != "":
            ax.set_title(title, fontsize=12)
        
        plt.tight_layout()
        
        return fig
    
    except Exception as e:
        st.error(f"Error loading basemap: {e}")
        return None