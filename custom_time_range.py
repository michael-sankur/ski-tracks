#

import numpy as np
import pandas as pd
import streamlit as st


def get_custom_time_range(df_selected_tracks, prefix:str):
    """
    Custom time range selection for animation based on selected tracks.
    Allows users to select a specific time range for the animation.
    """

    start_seconds = 0
    end_seconds = 24 * 3600
    with st.expander("Custom Time Range", expanded=False):
        
        if df_selected_tracks is not None and not df_selected_tracks.empty:

            num_days = np.ceil(df_selected_tracks["elapsed_seconds"].max() / (24*3600))
            num_days = int(max(num_days, 1))

            data_time_min_hour = int(np.floor(df_selected_tracks["elapsed_seconds"].min() / 3600))
            data_time_min_minute = int(np.floor((df_selected_tracks["elapsed_seconds"].min() % 3600) / 60))

            data_time_max_hour = int(np.floor(df_selected_tracks["elapsed_seconds"].max() / 3600 - 24*(num_days-1)))
            data_time_max_minute = int(np.floor((df_selected_tracks["elapsed_seconds"].max() % 3600) / 60))

            st.write(f"Data time range: Day {1} at {data_time_min_hour:02d}:{data_time_min_minute:02d}  -  Day {num_days} at {data_time_max_hour:02d}:{data_time_max_minute:02d}")

            min_time = df_selected_tracks["elapsed_seconds"].min()
            min_time_rounded = min_time - (min_time % (30*60))
            max_time = df_selected_tracks["elapsed_seconds"].max()
            max_time_rounded = max_time - (max_time % (30*60)) + 30*60

            time_options = []
            for hour in range(num_days*24 + 1):
                for minute in [0, 15, 30, 45]:
                    if hour == num_days*24 and minute > 0:
                        continue
                    time_options.append(f"{hour:02d}:{minute:02d}")

            # Default to nearest 30-minute intervals
            time_slider_default_start_idx = min(int(2*np.floor(min_time_rounded / (30*60))), len(time_options)-1)
            time_slider_default_end_idx = min(int(2*np.ceil(max_time_rounded / (30*60))), len(time_options)-1)

            # Create a range slider using the select_slider
            time_slider_selected_range = st.select_slider(
                "Time range",
                options=time_options,
                value=(time_options[time_slider_default_start_idx], time_options[time_slider_default_end_idx]),
                key=f"{prefix}_time_slider_range"
            )

            start_time_selected, end_time_selected = time_slider_selected_range

            start_hour, start_minute = map(int, start_time_selected.split(":"))
            end_hour, end_minute = map(int, end_time_selected.split(":"))

            start_seconds = 3600 * start_hour + 60 * start_minute
            end_seconds = 3600 * end_hour + 60 * end_minute

        else:
            st.write("No data available for custom time range selection. Upload GPX files and select one or more tracks.")
    
    return start_seconds, end_seconds