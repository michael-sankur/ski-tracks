if df_selected_tracks is not None and not df_selected_tracks.empty:
            anim_params = show_static_map_options(df_selected_tracks)
            
            # Check if parameters have changed
            anim_params_changed, anim_current_hash = check_params_changed(
                anim_params, "anim_params_hash"
            )
            
            # Show notice if params changed since last generation
            if anim_params_changed and st.session_state.anim_map_generated:
                st.info("Map parameters have changed. Click Generate Static Map to update the visualization.")
            
            # Generate the map
            generate_display_static_map(df_selected_tracks, anim_params, selected_tracks)
            
            # Update hash if map was generated
            if st.session_state.anim_map_generated:
                st.session_state.anim_params_hash = anim_current_hash
                st.session_state.current_anim_params = anim_params

        st.divider()