# Generate static map

import contextily as ctx
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from providers import PROVIDERS
from util import get_distinct_colors

def generate_map(
    combined_df,
    *,
    map_style="USTopo",
    fig_width=8,
    lat_buffer=0.125,
    lon_buffer=0.125, 
    lat_min=None,
    lat_max=None,
    lon_min=None,
    lon_max=None,
    title="",
    start_end_points=False,
    show_legend=False,
    show_coordinates=False
):
    """
    Preview the map with all tracks fully plotted.
    Args:
        combined_df (pd.DataFrame): DataFrame containing track data.
        map_style (str): Basemap style.
        fig_width (float): Width of the figure.
        lat_buffer (float): Buffer for latitude bounds.
        lon_buffer (float): Buffer for longitude bounds.
        lat_min (float): Minimum latitude for figure bounds.
        lat_max (float): Maximum latitude for figure bounds.
        lon_min (float): Minimum longitude for figure bounds.
        lon_max (float): Maximum longitude for figure bounds.
        title (str): Title of the map.
        start_end_points (bool): Whether to show start and end points.
        show_legend (bool): Whether to show legend.
    Returns:
        fig: Matplotlib figure object.
    """

    # Determine the latitude and longitude bounds of the tracks
    track_lat_delta = combined_df["latitude"].max() - combined_df["latitude"].min()
    track_lon_delta = combined_df["longitude"].max() - combined_df["longitude"].min()
    
    # Add buffers to the bounds as portion of existing difference between upper and lower bounds
    track_lat_min = combined_df["latitude"].min() - lat_buffer*track_lat_delta
    track_lat_max = combined_df["latitude"].max() + lat_buffer*track_lat_delta
    track_lon_min = combined_df["longitude"].min() - lon_buffer*track_lon_delta
    track_lon_max = combined_df["longitude"].max() + lon_buffer*track_lon_delta
    
    # Use custom bounds if provided, otherwise use data bounds
    fig_lat_min = lat_min if lat_min is not None else track_lat_min
    fig_lat_max = lat_max if lat_max is not None else track_lat_max
    fig_lon_min = lon_min if lon_min is not None else track_lon_min
    fig_lon_max = lon_max if lon_max is not None else track_lon_max
    
    # Calculate figure height based on aspect ratio
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
    
    try:
        # Add the basemap
        ctx.add_basemap(
            ax, 
            source=provider,
            crs="EPSG:4326",
            attribution_size=8
        )

        ax.set_xlabel("")
        ax.set_ylabel("")
        if not show_coordinates:
            ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        
        # Generate colors for all tracks
        track_names = combined_df["track_name"].unique()
        colors = get_distinct_colors(len(track_names))
        color_map = dict(zip(track_names, colors))
        
        # Plot all tracks with their full paths
        for track_name in track_names:
            track_data = combined_df[combined_df["track_name"] == track_name]
            
            # Sort by timestamp to ensure proper path drawing
            track_data = track_data.sort_values(by="elapsed_seconds")
            
            # Plot the full track
            ax.plot(track_data["longitude"], track_data["latitude"], 
                    color=color_map[track_name], linewidth=2, alpha=0.8,
                    label=track_name)
            
            if start_end_points:
                # Mark the start point with a green circle
                start_point = track_data.iloc[0]
                ax.plot(start_point["longitude"], start_point["latitude"], 'go', markersize=4)
                
                # Mark the end point with a red square
                end_point = track_data.iloc[-1]
                ax.plot(end_point["longitude"], end_point["latitude"], 'rs', markersize=4)
        
        # Add legend if there are multiple tracks
        if show_legend:
            ax.legend(loc='upper right', fontsize=8)
        
        if title != "":
            ax.set_title(title, fontsize=12)
        
        plt.tight_layout()
        
        return fig
    
    except Exception as e:
        st.error(f"Error loading basemap: {e}")
        return None