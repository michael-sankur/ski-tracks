
import streamlit as st

def get_default_map_bounds(
    df_selected_tracks,
    lat_padding=0.125,
    lon_padding=0.125
):
    """Calculate default map bounds based on selected tracks and padding."""
    if df_selected_tracks is None or df_selected_tracks.empty:
        return 0, 0, 0, 0

    track_lat_delta = df_selected_tracks["latitude"].max() - df_selected_tracks["latitude"].min()
    track_lon_delta = df_selected_tracks["longitude"].max() - df_selected_tracks["longitude"].min()

    lat_min = df_selected_tracks["latitude"].min() - lat_padding * track_lat_delta
    lat_max = df_selected_tracks["latitude"].max() + lat_padding * track_lat_delta
    lon_min = df_selected_tracks["longitude"].min() - lon_padding * track_lon_delta
    lon_max = df_selected_tracks["longitude"].max() + lon_padding * track_lon_delta

    return lat_min, lat_max, lon_min, lon_max

def get_custom_map_bounds(
    df_selected_tracks,
    prefix:str,
    lat_padding=0.125,
    lon_padding=0.125
):

    # Custom map bounds
    lat_min = 0
    lat_max = 0
    lon_min = 0
    lon_max = 0
    with st.expander("Custom Latitude and Longitude Bounds", expanded=False):
        
        if df_selected_tracks is not None and not df_selected_tracks.empty:

            track_lat_delta = df_selected_tracks["latitude"].max() - df_selected_tracks["latitude"].min()
            track_lon_delta = df_selected_tracks["longitude"].max() - df_selected_tracks["longitude"].min()

            lat_min_default = df_selected_tracks["latitude"].min() - lat_padding*track_lat_delta
            lat_max_default = df_selected_tracks["latitude"].max() + lat_padding*track_lat_delta
            lon_min_default = df_selected_tracks["longitude"].min() - lon_padding*track_lon_delta
            lon_max_default = df_selected_tracks["longitude"].max() + lon_padding*track_lon_delta

            custom_bounds_mode = st.radio(
                label="Select custom bounds mode:",
                options=["Use standard lat/lon padding", "Use custom NSEW padding", "Use custom latitude and longitude"],
                index=0,
                key=f"{prefix}_custom_bounds_mode",
                horizontal=True
            )
            if custom_bounds_mode == "Use standard lat/lon padding":
                lat_min = lat_min_default
                lat_max = lat_max_default
                lon_min = lon_min_default
                lon_max = lon_max_default

                st.write(f"Map latitude extents: {lat_min:.4f} to {lat_max:.4f}")
                st.write(f"Map longitude extents: {lon_min:.4f} to {lon_max:.4f}")

            elif custom_bounds_mode == "Use custom NSEW padding":
                north_padding = st.number_input("North Padding", min_value=0.0, max_value=1.0, value=lat_padding, step=0.005, format="%.3f", key=f"{prefix}_north_padding")
                south_padding = st.number_input("South Padding", min_value=0.0, max_value=1.0, value=lat_padding, step=0.005, format="%.3f", key=f"{prefix}_south_padding")
                east_padding = st.number_input("East Padding", min_value=0.0, max_value=1.0, value=lon_padding, step=0.005, format="%.3f", key=f"{prefix}_east_padding")
                west_padding = st.number_input("West Padding", min_value=0.0, max_value=1.0, value=lon_padding, step=0.005, format="%.3f", key=f"{prefix}_west_padding")

                lat_min = df_selected_tracks["latitude"].min() - south_padding*track_lat_delta
                lat_max = df_selected_tracks["latitude"].max() + north_padding*track_lat_delta
                lon_min = df_selected_tracks["longitude"].min() - west_padding*track_lon_delta
                lon_max = df_selected_tracks["longitude"].max() + east_padding*track_lon_delta

                st.write(f"Map latitude extents: {lat_min:.4f} to {lat_max:.4f}")
                st.write(f"Map longitude extents: {lon_min:.4f} to {lon_max:.4f}")
            elif custom_bounds_mode == "Use custom latitude and longitude":                        
                lat_min = st.number_input("Min Latitude", value=lat_min_default, format="%.4f", step=0.005, key=f"{prefix}_lat_min")
                lat_max = st.number_input("Max Latitude", value=lat_max_default, format="%.4f", step=0.005, key=f"{prefix}_lat_max")
                lon_min = st.number_input("Min Longitude", value=lon_min_default, format="%.4f", step=0.005, key=f"{prefix}_lon_min")                        
                lon_max = st.number_input("Max Longitude", value=lon_max_default, format="%.4f", step=0.005, key=f"{prefix}_lon_max")
        else:
            st.write("No data available for custom bounds selection. Upload GPX files and select one or more tracks.")

    return lat_min, lat_max, lon_min, lon_max