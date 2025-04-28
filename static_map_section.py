import streamlit as st
from providers import PROVIDERS

from custom_map_bounds import get_custom_map_bounds
from custom_time_range import get_custom_time_range
from generate_map import generate_map

def show_static_map_options(
    df_selected_tracks,
    default_lat_padding=0.125,
    default_lon_padding=0.125
):
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
        
        track_lat_delta = df_selected_tracks["latitude"].max() - df_selected_tracks["latitude"].min()
        track_lon_delta = df_selected_tracks["longitude"].max() - df_selected_tracks["longitude"].min()

        stat_lat_min = df_selected_tracks["latitude"].min() - stat_lat_padding*track_lat_delta
        stat_lat_max = df_selected_tracks["latitude"].max() + stat_lat_padding*track_lat_delta
        stat_lon_min = df_selected_tracks["longitude"].min() - stat_lon_padding*track_lon_delta
        stat_lon_max = df_selected_tracks["longitude"].max() + stat_lon_padding*track_lon_delta
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

def get_map_bounds(df, lat_padding, lon_padding):
    """Calculate map bounds based on data and padding"""
    if df is None or df.empty:
        return 0, 0, 0, 0
        
    track_lat_delta = df["latitude"].max() - df["latitude"].min()
    track_lon_delta = df["longitude"].max() - df["longitude"].min()

    lat_min = df["latitude"].min() - lat_padding * track_lat_delta
    lat_max = df["latitude"].max() + lat_padding * track_lat_delta
    lon_min = df["longitude"].min() - lon_padding * track_lon_delta
    lon_max = df["longitude"].max() + lon_padding * track_lon_delta
    
    return lat_min, lat_max, lon_min, lon_max

# def get_time_range(df):
#     """Get time range from data"""
#     if df is None or df.empty:
#         return 0, 24 * 3600
        
#     # Add time range slider logic here
#     # For brevity, returning min/max by default
#     return df["elapsed_seconds"].min(), df["elapsed_seconds"].max()

def generate_display_static_map(
        df_selected_tracks,
        stat_params,
        selected_tracks,
        session_key_prefix="stat"
):
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