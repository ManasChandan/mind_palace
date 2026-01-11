import streamlit as st
import os
import re


def dict_of_all_files(root_path):
    path_dict = {}

    for root, _, files in os.walk(root_path):
        for name in files:
            full_file_path = os.path.join(root, name)
            path_dict[name.replace(".md", "")] = full_file_path

    return path_dict


def select_file(path):
    # Set the file to be displayed
    st.session_state.current_file = path
    # CLEAR the search input value in session state
    st.session_state.global_search = ""


def search_box():
    search_query = st.text_input(
        "🔍 Search Palace Rooms",
        placeholder="Type filename or path...",
        key="global_search",
    )

    if search_query:
        # Filter the dictionary based on value (file path) or key
        # Adjust 'v' or 'k' depending on how your dict_of_all_files is structured
        matches = {
            k: v
            for k, v in st.session_state.directory_dict.items()
            if search_query.lower() in v.lower()
        }

        if matches:
            with st.container():
                st.caption("Search Results:")
                for key, path in matches.items():
                    # Display filename and part of the path for context
                    file_label = f"📄 {os.path.basename(path)} - ({path})"
                    st.button(
                        file_label,
                        key=f"search_btn_{path}",
                        on_click=select_file,
                        args=(path,),
                        use_container_width=True,
                    )
            st.divider()


def render_markdown_file():
    """Reads a .md file and renders it in the Streamlit main page."""
    try:
        file_path = st.session_state.current_file

        # Check if file exists and is a markdown file
        if os.path.exists(file_path) and file_path.endswith(".md"):
            with open(file_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            st.caption(f"Location: {file_path.replace(os.sep, r' > ')}")

            st.title(os.path.basename(file_path).replace(".md", ""))

            st.divider()

            # Render the content
            st.markdown(md_content)

        else:
            st.error(f"File not found or not a markdown file: {file_path}")

    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")


def display_directory_contents(path):
    """Helper function for recursive display."""

    for root, dir, files in os.walk(path):
        if os.path.basename(root) != path:
            folder_name = re.split(path, root)[-1].lstrip(os.sep)
            st.sidebar.markdown(f"📂 {folder_name.replace(os.sep, r' > ')}")

        for name in files:
            full_path = os.path.join(root, name)

            if st.sidebar.button(
                f"📄 {name.replace('.md', '')}", use_container_width=True
            ):
                st.session_state.current_file = full_path


@st.cache_data
def search_inside_files(directory_dict, query):
    """Searches for a keyword inside the text of all files."""
    matches = []
    query = query.lower()

    for key, path in directory_dict.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().lower()
                if query in content:
                    # Find a small snippet of the text to show in results
                    idx = content.find(query)
                    start = max(0, idx - 30)
                    end = min(len(content), idx + 50)
                    snippet = f"...{content[start:end]}..."
                    matches.append({"path": path, "snippet": snippet})
        except Exception as e:
            print(e)
            continue  # Skip files that can't be read (binary, etc.)
    return matches

def select_file_from_keyword(path):
    st.session_state.current_file = path
    st.session_state.keyword_query = ""  # Clear the input


def keyword_search():
    kw_query = st.text_input(
        "🔍 Search Words in Rooms",
        placeholder="Type a word...",
        key="keyword_query",
    )

    if kw_query:
        results = search_inside_files(st.session_state.directory_dict, kw_query)

        if results:
            st.caption(f"Found {len(results)} matches:")
            for res in results:
                # Create a button for each match
                with st.container(border=True):
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.markdown(f"**{os.path.basename(res['path'])}**")
                        st.caption(res["snippet"])
                    with col2:
                        st.button(
                            "Open",
                            key=f"kw_{res['path']}",
                            on_click=select_file_from_keyword,
                            args=(res["path"],),
                        )
        else:
            st.warning("No files contain that keyword.")
