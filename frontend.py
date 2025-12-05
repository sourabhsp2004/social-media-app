import streamlit as st
import requests
import base64
import urllib.parse
from datetime import datetime
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Simple Social", layout="wide", page_icon="🚀")

# --- Custom CSS for "Next Level" UI ---
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* Force dark theme colors */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }

    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    h1, h2, h3, p, div, span, label, .stMarkdown {
        color: #e0e0e0 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Cards */
    .post-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .post-card:hover {
        border: 1px solid rgba(75, 108, 183, 0.5);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.1);
        background-color: #1f2937;
        color: white !important;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        border-color: #4b6cb7;
        color: #4b6cb7 !important;
        background-color: #1f2937;
    }
    
    /* Primary Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
        border: none;
        color: white !important;
    }

    /* Inputs */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #1f2937;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white !important;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #4b6cb7;
        box-shadow: 0 0 0 1px #4b6cb7;
    }

    /* Comments Section */
    .comment-box {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 8px;
        padding: 12px;
        margin-top: 12px;
        border-left: 3px solid #4b6cb7;
    }
    
    .timestamp {
        color: #9ca3af !important;
        font-size: 0.85rem;
    }

</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None


def get_headers():
    """Get authorization headers with token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; margin-bottom: 40px;'>🚀 Simple Social</h1>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("### Welcome Back")
            email = st.text_input("Email", placeholder="name@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Log In", type="primary", use_container_width=True):
                    if email and password:
                        login_data = {"username": email, "password": password}
                        try:
                            response = requests.post(f"{API_URL}/auth/jwt/login", data=login_data)
                            if response.status_code == 200:
                                token_data = response.json()
                                st.session_state.token = token_data["access_token"]
                                
                                user_response = requests.get(f"{API_URL}/users/me", headers=get_headers())
                                if user_response.status_code == 200:
                                    st.session_state.user = user_response.json()
                                    st.rerun()
                            else:
                                st.error("Invalid credentials")
                        except Exception as e:
                            st.error(f"Connection error: {e}")
                    else:
                        st.warning("Please fill in all fields")

            with col_b:
                if st.button("Sign Up", use_container_width=True):
                    if email and password:
                        signup_data = {"email": email, "password": password}
                        try:
                            response = requests.post(f"{API_URL}/auth/register", json=signup_data)
                            if response.status_code == 201:
                                st.success("Account created! You can now log in.")
                            else:
                                st.error("Registration failed. Email might be taken.")
                        except Exception as e:
                            st.error(f"Connection error: {e}")
                    else:
                        st.warning("Please fill in all fields")


def upload_page():
    st.markdown("## 📸 Share Your Moment")
    
    with st.container(border=True):
        uploaded_file = st.file_uploader("Choose media", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'])
        caption = st.text_area("Caption", placeholder="Write something interesting...")
        
        if uploaded_file and st.button("Post", type="primary"):
            with st.spinner("Uploading to the cloud..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"caption": caption}
                try:
                    response = requests.post(f"{API_URL}/upload", files=files, data=data, headers=get_headers())
                    if response.status_code == 200:
                        st.balloons()
                        st.success("Posted successfully!")
                        st.rerun()
                    else:
                        st.error("Upload failed. Please try again.")
                except Exception as e:
                    st.error(f"Error: {e}")


def encode_text_for_overlay(text):
    if not text: return ""
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url, transformation_params, caption=None):
    if caption:
        encoded_caption = encode_text_for_overlay(caption)
        text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-50,co-white,bg-000000A0,l-end"
        transformation_params = f"{transformation_params},{text_overlay}" if transformation_params else text_overlay

    if not transformation_params:
        return original_url

    parts = original_url.split("/")
    # Basic ImageKit URL parsing - assumes standard format
    try:
        imagekit_id = parts[3]
        file_path = "/".join(parts[4:])
        base_url = "/".join(parts[:4])
        return f"{base_url}/tr:{transformation_params}/{file_path}"
    except:
        return original_url


def feed_page():
    st.markdown("## 🏠 Your Feed")

    try:
        # Simple optimization: Use st.spinner to show loading state
        # For real caching, we'd need to refactor to pass token as arg to a cached function
        
        response = requests.get(f"{API_URL}/feed", headers=get_headers())
        if response.status_code != 200:
            st.error("Failed to load feed")
            return
            
        posts = response.json()["posts"]
        
        if not posts:
            st.info("No posts yet. Be the first to share!")
            return

        for post in posts:
            # Post Card Container
            with st.container():
                st.markdown(f"""
                <div class="post-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-weight: 600; font-size: 1.1em;">{post['email']}</div>
                        <div class="timestamp">{post['created_at'][:10]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Media
                if post['file_type'] == 'image':
                    st.image(post['url'], use_container_width=True)
                else:
                    st.video(post['url'])
                
                # Caption
                if post['caption']:
                    st.markdown(f"<div style='margin-top: 10px; margin-bottom: 15px;'>{post['caption']}</div>", unsafe_allow_html=True)

                # Action Bar
                col1, col2, col3 = st.columns([1, 1, 4])
                
                with col1:
                    like_icon = "❤️" if post['is_liked'] else "🤍"
                    if st.button(f"{like_icon} {post['like_count']}", key=f"like_{post['id']}"):
                        requests.post(f"{API_URL}/posts/{post['id']}/like", headers=get_headers())
                        st.rerun()

                with col2:
                    if st.button(f"💬 {post['comment_count']}", key=f"comment_btn_{post['id']}"):
                        if st.session_state.get(f"show_comments_{post['id']}"):
                            st.session_state[f"show_comments_{post['id']}"] = False
                        else:
                            st.session_state[f"show_comments_{post['id']}"] = True
                        st.rerun()
                
                with col3:
                    if post['is_owner']:
                        if st.button("🗑️ Delete", key=f"del_{post['id']}", type="secondary"):
                            requests.delete(f"{API_URL}/posts/{post['id']}", headers=get_headers())
                            st.rerun()

                # Comments Section
                if st.session_state.get(f"show_comments_{post['id']}", False):
                    st.markdown("---")
                    
                    # Fetch comments
                    comments_res = requests.get(f"{API_URL}/posts/{post['id']}/comments", headers=get_headers())
                    if comments_res.status_code == 200:
                        comments = comments_res.json()["comments"]
                        for comment in comments:
                            st.markdown(f"""
                            <div class="comment-box">
                                <small style="color: #4b6cb7;">{comment['email']}</small><br>
                                {comment['content']}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Add new comment
                    with st.form(key=f"add_comment_{post['id']}"):
                        new_comment = st.text_input("Add a comment...", label_visibility="collapsed")
                        if st.form_submit_button("Post Comment"):
                            if new_comment:
                                requests.post(
                                    f"{API_URL}/posts/{post['id']}/comments",
                                    json={"content": new_comment},
                                    headers=get_headers()
                                )
                                st.rerun()
                
                st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading feed: {e}")


# Main app logic
if st.session_state.user is None:
    login_page()
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👋 Hi, {st.session_state.user['email'].split('@')[0]}")
        st.markdown("---")
        page = st.radio("Navigate", ["🏠 Feed", "📸 Upload"], label_visibility="collapsed")
        st.markdown("---")
        if st.button("Log Out", use_container_width=True):
            st.session_state.user = None
            st.session_state.token = None
            st.rerun()

    if page == "🏠 Feed":
        feed_page()
    else:
        upload_page()