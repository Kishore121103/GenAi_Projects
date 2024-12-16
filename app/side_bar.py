import streamlit as st

def configure_sidebar():
    """
    Configures the Streamlit app sidebar.
    """
    st.sidebar.title("Recipe Assistant")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This is a recipe assistant app powered by AI agents. You can ask for recipes, "
        "ingredient details, dietary adjustments, and more!"
    )
