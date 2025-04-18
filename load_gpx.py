#

import gpxpy
import os
import pandas as pd
import streamlit as st
import tempfile

# Load GPX files into a DataFrame
def load_gpx_files(uploaded_files) -> pd.DataFrame | None:

    """
    Load GPX files into a DataFrame.
    Args:
        uploaded_files (list): List of uploaded GPX files.
    Returns:
        pd.DataFrame: DataFrame containing track data.
    """

    df_list = []
    
    for uploaded_file in uploaded_files:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.gpx') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Parse the GPX file
            with open(tmp_path, "r") as f:
                gpx = gpxpy.parse(f)
            
            track_points = []
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        track_points.append((uploaded_file.name.replace(".gpx", ""), 
                                            point.time, 
                                            point.latitude, 
                                            point.longitude, 
                                            point.elevation))
            
            if track_points:  # Only process if there are points
                df = pd.DataFrame(track_points, columns=["track_name", "timestamp", "latitude", "longitude", "elevation"])
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                
                # Handle timezone conversion safely
                try:
                    df["timestamp"] = df["timestamp"].dt.tz_convert("US/Pacific")
                except:
                    try:
                        df["timestamp"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert("US/Pacific")
                    except:
                        st.warning(f"Could not convert timestamps for {uploaded_file.name}. Using as is.")
                
                df["time"] = df["timestamp"].dt.strftime("%H:%M:%S")
                hours = df["timestamp"].dt.hour
                minutes = df["timestamp"].dt.minute
                seconds = df["timestamp"].dt.second
                elapsed_seconds = hours * 3600 + minutes * 60 + seconds
                df["elapsed_seconds"] = elapsed_seconds
                
                df_list.append(df)
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")
        finally:
            # Delete the temporary file
            os.unlink(tmp_path)
    
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df
    else:
        return None