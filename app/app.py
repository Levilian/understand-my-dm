import os
import pathlib
import json
import streamlit as st
from sidebar import sidebar
from index import construct_index, ask_question
from unicode_converter import unicode_converter

st.set_page_config(page_title='ChatHistoryGPT: Understand your DM', layout='wide')

parent_path = pathlib.Path(__file__).parent.parent.resolve()

os.environ['OPENAI_API_KEY'] = st.secrets.api_credentials['OPENAI_API_KEY']

# add sidebar
sidebar()

# @st.cache_data
def save_uploaded_file(chat_data, save_path: str):
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding='utf-8') as f:
        # Read the contents of the file as a binary, and parse it as a json object through unicode_converter
        decoded_data = unicode_converter(json.loads(chat_data.read()))
        # save ascii and unicode characters as is instead of \u escape sequences
        json.dump(decoded_data, f, ensure_ascii=False, indent=4)
        st.write(decoded_data)


def upload_data():
        uploaded_files = st.file_uploader(
            "Upload your chat history as .json files", type=['json'], accept_multiple_files=True
        )
        st.markdown(
            "Hint: you can [download your Facebook/Instagram chat history as .json files]"
            "(https://www.facebook.com/help/1701730696756992)."
        )
        submitted = st.form_submit_button("Submit")
        if submitted and uploaded_files:
            # Convert .json to Document file that can be used by langchain
            with st.spinner("Learning from your chat history..."):
                for uploaded_file in uploaded_files:
                    # Save uploaded file
                    save_path = parent_path / 'data' / uploaded_file.name

                    save_uploaded_file(uploaded_file, save_path)

                    construct_index(save_path, st.secrets.api_credentials['OPENAI_API_KEY'])
    

st.title("Ask my chat history!")
tab_settings, tab_qna = st.tabs(["Setup", "Q&A"])

# Define settings
show_event_sample = False
show_source_events = True
with tab_settings:
    # Collect user info (to be used to prompt later)
    prompt_context = {
        "name": st.text_input("What's your name?"),
    }

    # Upload chat history
    with st.form("my-form", clear_on_submit=True):
        upload_data()

data_path = parent_path / 'data'
uploaded_files = [f for f in os.listdir(data_path, ) if f.endswith('.json') and os.path.isfile(data_path / f)]
option = st.sidebar.selectbox('Pick a conversation to ask questions', uploaded_files)

# Show the user what we've collected

# talk to the model

with tab_qna:
    # if index is None:
    #     st.error("No index loaded! Please upload your calendar events first.")
    #     st.stop()

     # User asks a question
    submitted = False
    with st.form("query-form"):
        query = st.text_input( 
            label="Ask about your conversation with !",
            placeholder="When did I last go to Japan?",
        )
        submitted = st.form_submit_button("Submit")

    # Show response
    if submitted:
        with st.spinner("I'm thinking..."):
            response_text = ask_question(query, prompt_context)
            st.markdown(response_text)

# Select a file to talk to
# parent_path = pathlib.Path(__file__).parent.parent.resolve()
# data_path = os.path.join(parent_path, "data")
# onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]
# option = st.sidebar.selectbox('Pick a dataset', onlyfiles)
# file_location=os.path.join(data_path, option)
