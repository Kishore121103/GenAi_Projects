import streamlit as st
import requests
import os
from development import process_user_input  # Replace with your actual agent logic

# Constants
BASE_URL = "http://localhost:5105"
CREATE_SESSION_API = f"{BASE_URL}/api/Message/create-session"
GET_SESSIONS_API = f"{BASE_URL}/api/Message/get-sessions"
GET_MESSAGES_API = f"{BASE_URL}/api/Message/get-responses"
ADD_MESSAGE_API = f"{BASE_URL}/api/Message/add-response"
ADD_ITEMS_API = f"{BASE_URL}/api/Message/add-items"

# Set up the Streamlit app
st.set_page_config(
    page_title="Recipe Generator",
    page_icon="🍳",
    layout="wide"
)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_list" not in st.session_state:
    st.session_state.session_list = []

# Create a new session on the backend
def create_session():
    try:
        response = requests.post(CREATE_SESSION_API)
        if response.status_code == 201:
            session_data = response.json()
            st.session_state.session_id = session_data["sessionId"]
            st.success("New chat session created!")
        else:
            st.error(f"Error creating session: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred while creating a session: {e}")

# Fetch sessions from backend
def fetch_sessions():
    try:
        response = requests.get(GET_SESSIONS_API)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching sessions: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"An error occurred while fetching sessions: {e}")
        return []

# Fetch messages by session ID
def fetch_messages(session_id):
    try:
        api_url = f"{GET_MESSAGES_API}/{session_id}"  # Pass session ID in URL
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching messages: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"An error occurred while fetching messages: {e}")
        return []

# Post a new message to the backend
def add_message(session_id, role, message):
    try:
        payload = {
                "sessionId": session_id,
                "role": role,
                "content": message  # Ensure 'content' is lowercase
            }

        response = requests.post(ADD_MESSAGE_API, json=payload)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Error adding message: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while adding the message: {e}")
        return None

# Add items to the backend
def add_items(session_id, items):
    try:
        payload = {
            "sessionId": session_id,
            "items": items
        }
        response = requests.post(ADD_ITEMS_API, json=payload)
        if response.status_code == 200:
            st.success("Items successfully added to the backend.")
        else:
            st.error(f"Error adding items: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred while adding items: {e}")

# Sidebar for session management and item addition
with st.sidebar:
    st.title("Grocery Management")

    # Create a new session
    if st.button("New Chat"):
        create_session()
        st.session_state.chat_history = []

    # Load existing sessions
    if st.button("Load Sessions"):
        st.session_state.session_list = fetch_sessions()

    # Display list of sessions
    if st.session_state.session_list:
        session_options = {
            f"{s['sessionId']} - {s.get('createdAt', 'Unknown')}": s["sessionId"]
            for s in st.session_state.session_list
        }

        selected_session = st.radio("Select a Session", options=session_options.keys())

        if selected_session:
            st.session_state.session_id = session_options[selected_session]
            st.session_state.chat_history = fetch_messages(st.session_state.session_id)

    # Image upload for scanning items
    with st.expander("Scan Grocery Receipt"):
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png", "pdf"], label_visibility="collapsed")
        if uploaded_file:
            # Save the uploaded file
            upload_dir = r"C:\Users\saunt\Documents\recipe generator\GenAi_Projects\Uploaded images"
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            temp_file_path = os.path.join(upload_dir, uploaded_file.name)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.read())

            # Process the uploaded file
            with st.spinner("Processing document..."):
                response = process_user_input(None, st.session_state.chat_history, uploaded_file_path=temp_file_path)

                if response and response.get("data"):
                    extracted_items = response["data"]
                    st.success("Document processed successfully!")
                    st.json(extracted_items)

                    if st.session_state.session_id:
                        add_items(st.session_state.session_id, extracted_items)
                    else:
                        st.error("No active session. Please start a new chat to save extracted data.")
                else:
                    st.error("Failed to process the uploaded document.")

    # Manual input for adding grocery items
    with st.expander("Add Items Manually"):
        st.write("Enter grocery items manually:")
        item_name = st.text_input("Item Name")
        quantity = st.text_input("Quantity")
        purchase_date = st.date_input("Purchase Date")  # Use a date picker for valid dates

        if st.button("Add Item"):
            if not item_name or not quantity or not purchase_date:
                st.error("Please fill in all fields before submitting.")
            else:
                # Format date as ISO-8601 string
                formatted_date = purchase_date.strftime("%Y-%m-%d")

                manual_items = [{
                    "itemName": item_name,
                    "quantity": quantity,  # Ensure quantity is an integer
                    "purchaseDate": formatted_date,
                }]
                if st.session_state.session_id:
                    with st.spinner("Adding item to the backend..."):
                        try:
                            add_items(st.session_state.session_id, manual_items)
                            st.success(f"Item '{item_name}' successfully added.")
                        except Exception as e:
                            st.error(f"Failed to add item '{item_name}': {e}")
                else:
                    st.error("No active session. Please start a new chat to save items.")

# Main chat UI
st.title("Recipe Generator 🍳")

# Display chat history
if st.session_state.chat_history:
    for chat in st.session_state.chat_history:
        role = chat["role"]
        content = chat["content"]
        st.chat_message(role).markdown(content)

# Input text box
user_input = st.chat_input("Ask a question or describe your recipe requirements...")

# Handle user input
if user_input:
    if not st.session_state.session_id:
        st.error("No active session. Please start a new chat.")
    else:
        st.chat_message("user").markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Processing..."):
            assistant_response = process_user_input(user_input, st.session_state.chat_history)

        if assistant_response:
            st.chat_message("assistant").markdown(assistant_response)
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
            add_message(st.session_state.session_id, "user", user_input)
            add_message(st.session_state.session_id, "assistant", assistant_response)
        else:
            st.error("Failed to fetch a valid response from the assistant.")

