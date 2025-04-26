import streamlit as st
import os

def initialize_session_state():
    """Initialize all session state variables"""
    state_vars = {
        "df_combined": None,
        "selected_tracks": None,
        "df_selected_tracks": None,
        "stat_map_generated": False,
        "stat_map_fig": None,
        "animation_generated": False,
        "animation_file": None,        
        "animation_bytes": None,
        "stat_params_hash": "",
        "anim_params_hash": "",
        "stat_current_params": {},
        "anim_current_params": {}
    }
    
    for var, default in state_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default

def on_files_uploaded():
    """Callback function executed when new files are uploaded."""
    # Store current animation file path before resetting
    animation_file_path = st.session_state.get("animation_file")
    
    # Reset visualization flags
    st.session_state.stat_map_generated = False
    st.session_state.animation_generated = False
    st.session_state.stat_map_fig = None
    st.session_state.animation_bytes = None
    st.session_state.df_combined = None
    
    # Reset parameter tracking
    st.session_state.stat_params_hash = ""
    st.session_state.anim_params_hash = ""
    st.session_state.stat_current_params = {}
    st.session_state.anim_current_params = {}
    
    # Clean up temporary animation file if it exists
    if animation_file_path is not None:
        try:
            if os.path.exists(animation_file_path):
                os.unlink(animation_file_path)
                st.session_state.animation_file = None
        except OSError as e:
            st.warning(f"Could not delete temporary file: {e}")
    
    # Reset checkbox states to ensure track selection is refreshed
    if "checkbox_states" in st.session_state:
        del st.session_state.checkbox_states