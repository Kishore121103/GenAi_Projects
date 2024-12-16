import streamlit as st

def initialize_session_state(key, default_value):
    """
    Initializes a session state variable with a default value if it does not exist.
    """
    if key not in st.session_state:
        st.session_state[key] = default_value
