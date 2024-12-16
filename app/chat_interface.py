import streamlit as st

def display_chat():
    """
    Display the user chat interface with a text input and a history log.
    """
    # Display conversation history
    st.markdown("### Conversation History")
    if "chat_history" in st.session_state and st.session_state["chat_history"]:
        for message in st.session_state["chat_history"]:
            role, content = message
            st.write(f"**{role.capitalize()}:** {content}")

    # User input box
    user_input = st.text_input("Enter your query:", "")
    return user_input
