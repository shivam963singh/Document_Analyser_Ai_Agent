import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from google import genai
from document_parser import extract_text

# Set page config
st.set_page_config(page_title="Document Analysis Agent", page_icon="📄", layout="wide")

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Custom CSS for a better UI
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Header styling */
    h1 {
        color: #1E3A8A;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        margin-bottom: 0rem;
    }
    
    .subtitle {
        color: #64748B;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        color: #1E3A8A;
        font-weight: 600;
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: white;
        border-right: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 Document Analysis Agent")
st.markdown('<p class="subtitle">Upload a document and interact with it using Gemini 2.5 Flash.</p>', unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "document_summary" not in st.session_state:
    st.session_state.document_summary = None
if "document_text" not in st.session_state:
    st.session_state.document_text = None

# Sidebar Setup
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg", width=50)
    st.header("Agent Configuration")
    
    # API Key input
    user_api_key = st.text_input("Gemini API Key", value=api_key if api_key else "", type="password", help="Enter your Gemini API Key. It will be loaded from .env if available.")
    
    if user_api_key:
        try:
            client = genai.Client(api_key=user_api_key)
        except Exception as e:
            st.error(f"API Configuration Error: {e}")
            client = None
    else:
        st.warning("⚠️ Please provide a Gemini API Key to continue.")
        client = None

    st.divider()
    st.header("Document Upload")
    
    uploaded_file = st.file_uploader("Select a Document", type=["pdf", "docx", "xlsx", "xls", "ipynb", "txt", "md", "csv", "py", "json"])
    
    if uploaded_file is not None and client is not None:
        if st.button("🚀 Process Document"):
            with st.spinner("Extracting text and generating summary..."):
                # Save uploaded file to a temporary file
                ext = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                try:
                    # Extract text using the existing document parser
                    document_text = extract_text(tmp_file_path)
                    st.session_state.document_text = document_text
                    
                    if not document_text.strip():
                        st.error("The document appears to be empty or text could not be extracted.")
                    else:
                        # Generate Summary
                        model_id = "gemini-2.5-flash"
                        summary_prompt = f"""
                        You are an expert Document Analysis Agent. 
                        Below is the text extracted from a document. Please provide a comprehensive, well-structured summary of the document.

                        Document Text:
                        {document_text}
                        """
                        
                        response = client.models.generate_content(
                            model=model_id,
                            contents=summary_prompt
                        )
                        st.session_state.document_summary = response.text
                        
                        # Initialize Chat Session
                        st.session_state.chat_session = client.chats.create(
                            model=model_id,
                            history=[
                                {
                                    "role": "user",
                                    "parts": [{"text": f"Here is a document for context. I will ask you questions about it.\n\nDocument Text:\n{document_text}"}]
                                },
                                {
                                    "role": "model",
                                    "parts": [{"text": "I have received the document and generated the summary. I am ready to answer any questions you have."}]
                                }
                            ]
                        )
                        
                        st.session_state.messages = [
                            {"role": "assistant", "content": "Hi! I've read the document and generated a summary. How can I help you explore it further?"}
                        ]
                        
                        st.success("Document processed! Ready for Q&A. 🎉")
                        
                except Exception as e:
                    st.error(f"Error processing document: {e}")
                finally:
                    # Clean up
                    if os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)
                        
    st.divider()
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        if st.session_state.document_text and client:
            # Re-initialize chat
            st.session_state.chat_session = client.chats.create(
                model="gemini-2.5-flash",
                history=[
                    {
                        "role": "user",
                        "parts": [{"text": f"Here is a document for context. I will ask you questions about it.\n\nDocument Text:\n{st.session_state.document_text}"}]
                    },
                    {
                        "role": "model",
                        "parts": [{"text": "I have received the document and generated the summary. I am ready to answer any questions you have."}]
                    }
                ]
            )
            st.session_state.messages = [
                {"role": "assistant", "content": "Conversation cleared. What else would you like to ask?"}
            ]
            st.rerun()

# Main Workspace
if st.session_state.document_summary:
    with st.expander("📑 View Document Summary", expanded=False):
        st.markdown(st.session_state.document_summary)

# Display Messages
if not st.session_state.messages and not st.session_state.chat_session:
    # Empty state
    st.info("👈 Upload a document in the sidebar to get started!")
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about the document..."):
    if not st.session_state.chat_session:
        st.warning("Please upload and process a document first.")
    else:
        # Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Generate & show assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat_session.send_message(prompt)
                    message_placeholder.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error communicating with Gemini: {e}")
