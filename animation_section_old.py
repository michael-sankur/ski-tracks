# st.header("Generate an Animation")
        # st.write("Create an animated visualization of the GPX tracks over time. You can customize the animation settings such as duration, FPS, and map style.")
        
        # # anim_title = st.text_input("Animation title", "", key="anim_title")
        # anim_col_01, anim_col_02, anim_col_03 = st.columns(3)
        
        # with anim_col_01:
        #     st.subheader("Map Settings")
        #     anim_fig_width = st.number_input("Animation width (inches):", min_value=6.0, max_value=18.0, value=12.0, step=0.5, format="%.1f", key="anim_fig_width")
        #     anim_map_style = st.selectbox("Map Style", list(PROVIDERS.keys()), index=12, key="anim_map_style")
        #     anim_lat_padding = st.number_input("Latitude Padding", min_value=0.0, max_value=1.0, value=0.125, step=0.005, format="%.3f",key="anim_lat_padding")
        #     anim_lon_padding = st.number_input("Longitude Padding", min_value=0.0, max_value=1.0, value=0.125, step=0.005, format="%.3f", key="anim_lon_padding")

        #     # Custom map bounds
        #     anim_lat_min = 0
        #     anim_lat_max = 0
        #     anim_lon_min = 0
        #     anim_lon_max = 0
        #     with st.expander("Custom Latitude and Longitude Bounds", expanded=False):
                
        #         if uploaded_files and df_selected_tracks is not None and not df_selected_tracks.empty:

        #             anim_track_lat_delta = df_selected_tracks["latitude"].max() - df_selected_tracks["latitude"].min()
        #             anim_track_lon_delta = df_selected_tracks["longitude"].max() - df_selected_tracks["longitude"].min()

        #             anim_lat_min_default = df_selected_tracks["latitude"].min() - anim_lat_padding*anim_track_lat_delta
        #             anim_lat_max_default = df_selected_tracks["latitude"].max() + anim_lat_padding*anim_track_lat_delta
        #             anim_lon_min_default = df_selected_tracks["longitude"].min() - anim_lon_padding*anim_track_lon_delta
        #             anim_lon_max_default = df_selected_tracks["longitude"].max() + anim_lon_padding*anim_track_lon_delta

        #             anim_custom_bounds_mode = st.radio(
        #                 label="Select custom bounds mode:",
        #                 options=["Use standard lat/lon padding", "Use custom NSEW padding", "Use custom latitude and longitude"],
        #                 index=0,
        #                 key="anim_custom_bounds_mode",
        #                 horizontal=True
        #             )
        #             if anim_custom_bounds_mode == "Use standard lat/lon padding":
        #                 anim_lat_min = anim_lat_min_default
        #                 anim_lat_max = anim_lat_max_default
        #                 anim_lon_min = anim_lon_min_default
        #                 anim_lon_max = anim_lon_max_default

        #                 st.write(f"Map latitude extents: {anim_lat_min:.4f} to {anim_lat_max:.4f}")
        #                 st.write(f"Map longitude extents: {anim_lon_min:.4f} to {anim_lon_max:.4f}")

        #             elif anim_custom_bounds_mode == "Use custom NSEW padding":
        #                 anim_north_padding = st.number_input("North Padding", min_value=0.0, max_value=1.0, value=anim_lat_padding, step=0.005, format="%.3f", key="anim_north_padding")
        #                 anim_south_padding = st.number_input("South Padding", min_value=0.0, max_value=1.0, value=anim_lat_padding, step=0.005, format="%.3f", key="anim_south_padding")
        #                 anim_east_padding = st.number_input("East Padding", min_value=0.0, max_value=1.0, value=anim_lon_padding, step=0.005, format="%.3f", key="anim_east_padding")
        #                 anim_west_padding = st.number_input("West Padding", min_value=0.0, max_value=1.0, value=anim_lon_padding, step=0.005, format="%.3f", key="anim_west_padding")

        #                 anim_lat_min = df_selected_tracks["latitude"].min() - anim_south_padding*anim_track_lat_delta
        #                 anim_lat_max = df_selected_tracks["latitude"].max() + anim_north_padding*anim_track_lat_delta
        #                 anim_lon_min = df_selected_tracks["longitude"].min() - anim_west_padding*anim_track_lon_delta
        #                 anim_lon_max = df_selected_tracks["longitude"].max() + anim_east_padding*anim_track_lon_delta

        #                 st.write(f"Map latitude extents: {anim_lat_min:.4f} to {anim_lat_max:.4f}")
        #                 st.write(f"Map longitude extents: {anim_lon_min:.4f} to {anim_lon_max:.4f}")
        #             elif anim_custom_bounds_mode == "Use custom latitude and longitude":                        
        #                 anim_lat_min = st.number_input("Min Latitude", value=anim_lat_min_default, format="%.4f", step=0.005, key="anim_lat_min")
        #                 anim_lat_max = st.number_input("Max Latitude", value=anim_lat_max_default, format="%.4f", step=0.005, key="anim_lat_max")
        #                 anim_lon_min = st.number_input("Min Longitude", value=anim_lon_min_default, format="%.4f", step=0.005, key="anim_lon_min")                        
        #                 anim_lon_max = st.number_input("Max Longitude", value=anim_lon_max_default, format="%.4f", step=0.005, key="anim_lon_max")
        #         else:
        #             st.write("No data available for custom bounds selection. Upload GPX files and select one or more tracks.")

        # with anim_col_02:
        #     st.subheader("Data Settings")

        #     anim_show_time = st.checkbox("Show time", value=True, key="anim_show_time")
        #     anim_show_legend = st.checkbox("Show legend", value=False, key="anim_show_legend")            
        #     anim_show_start_end_points = st.checkbox("Show start and end points", value=False, key="anim_show_start_end")
        #     anim_show_coordinates = st.checkbox("Show coordinates", value=False, key="anim_show_coordinates")
        #     anim_line_width = st.slider("Line Width", min_value=1, max_value=6, value=3, step=1, key="anim_line_width")
        #     anim_marker_size = st.slider("Marker Size", min_value=2, max_value=12, value=6, step=1, key="anim_marker_size")

        #     anim_start_seconds = 0
        #     anim_end_seconds = 24 * 3600
        #     with st.expander("Custom Time Range", expanded=False):
                
        #         if uploaded_files and df_selected_tracks is not None and not df_selected_tracks.empty:

        #             anim_num_days = np.ceil(df_selected_tracks["elapsed_seconds"].max() / (24*3600))
        #             anim_num_days = int(max(anim_num_days, 1))

        #             anim_data_time_min_hour = int(np.floor(df_selected_tracks["elapsed_seconds"].min() / 3600))
        #             anim_data_time_min_minute = int(np.floor((df_selected_tracks["elapsed_seconds"].min() % 3600) / 60))

        #             anim_data_time_max_hour = int(np.floor(df_selected_tracks["elapsed_seconds"].max() / 3600 - 24*(anim_num_days-1)))
        #             anim_data_time_max_minute = int(np.floor((df_selected_tracks["elapsed_seconds"].max() % 3600) / 60))

        #             st.write(f"Data time range: Day {1} at {anim_data_time_min_hour:02d}:{anim_data_time_min_minute:02d}  -  Day {anim_num_days} at {anim_data_time_max_hour:02d}:{anim_data_time_max_minute:02d}")

        #             anim_min_time = df_selected_tracks["elapsed_seconds"].min()
        #             anim_min_time_rounded = anim_min_time - (anim_min_time % (30*60))
        #             anim_max_time = df_selected_tracks["elapsed_seconds"].max()
        #             anim_max_time_rounded = anim_max_time - (anim_max_time % (30*60)) + 30*60

        #             anim_time_options = []
        #             for hour in range(anim_num_days*24 + 1):
        #                 for minute in [0, 15, 30, 45]:
        #                     if hour == anim_num_days*24 and minute > 0:
        #                         continue
        #                     anim_time_options.append(f"{hour:02d}:{minute:02d}")

        #             # Default to nearest 30-minute intervals
        #             anim_time_slider_default_start_idx = int(2*np.floor(anim_min_time_rounded / (30*60)))
        #             anim_time_slider_default_end_idx = int(2*np.ceil(anim_max_time_rounded / (30*60)))
        #             st.write(len(anim_time_options))
        #             st.write(anim_time_slider_default_end_idx)


        #             # Create a range slider using the select_slider
        #             anim_time_slider_selected_range = st.select_slider(
        #                 "Time range",
        #                 options=anim_time_options,
        #                 value=(anim_time_options[anim_time_slider_default_start_idx], anim_time_options[anim_time_slider_default_end_idx]),
        #                 key="anim_time_slider_range"
        #             )

        #             anim_start_time_selected, anim_end_time_selected = anim_time_slider_selected_range

        #             anim_start_hour, anim_start_minute = map(int, anim_start_time_selected.split(":"))
        #             anim_end_hour, anim_end_minute = map(int, anim_end_time_selected.split(":"))

        #             anim_start_seconds = 3600 * anim_start_hour + 60 * anim_start_minute
        #             anim_end_seconds = 3600 * anim_end_hour + 60 * anim_end_minute

        #             st.write(anim_start_seconds, anim_end_seconds)
        #         else:
        #             st.write("No data available for custom time range selection. Upload GPX files and select one or more tracks.")
        
        # with anim_col_03:
        #     st.subheader("Animation Settings")

        #     anim_duration = st.slider("Animation length (seconds)", min_value=10, max_value=60, value=20, step=2, key="anim_duration")
        #     anim_fps = st.slider("Frames per second", min_value=10, max_value=48, value=24, step=2, key="anim_fps")            
        #     anim_trail_duration = 60*60*st.slider(
        #         "Trail duration (hours)",
        #         min_value=0,
        #         max_value=24,
        #         value=12,
        #         step=1,
        #         key="anim_trail_hours"
        #     )                    
        #     anim_dpi = st.slider("Resolution (DPI)", min_value=100, max_value=300, value=150, step=25, key="anim_dpi")
            
        # col1, col2, col3 = st.columns([1, 4, 1])
        # with col2:

        #     anim_title = st.text_input("Title", "", key="anim_title")
            
        #     # Create a dictionary of all animation parameters
        #     anim_params = {
        #         "map_style": anim_map_style,
        #         "fig_width": anim_fig_width,
        #         "lat_min": anim_lat_min,
        #         "lat_max": anim_lat_max,
        #         "lon_min": anim_lon_min,
        #         "lon_max": anim_lon_max,
        #         "show_time": anim_show_time,
        #         "show_legend": anim_show_legend,
        #         "show_start_end_points": anim_show_start_end_points,
        #         "show_coordinates": anim_show_coordinates,
        #         "marker_size": anim_marker_size,
        #         "line_width": anim_line_width,
        #         "start_time": anim_start_seconds,
        #         "end_time": anim_end_seconds,
        #         "length": anim_duration,
        #         "fps": anim_fps,
        #         "trail_duration": anim_trail_duration,
        #         "dpi": anim_dpi,
        #         "title": anim_title,
        #     }
            
        #     # Generate a hash of these parameters
        #     anim_params_str = json.dumps(anim_params, sort_keys=True)
        #     anim_current_hash = hashlib.md5(anim_params_str.encode()).hexdigest()
            
        #     # Check if parameters have changed since last generation
        #     anim_params_changed = anim_current_hash != st.session_state.anim_params_hash
            
        #     # Display a note if parameters have changed since last generation
        #     if anim_params_changed and st.session_state.animation_generated:
        #         st.info("Animation parameters have changed. Click Generate Animation to update the visualization.")

        #     # if uploaded_files and df_combined is not None and not df_combined.empty:
            
        #     # Generate animation button
        #     anim_gen_clicked = st.button("Generate Animation", disabled=not(uploaded_files and df_selected_tracks is not None and not df_selected_tracks.empty))
            
        #     # Display the animation if button clicked or if it was previously generated
        #     if anim_gen_clicked or st.session_state.animation_generated:
        #         # Regenerate only if button was explicitly clicked or if first time
        #         anim_needs_regeneration = (anim_gen_clicked or st.session_state.animation_bytes is None)
                
        #         # Generate the animation if needed
        #         if anim_needs_regeneration:
        #             with st.spinner("Generating animation... This may take a while depending on duration and quality settings."):
        #                 try:
        #                     animation_file = generate_animation(
        #                         df_selected_tracks,
        #                         mode=vis_mode,
        #                         map_style=anim_map_style,
        #                         fig_width=int(anim_fig_width),
        #                         lat_min=anim_lat_min,
        #                         lat_max=anim_lat_max,
        #                         lon_min=anim_lon_min,
        #                         lon_max=anim_lon_max,
                                
        #                         show_time=anim_show_time,
        #                         show_legend=anim_show_legend,
        #                         show_coordinates=anim_show_coordinates,
        #                         line_width=anim_line_width,
        #                         marker_size=anim_marker_size,
        #                         start_time=anim_start_seconds,
        #                         end_time=anim_end_seconds,

        #                         duration=anim_duration,
        #                         fps=anim_fps,
        #                         trail_duration=anim_trail_duration,
        #                         dpi=anim_dpi,


        #                         title=anim_title,
        #                     )
                            
        #                     # Store the animation file path and load the bytes
        #                     st.session_state.animation_file = animation_file
        #                     with open(animation_file, "rb") as video_file:
        #                         st.session_state.animation_bytes = video_file.read()
                            
        #                     st.session_state.animation_generated = True
        #                     # Update the hash and store current parameters
        #                     st.session_state.anim_params_hash = anim_current_hash
        #                     st.session_state.current_anim_params = anim_params
                            
        #                 except Exception as e:
        #                     st.error(f"Error generating animation: {e}")
        #                     st.session_state.animation_generated = False
        #                     st.session_state.animation_bytes = None
                
        #         # Display the animation if it was successfully generated
        #         if st.session_state.animation_generated and st.session_state.animation_bytes is not None:
        #             st.success("Animation generated successfully!")
                    
        #             # Display the video using the stored bytes
        #             st.video(st.session_state.animation_bytes, loop=True)
                    
        #             # Provide download link
        #             if anim_title == "":
        #                 download_label = "animation"
        #             else:
        #                 download_label = anim_title
                        
        #             if st.session_state.animation_file:
        #                 st.markdown(get_binary_file_downloader_html(st.session_state.animation_file, download_label), 
        #                             unsafe_allow_html=True)

        # st.divider()