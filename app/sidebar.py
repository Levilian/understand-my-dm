import streamlit as st

def set_api_key(api_key: str):
    st.session_state["OPENAI_API_KEY"] = api_key

def sidebar():
    with st.sidebar:
        st.markdown(
            "## Setup\n"
            "1. Enter your [OpenAI API key](https://beta.openai.com/docs/developer-quickstart/your-api-keys) to get started.\n"
            "2. Upload your chat history as .json files.\n"
            "3. Ask questions about your chat history!\n"
        )
        
        api_key = st.text_input("OpenAI API key",
                    type="password",
                    placeholder="Enter your OpenAI API key",
                    help="Get your openAI API key at https://beta.openai.com/docs/developer-quickstart/your-api-keys",
                    value=st.session_state.get("OPENAI_API_KEY", ""),
                )
        
        if api_key:
            set_api_key(api_key)