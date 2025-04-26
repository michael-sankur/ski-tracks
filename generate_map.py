# Generate static map

import contextily as ctx
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from providers import PROVIDERS
from util import get_distinct_colors

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