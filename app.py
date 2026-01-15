import streamlit as st


import utils as u

# --- PAGE CONFIG ---
st.set_page_config(page_title="Manas Mind Palace", layout="wide")
st.markdown("<div id='top'></div>", unsafe_allow_html=True)
BRAIN_DIR = "palace"

# --- SIDEBAR ---
st.sidebar.markdown("[🏠 Back to Top](#top)")
st.sidebar.title("🧠 Palace Rooms")

# --- SESSION STATE ---

# We use this to keep track of which file is currently open
if "current_file" not in st.session_state:
    st.session_state.current_file = None

if "directory_dict" not in st.session_state:
    st.session_state.directory_dict = u.dict_of_all_files(BRAIN_DIR)

u.display_directory_contents(BRAIN_DIR)

# --- MAIN CONTENT ---
u.search_box()
u.keyword_search()

if st.session_state.current_file:
    u.render_markdown_file()
else:
    st.title("Welcome to Manas Mind Palace")
    st.info("Select a Room")
