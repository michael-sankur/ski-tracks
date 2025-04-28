import streamlit as st

def show_track_selection(df_combined):
    """
    Display track selection UI and return selected tracks
    
    Args:
        df_combined: DataFrame with combined GPX data
        
    Returns:
        selected_tracks: List of selected track names
        df_selected_tracks: DataFrame filtered to selected tracks
    """
    st.header("Select Tracks")
    
    if df_combined is None or df_combined.empty:
        st.write("No data available. Upload one or more GPX files.")
        return [], None
    
    all_tracks = sorted(df_combined["track_name"].unique().tolist())
    selected_tracks = show_checklist(all_tracks)
    
    # Filter dataframe to selected tracks
    df_selected_tracks = df_combined[df_combined["track_name"].isin(selected_tracks)].copy() if selected_tracks else None
    
    return selected_tracks, df_selected_tracks

def show_checklist(options_list):
    """Display a checklist of options and return selected items"""
    # Create a list to store the status of each checkbox (True = checked)
    if "checkbox_states" not in st.session_state:
        # Initialize all checkboxes as checked (True)
        st.session_state.checkbox_states = [True] * len(options_list)
    
    # Display checkboxes and update their states
    for k1, option in enumerate(options_list):
        st.session_state.checkbox_states[k1] = st.checkbox(
            option, 
            value=st.session_state.checkbox_states[k1],
            key=f"checkbox_{k1}"
        )
    
    # Return only the selected options
    selected_options = [opt for opt, state in zip(options_list, st.session_state.checkbox_states) if state]
    return selected_options