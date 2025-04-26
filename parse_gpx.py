#

import gpxpy
import os
import pandas as pd
import streamlit as st
import tempfile

# Function to convert timestamps in a DataFrame column to a specified timezone
def convert_timestamp_timezone(df, column_name, target_tz="US/Pacific", file_name=None):
    """
    Convert timestamps in a DataFrame column to the target timezone.
    
    Args:
        df (pd.DataFrame): DataFrame containing the timestamp column
        column_name (str): Name of the column containing timestamps
        target_tz (str): Target timezone to convert to
        file_name (str, optional): Name of the file for warning messages
        
    Returns:
        pd.DataFrame: DataFrame with converted timestamps
    """
    original_df = df.copy()
    
    # Check if timestamps already have timezone info
    sample_timestamp = df[column_name].iloc[0] if not df.empty else None
    has_tzinfo = sample_timestamp is not None and sample_timestamp.tzinfo is not None
    
    try:
        if has_tzinfo:
            # Timestamps already have timezone info, just convert
            df[column_name] = df[column_name].dt.tz_convert(target_tz)
        else:
            # Timestamps don't have timezone, assume UTC and convert
            df[column_name] = df[column_name].dt.tz_localize("UTC").dt.tz_convert(target_tz)
        return df
    except Exception as e:
        # If conversion fails, issue a warning and return original data
        if file_name:
            st.warning(f"Could not convert timestamps for {file_name}: {str(e)}. Using as is.")
        return original_df

# Load GPX files into a DataFrame
def parse_gpx_files(uploaded_files) -> pd.DataFrame | None:

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
            
            
            for track in gpx.tracks:
                track_points = []
                for segment in track.segments:
                    for point in segment.points:
                        track_points.append(
                            (uploaded_file.name.replace(".gpx", ""),
                            track.name,
                            point.time,
                            point.latitude,
                            point.longitude,
                            point.elevation)
                        )

                if track_points:  # Only process if there are points
                    df = pd.DataFrame(track_points, columns=["file_name", "track_name", "timestamp", "latitude", "longitude", "elevation"])
                    df["timestamp"] = pd.to_datetime(df["timestamp"])

                    df = convert_timestamp_timezone(df, "timestamp", file_name=uploaded_file.name)


                    min_track_timestamp = df["timestamp"].min()

                    # Create a datetime object for midnight of the day of the minimum timestamp
                    if min_track_timestamp.tzinfo is not None:
                    # Create a timezone-aware datetime object for midnight of the minimum timestamp's day
                        start_time = pd.Timestamp(
                            year=min_track_timestamp.year,
                            month=min_track_timestamp.month,
                            day=min_track_timestamp.day,
                            hour=0,
                            minute=0,
                            second=0,
                            tz=min_track_timestamp.tzinfo  # Use the same timezone as your data
                        )
                    else:
                        # If timestamps are timezone-naive, create a naive midnight datetime
                        start_time = pd.Timestamp(
                            year=min_track_timestamp.year,
                            month=min_track_timestamp.month,
                            day=min_track_timestamp.day,
                            hour=0,
                            minute=0,
                            second=0
                        )

                    # Calculate the difference in seconds between each timestamp and start_time
                    df["elapsed_seconds"] = (df["timestamp"] - start_time).dt.total_seconds()
                    
                    df["time"] = df["timestamp"].dt.strftime("%H:%M:%S")
                    
                    for track_name in sorted(df["track_name"].unique()):
                        print(f"Track: {track_name}, Points: {len(df[df['track_name'] == track_name])}")
                        print(f"Elapsed second: {df[df['track_name'] == track_name]['elapsed_seconds'].min()}")
                        print(f"Elapsed second: {df[df['track_name'] == track_name]['elapsed_seconds'].max()}")

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