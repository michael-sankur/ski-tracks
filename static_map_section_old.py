
        # with stat_map_settings_column:
        #     st.subheader("Map Settings")
        #     stat_map_style = st.selectbox("Map Style", list(PROVIDERS.keys()), index=12, key="stat_map_style")
        #     stat_fig_width = st.number_input("Figure Width (inches):", min_value=6.0, max_value=18.0, value=12.0, step=0.5, format="%.1f", key="stat_fig_width")     
        #     stat_lat_padding = st.number_input("Latitude Padding - extra space north and south of the extents of displayed tracks", min_value=0.0, max_value=1.0, value=0.125, step=0.005, format="%.3f",key="stat_lat_padding")
        #     stat_lon_padding = st.number_input("Longitude Padding - extra space east and west of the extents of displayed tracks", min_value=0.0, max_value=1.0, value=0.125, step=0.005, format="%.3f",key="stat_lon_padding")

        #     # Custom map bounds
        #     stat_lat_min = 0
        #     stat_lat_max = 0
        #     stat_lon_min = 0
        #     stat_lon_max = 0
        #     with st.expander("Custom Latitude and Longitude Bounds", expanded=False):
                
        #         if uploaded_files and df_selected_tracks is not None and not df_selected_tracks.empty:

        #             stat_track_lat_delta = df_selected_tracks["latitude"].max() - df_selected_tracks["latitude"].min()
        #             stat_track_lon_delta = df_selected_tracks["longitude"].max() - df_selected_tracks["longitude"].min()

        #             stat_lat_min_default = df_selected_tracks["latitude"].min() - stat_lat_padding*stat_track_lat_delta
        #             stat_lat_max_default = df_selected_tracks["latitude"].max() + stat_lat_padding*stat_track_lat_delta
        #             stat_lon_min_default = df_selected_tracks["longitude"].min() - stat_lon_padding*stat_track_lon_delta
        #             stat_lon_max_default = df_selected_tracks["longitude"].max() + stat_lon_padding*stat_track_lon_delta

        #             stat_custom_bounds_mode = st.radio(
        #                 label="Select custom bounds mode:",
        #                 options=["Use standard lat/lon padding", "Use custom NSEW padding", "Use custom latitude and longitude"],
        #                 index=0,
        #                 key="stat_custom_bounds_mode",
        #                 horizontal=True
        #             )
        #             if stat_custom_bounds_mode == "Use standard lat/lon padding":
        #                 stat_lat_min = stat_lat_min_default
        #                 stat_lat_max = stat_lat_max_default
        #                 stat_lon_min = stat_lon_min_default
        #                 stat_lon_max = stat_lon_max_default

        #                 st.write(f"Map latitude extents: {stat_lat_min:.4f} to {stat_lat_max:.4f}")
        #                 st.write(f"Map longitude extents: {stat_lon_min:.4f} to {stat_lon_max:.4f}")

        #             elif stat_custom_bounds_mode == "Use custom NSEW padding":
        #                 stat_north_padding = st.number_input("North Padding", min_value=0.0, max_value=1.0, value=stat_lat_padding, step=0.005, format="%.3f", key="stat_north_padding")
        #                 stat_south_padding = st.number_input("South Padding", min_value=0.0, max_value=1.0, value=stat_lat_padding, step=0.005, format="%.3f", key="stat_south_padding")
        #                 stat_east_padding = st.number_input("East Padding", min_value=0.0, max_value=1.0, value=stat_lon_padding, step=0.005, format="%.3f", key="stat_east_padding")
        #                 stat_west_padding = st.number_input("West Padding", min_value=0.0, max_value=1.0, value=stat_lon_padding, step=0.005, format="%.3f", key="stat_west_padding")

        #                 stat_lat_min = df_selected_tracks["latitude"].min() - stat_south_padding*stat_track_lat_delta
        #                 stat_lat_max = df_selected_tracks["latitude"].max() + stat_north_padding*stat_track_lat_delta
        #                 stat_lon_min = df_selected_tracks["longitude"].min() - stat_west_padding*stat_track_lon_delta
        #                 stat_lon_max = df_selected_tracks["longitude"].max() + stat_east_padding*stat_track_lon_delta

        #                 st.write(f"Map latitude extents: {stat_lat_min:.4f} to {stat_lat_max:.4f}")
        #                 st.write(f"Map longitude extents: {stat_lon_min:.4f} to {stat_lon_max:.4f}")
        #             elif stat_custom_bounds_mode == "Use custom latitude and longitude":                        
        #                 stat_lat_min = st.number_input("Min Latitude", value=stat_lat_min_default, format="%.4f", step=0.005, key="stat_lat_min")
        #                 stat_lat_max = st.number_input("Max Latitude", value=stat_lat_max_default, format="%.4f", step=0.005, key="stat_lat_max")
        #                 stat_lon_min = st.number_input("Min Longitude", value=stat_lon_min_default, format="%.4f", step=0.005, key="stat_lon_min")                        
        #                 stat_lon_max = st.number_input("Max Longitude", value=stat_lon_max_default, format="%.4f", step=0.005, key="stat_lon_max")
        #         else:
        #             st.write("No data available for custom bounds selection. Upload GPX files and select one or more tracks.")
        
        # with stat_vis_settings_column:
        #     st.subheader("Visualization Options")
        #     stat_show_start_end_points = st.checkbox("Show start and end points", value=True, key="stat_show_start_end")
        #     stat_show_legend = st.checkbox("Show legend", value=False, key="stat_show_legend")
        #     stat_show_coordinates = st.checkbox("Show coordinates", value=False, key="stat_show_coordinates")

        #     stat_line_width = st.slider("Line width", min_value=1, max_value=6, value=3, step=1, key="stat_line_width")
        #     stat_marker_size = st.slider("Start and end point marker size", min_value=2, max_value=12, value=6, step=1, key="stat_marker_size")

        #     stat_start_seconds = 0
        #     stat_end_seconds = 24 * 3600
        #     with st.expander("Custom Time Range", expanded=False):
                
        #         if uploaded_files and df_selected_tracks is not None and not df_selected_tracks.empty:

        #             stat_num_days = np.ceil(df_selected_tracks["elapsed_seconds"].max() / (24*3600))
        #             stat_num_days = int(max(stat_num_days, 1))

        #             stat_data_time_min_hour = int(np.floor(df_selected_tracks["elapsed_seconds"].min() / 3600))
        #             stat_data_time_min_minute = int(np.floor((df_selected_tracks["elapsed_seconds"].min() % 3600) / 60))

        #             stat_data_time_max_hour = int(np.floor(df_selected_tracks["elapsed_seconds"].max() / 3600 - 24*(stat_num_days-1)))
        #             stat_data_time_max_minute = int(np.floor((df_selected_tracks["elapsed_seconds"].max() % 3600) / 60))

        #             st.write(f"Data time range: Day {1} at {stat_data_time_min_hour:02d}:{stat_data_time_min_minute:02d}  -  Day {stat_num_days} at {stat_data_time_max_hour:02d}:{stat_data_time_max_minute:02d}")

        #             stat_min_time = df_selected_tracks["elapsed_seconds"].min()
        #             stat_min_time_rounded = stat_min_time - (stat_min_time % (30*60))
        #             stat_max_time = df_selected_tracks["elapsed_seconds"].max()
        #             stat_max_time_rounded = stat_max_time - (stat_max_time % (30*60)) + 30*60

        #             stat_time_options = []
        #             for hour in range(stat_num_days*24 + 1):
        #                 for minute in [0, 15, 30, 45]:
        #                     if hour == stat_num_days*24 and minute > 0:
        #                         continue
        #                     stat_time_options.append(f"{hour:02d}:{minute:02d}")

        #             # Default to nearest 30-minute intervals
        #             stat_time_slider_default_start_idx = int(2*np.floor(stat_min_time_rounded / (30*60)))
        #             stat_time_slider_default_end_idx = int(2*np.ceil(stat_max_time_rounded / (30*60)))
        #             st.write(len(stat_time_options))
        #             st.write(stat_time_slider_default_end_idx)


        #             # Create a range slider using the select_slider
        #             stat_time_slider_selected_range = st.select_slider(
        #                 "Time range",
        #                 options=stat_time_options,
        #                 value=(stat_time_options[stat_time_slider_default_start_idx], stat_time_options[stat_time_slider_default_end_idx]),
        #                 key="stat_time_slider_range"
        #             )

        #             stat_start_time_selected, stat_end_time_selected = stat_time_slider_selected_range

        #             stat_start_hour, stat_start_minute = map(int, stat_start_time_selected.split(":"))
        #             stat_end_hour, stat_end_minute = map(int, stat_end_time_selected.split(":"))

        #             stat_start_seconds = 3600 * stat_start_hour + 60 * stat_start_minute
        #             stat_end_seconds = 3600 * stat_end_hour + 60 * stat_end_minute

        #             st.write(stat_start_seconds, stat_end_seconds)
        #         else:
        #             st.write("No data available for custom time range selection. Upload GPX files and select one or more tracks.")
                    
        # col1, col2, col3 = st.columns([1, 4, 1])
        # with col2:
        #     stat_title = st.text_input("Title", "", key="stat_title")
        
        #     # Create a dictionary of all static map parameters
        #     stat_params = {
        #         "selected_tracks": selected_tracks,
        #         "vis_mode": vis_mode,
        #         "map_style": stat_map_style,
        #         "fig_width": stat_fig_width,
        #         "lat_min": stat_lat_min,
        #         "lat_max": stat_lat_max,
        #         "lon_min": stat_lon_min,
        #         "lon_max": stat_lon_max,
        #         "show_start_end_points": stat_show_start_end_points,
        #         "show_legend": stat_show_legend,            
        #         "show_coordinates": stat_show_coordinates,
        #         "line_width": stat_line_width,
        #         "marker_size": stat_marker_size,
        #         "custom_title": stat_title,
        #         "start_seconds": stat_start_seconds,
        #         "end_seconds": stat_end_seconds,
        #     }
            
        #     # Generate a hash of these parameters
        #     stat_params_str = json.dumps(stat_params, sort_keys=True)
        #     stat_current_hash = hashlib.md5(stat_params_str.encode()).hexdigest()
            
        #     # Check if parameters have changed since last generation
        #     stat_params_changed = stat_current_hash != st.session_state.stat_params_hash
            
        #     # Display a note if parameters have changed since last generation
        #     if stat_params_changed and st.session_state.stat_map_generated:
        #         st.info("Map parameters have changed. Click Generate Static Map to update the visualization.")

        #     stat_generate_clicked = st.button("Generate Static Map", disabled=not(uploaded_files and df_selected_tracks is not None and not df_selected_tracks.empty))
            
        #     # Always show the map if it was previously generated
        #     if stat_generate_clicked or st.session_state.stat_map_generated:
        #         # Regenerate the map only if button was clicked or it is the first time
        #         if stat_generate_clicked or st.session_state.stat_map_fig is None:
        #             with st.spinner("Generating map..."):
        #                 fig = generate_map(
        #                     df_selected_tracks,
        #                     mode=vis_mode,
        #                     map_style=stat_map_style,
        #                     fig_width=int(stat_fig_width),
        #                     lat_min=stat_lat_min,
        #                     lat_max=stat_lat_max,
        #                     lon_min=stat_lon_min,
        #                     lon_max=stat_lon_max,                            
        #                     show_start_end_points=stat_show_start_end_points,
        #                     show_legend=stat_show_legend,
        #                     show_coordinates=stat_show_coordinates,
        #                     line_width=stat_line_width,
        #                     start_end_marker_size=stat_marker_size,
        #                     title=stat_title,
        #                     start_time=stat_start_seconds,
        #                     end_time=stat_end_seconds
        #                 )
        #                 st.session_state.stat_map_fig = fig
        #                 st.session_state.stat_map_generated = True
        #                 # Update the hash
        #                 st.session_state.stat_params_hash = stat_current_hash
        #                 # Record the current parameters so we know we are showing the latest
        #                 st.session_state.current_stat_params = stat_params
                
        #         # Display the map outside the regeneration condition
        #         # This ensures it's always shown if it exists
        #         if st.session_state.stat_map_fig:
        #             # col1, col2, col3 = st.columns([1, 4, 1])
        #             # with col2:
        #             st.pyplot(st.session_state.stat_map_fig)

        # st.divider()