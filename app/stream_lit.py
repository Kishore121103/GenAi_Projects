import streamlit as st
from app_utils import initialize_session_state
from chat_interface import display_chat
from side_bar import configure_sidebar
from development import RecipeAssistant

# Initialize the Recipe Assistant
assistant = RecipeAssistant()

# Set up session state variables
initialize_session_state("chat_history", [])

# Configure the sidebar
configure_sidebar()

# Main app interface
st.title("AI Recipe Assistant")
st.markdown("Welcome! Type in your query below and let the AI agents assist you.")

# Display chat interface and get user input
user_input = display_chat()

# If the user submits input, process it and update chat history
if user_input:
    # Process the user input through the Recipe Assistant
    response = assistant.process_user_input(user_input)

    # Update the chat history in session state
    st.session_state["chat_history"].append(("user", user_input))
    st.session_state["chat_history"].append(("assistant", response))

    # Refresh the page to display the updated chat history
    st.experimental_rerun()
