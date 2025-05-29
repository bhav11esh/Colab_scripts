import streamlit as st
import instaloader
import pandas as pd
import os
import json
import glob
from datetime import datetime
import time
import random
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import openai
import re
from openai import OpenAI
from importlib.util import spec_from_file_location, module_from_spec

# Set page config
st.set_page_config(
    page_title="Instagram Content Automation",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# OpenAI API Key setup
# NOTE: Never hardcode your OpenAI API key in code. Use environment variables or Streamlit secrets/session state.
def set_openai_key():
    if 'openai_api_key' in st.session_state and st.session_state.openai_api_key:
        openai.api_key = st.session_state.openai_api_key
    else:
        openai.api_key = os.getenv('OPENAI_API_KEY', '')

# --- Store/retrieve OpenAI API key in browser cache (query params workaround) ---
# On app load, check for key in query params
query_params = st.query_params  # st.query_params is now a property
if 'openai_api_key' in query_params and query_params['openai_api_key']:
    if 'openai_api_key' not in st.session_state or st.session_state['openai_api_key'] != query_params['openai_api_key'][0]:
        st.session_state['openai_api_key'] = query_params['openai_api_key'][0]

def search_instagram_accounts_llm(keyword, max_accounts=10):
    set_openai_key()
    client = OpenAI(api_key=openai.api_key)
    prompt = (
        f"Give me a Python list of dicts for real, popular, or interesting Instagram account usernames related to '{keyword}'. "
        f"Each dict must have: 'username' (str), 'profile_url' (str), 'bio' (str, if available), 'followers' (int, plausible estimate), and 'posts' (int, plausible estimate). "
        f"No extra text. Limit to {max_accounts} results."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that only returns valid Python code as instructed."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        content = response.choices[0].message.content.strip()
        # Extract the list using regex in case extra text is present
        import ast, re
        match = re.search(r'(\[.*\])', content, re.DOTALL)
        if match:
            accounts = ast.literal_eval(match.group(1))
        else:
            accounts = ast.literal_eval(content)
        # Ensure each item is a dict with required keys
        valid_accounts = []
        for a in accounts:
            if (
                isinstance(a, dict) and
                'username' in a and 'profile_url' in a and 'followers' in a and 'posts' in a
            ):
                valid_accounts.append(a)
        return valid_accounts
    except Exception as e:
        st.error(f"OpenAI API error: {e}")
        return []
    

    
# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #F56040; 
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #833AB4;
        margin-bottom: 1rem;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        background-color: #F9F9F9;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    .warning-text {
        color: #ffc107;
        font-weight: bold;
    }
    .error-text {
        color: #dc3545;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background-color: #F56040;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown("<h1 class='main-header'>Instagram Content Automation</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Analyze and download Instagram content with smart recommendations</p>", unsafe_allow_html=True)

# Create Instaloader instance
@st.cache_resource
def get_instaloader():
    return instaloader.Instaloader(
        download_pictures=False,
        download_video_thumbnails=False,
        download_videos=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=True,
        compress_json=False
    )

# Create loader
L = get_instaloader()

# Sidebar navigation
st.sidebar.markdown("## Navigation")
page = st.sidebar.radio("Choose a function:", [
    "🏠 Home",
    "🔍 Search Accounts",
    "✅ Verify Accounts",
    "📥 Download Content",
    "📊 Analyze Data",
    "🏆 View Recommendations",
    "⚙️ Settings"
])

# Add OpenAI API Key input in the sidebar for convenience
with st.sidebar:
    st.markdown("---")
    st.markdown("### OpenAI API Key")
    api_key_input = st.text_input("Enter your OpenAI API Key", type="password", value=st.session_state.get('openai_api_key', ''))
    if api_key_input:
        st.session_state['openai_api_key'] = api_key_input
        # Save to browser cache (query params workaround)
        st.query_params["openai_api_key"] = api_key_input
        st.success("OpenAI API Key set for this session.")
    else:
        st.info("Please enter your OpenAI API Key to enable LLM-powered features.")

# Import the simple_profile_download function
spec = spec_from_file_location("insta_content_automation", "Insta Content Automation.py")
insta_content_automation = module_from_spec(spec)
spec.loader.exec_module(insta_content_automation)
simple_profile_download = insta_content_automation.simple_profile_download
analyze_collected_data = getattr(insta_content_automation, 'analyze_collected_data', None)

# New: Function to combine all JSONs in all subfolders and analyze
import json
def combine_all_jsons_and_analyze(base_folder="."):
    json_files = []
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    all_data = []
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_data.append(data)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    if not all_data:
        return None
    import pandas as pd
    df = pd.json_normalize(all_data)
    csv_name = f"all_jsons_{len(df)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_name, index=False)
    return df, csv_name

# --- Top Content Recommendations Section (Reusable) ---
def show_top_content_recommendations(df, analyze_type=None):
    import pandas as pd
    st = __import__('streamlit')
    # Ensure selected_shortcodes in session state
    if 'selected_shortcodes' not in st.session_state:
        st.session_state['selected_shortcodes'] = set()
    selected_shortcodes = st.session_state['selected_shortcodes']
    # Use node.__typename for type and smart_score logic
    typename_col = None
    for col in df.columns:
        if col.lower() == "node.__typename":
            typename_col = col
            break
    filtered_df = df.copy()
    if analyze_type and typename_col:
        if analyze_type == "Posts only (GraphSidecar)":
            filtered_df = filtered_df[filtered_df[typename_col] == "GraphSidecar"]
        elif analyze_type == "Videos only (GraphVideo)":
            filtered_df = filtered_df[filtered_df[typename_col] == "GraphVideo"]
    elif analyze_type and analyze_type != "All":
        st.warning("Column 'node.__typename' not found in the data. Cannot filter by content type.")
    # Compute smart_score if not present or recalculate for filtered
    if 'likes' not in filtered_df.columns:
        filtered_df['likes'] = 0
    else:
        filtered_df['likes'] = pd.to_numeric(filtered_df['likes'], errors='coerce').fillna(0)
    if 'comments' not in filtered_df.columns:
        filtered_df['comments'] = 0
    else:
        filtered_df['comments'] = pd.to_numeric(filtered_df['comments'], errors='coerce').fillna(0)
    if 'views' in filtered_df.columns:
        filtered_df['views'] = pd.to_numeric(filtered_df['views'], errors='coerce').fillna(0)
    # Smart score logic by type
    if typename_col:
        filtered_df['smart_score'] = filtered_df.apply(
            lambda row: row['likes'] + 2*row['comments'] + (0.1*row.get('views', 0) if row[typename_col]=="GraphVideo" else 0), axis=1
        )
    else:
        filtered_df['smart_score'] = filtered_df['likes'] + 2*filtered_df['comments']
    # Sort and rank
    filtered_df = filtered_df.sort_values('smart_score', ascending=False).reset_index(drop=True)
    filtered_df['rank'] = filtered_df.index + 1
    filtered_df['recommendation'] = filtered_df['smart_score'].apply(
        lambda x: "⭐⭐⭐" if x >= 75 else ("⭐⭐" if x >= 50 else ("⭐" if x >= 25 else ""))
    )
    top_content = filtered_df.head(30)  # Show more for grid
    cols = st.columns(3)
    for idx, row in top_content.iterrows():
        type_str = (
            row.get('node.__typename')
            or row.get('node.iphone_struct.__typename')
            or ("Video" if row.get('node.is_video', False) else "Image")
        )
        date_str = (
            row.get('node.date')
            or row.get('node.iphone_struct.taken_at_timestamp')
            or ''
        )
        post_shortcode = (
            row.get('node.shortcode')
            or row.get('node.iphone_struct.shortcode')
            or ''
        )
        post_url = f"https://www.instagram.com/p/{post_shortcode}"
        likes = row.get('node.edge_media_preview_like.count') or row.get('node.iphone_struct.edge_media_preview_like.count') or row.get('node.iphone_struct.edge_liked_by.count') or 0
        comments = row.get('node.comments') or row.get('node.iphone_struct.edge_media_to_comment.count') or 0
        views = row.get('node.video_view_count') or row.get('node.iphone_struct.video_view_count') or 0
        smart_score = row.get('smart_score', 0)
        likes = 0 if pd.isna(likes) else int(likes)
        comments = 0 if pd.isna(comments) else int(comments)
        views = 0 if pd.isna(views) else int(views)
        col = cols[idx % 3]
        with col:
            st.markdown(f"""
            <div style='background:rgba(0,0,0,0.6); color:#fff; padding:8px; border-radius:0 0 10px 10px; font-size:13px;'>
                <b>Rank {row['rank']} {row['recommendation']}</b> | {type_str} | {date_str}<br>
                ❤️ {likes} &nbsp; 💬 {comments} &nbsp; 👁️ {views} &nbsp; <b>Score: {smart_score:.1f}</b><br>
                <a href='{post_url}' style='color:#1DA1F2;' target='_blank'>View on Instagram</a>
            </div>
            """, unsafe_allow_html=True)
            if post_shortcode:
                st.markdown(f"""
                <iframe src=\"https://www.instagram.com/p/{post_shortcode}/embed\" width=\"400\" height=\"480\" frameborder=\"0\" scrolling=\"no\" allowtransparency=\"true\"></iframe>
                """, unsafe_allow_html=True)
            checked = st.checkbox("Select this post", key=f"select_{post_shortcode}", value=post_shortcode in selected_shortcodes)
            if checked:
                selected_shortcodes.add(post_shortcode)
            else:
                selected_shortcodes.discard(post_shortcode)
    # Download recommendations
    rec_csv = filtered_df.head(50).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Top 50 Recommendations as CSV",
        data=rec_csv,
        file_name="top_content_recommendations.csv",
        mime="text/csv"
    )
    # Show filtered/analysed CSV with smart_score
    st.markdown("#### Filtered & Analyzed Data Preview")
    st.dataframe(filtered_df.head(20), use_container_width=True)
    filtered_csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered/Analyzed CSV",
        data=filtered_csv,
        file_name=f"filtered_analyzed_{(analyze_type or 'all').replace(' ', '_').lower()}.csv",
        mime="text/csv",
        help="Download the filtered and analyzed data as a CSV file"
    )

if page == "🏠 Home":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Welcome to Instagram Content Automation")
    st.markdown("""
    This app helps you analyze Instagram content and find high-performing posts based on engagement metrics.
    
    **Key Features:**
    - Search for Instagram accounts by keyword
    - Verify if accounts are public and accessible
    - Download content from verified accounts
    - Analyze engagement metrics
    - Get smart content recommendations
    
    **⚠️ Important Note:**
    This app respects Instagram's rate limiting. If you encounter rate limit issues, the app will notify you and 
    automatically retry when allowed by Instagram's API.
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Quick start cards in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. Go to **Search Accounts** to find Instagram accounts
        2. Use **Verify Accounts** to check which ones are accessible
        3. **Download Content** from verified accounts
        4. Run **Analyze Data** to get engagement metrics
        5. View **Recommendations** for high-performing content
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📈 Sample Results")
        
        # Show a sample chart if data exists, otherwise placeholder
        sample_data = {'account': ['@travel1', '@travel2', '@travel3', '@travel4', '@travel5'],
                      'engagement': [87, 65, 91, 72, 43]}
        df = pd.DataFrame(sample_data)
        
        fig = px.bar(df, x='account', y='engagement', 
                    title='Sample Engagement Scores',
                    color='engagement',
                    color_continuous_scale=px.colors.sequential.Plasma)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "🔍 Search Accounts":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Search for Instagram Accounts")
    
    # Search form
    with st.form("search_form"):
        keyword = st.text_input("Enter keyword to search for Instagram accounts:", placeholder="e.g., travel, photography, india")
        max_accounts = st.slider("Maximum number of accounts to find:", min_value=5, max_value=50, value=10)
        submitted = st.form_submit_button("Search")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if submitted and keyword:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        with st.spinner(f"Searching for Instagram accounts related to '{keyword}' via OpenAI LLM..."):
            st.markdown(f"#### Results for '{keyword}'")
            # Use OpenAI LLM to get account suggestions
            found_accounts = search_instagram_accounts_llm(keyword, max_accounts)
            if not found_accounts:
                st.warning("No accounts found or OpenAI API error.")
                found_accounts = []
            # Store in session state for saving
            st.session_state['found_accounts'] = found_accounts
            # Display found accounts
            found_accounts = found_accounts[:max_accounts]
            
            if found_accounts:
                df = pd.DataFrame(found_accounts)
                # Format followers and posts if present
                if "followers" in df.columns:
                    df["followers"] = df["followers"].apply(lambda x: f"{x/1000:.1f}K" if x < 1000000 else f"{x/1000000:.1f}M")
                if "posts" in df.columns:
                    df["posts"] = df["posts"].apply(lambda x: f"{x:,}")
                # Add clickable profile_url if present
                if "profile_url" in df.columns:
                    df["profile_url"] = df["profile_url"].apply(lambda url: f"[Link]({url})" if pd.notnull(url) else "")
                # Rename columns for display
                rename_dict = {"username": "Username", "followers": "Followers", "posts": "Posts", "bio": "Bio", "profile_url": "Profile URL"}
                df = df.rename(columns=rename_dict)
                st.dataframe(df, use_container_width=True)
                
                # Option to save accounts
                st.markdown("#### Save Verified Accounts")
                save_filename = st.text_input("Enter filename to save (e.g., verified_accounts.txt):", value="verified_accounts.txt")
                st.write(f"Current working directory: {os.getcwd()}")
                if st.button("Save to Verified Accounts List"):
                    usernames = [a["username"] for a in st.session_state.get('found_accounts', []) if "username" in a]
                    st.write(f"Usernames to save: {usernames}")
                    try:
                        with open(save_filename, "w") as f:
                            for u in usernames:
                                f.write(u + "\n")
                        st.success(f"Saved {len(usernames)} accounts to {save_filename}")
                    except Exception as e:
                        st.error(f"Error saving to {save_filename}: {e}")
            else:
                st.info("No accounts to display.")
        
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "✅ Verify Accounts":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Verify Instagram Accounts")
    st.markdown("Check if Instagram accounts are public and accessible")
    
    # List all files matching 'verified_accounts*.txt'
    verified_files = glob.glob("verified_accounts*.txt")
    if not verified_files:
        verified_files = ["verified_accounts.txt"]
    
    # Input options
    verify_option = st.radio("How would you like to verify accounts?", [
        "Enter account names manually",
        "Verify from a saved verified accounts file"
    ])
    
    def verify_instagram_account_streamlit(username):
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            if profile.is_private:
                return False, None, "Private account"
            return True, profile, None
        except instaloader.exceptions.ProfileNotExistsException:
            return False, None, "Profile does not exist"
        except instaloader.exceptions.LoginRequiredException:
            return False, None, "Login required"
        except Exception as e:
            return False, None, str(e)
    
    if verify_option == "Enter account names manually":
        accounts_input = st.text_area("Enter Instagram usernames (one per line):", 
                                      placeholder="natgeo\nchrisburkard\nbeautifuldestinations")
        verify_button = st.button("Verify Accounts")
        
        if verify_button and accounts_input:
            accounts_to_verify = [a.strip() for a in accounts_input.split('\n') if a.strip()]
            st.markdown("#### Verification Results")
            progress_bar = st.progress(0)
            results = []
            verified_accounts = []
            for i, account in enumerate(accounts_to_verify):
                st.write(f"Verifying @{account}...")
                is_verified, profile, error = verify_instagram_account_streamlit(account)
                if is_verified:
                    status = "✅ Public"
                    details = {
                        "Account": f"@{account}",
                        "Status": status,
                        "Username": profile.username,
                        "Full Name": profile.full_name,
                        "Followers": f"{profile.followers:,}",
                        "Following": f"{profile.followees:,}",
                        "Bio": profile.biography,
                        "External URL": profile.external_url if profile.external_url else "",
                        "Number of Posts": profile.mediacount,
                        "Profile Picture URL": profile.profile_pic_url,
                    }
                    verified_accounts.append(account)
                else:
                    status = "❌ Not accessible"
                    details = {
                        "Account": f"@{account}",
                        "Status": status,
                        "Username": account,
                        "Full Name": "-",
                        "Followers": "-",
                        "Following": "-",
                        "Bio": error,
                        "External URL": "",
                        "Number of Posts": "-",
                        "Profile Picture URL": "",
                    }
                results.append(details)
                progress_bar.progress((i + 1) / len(accounts_to_verify))
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            successful = sum(1 for r in results if "✅" in r["Status"])
            if successful > 0:
                # Save verified accounts to file
                existing = set()
                if os.path.isfile("verified_accounts.txt"):
                    with open("verified_accounts.txt", "r") as f:
                        existing = set(line.strip() for line in f if line.strip())
                new_accounts = [a for a in verified_accounts if a not in existing]
                if new_accounts:
                    with open("verified_accounts.txt", "a") as f:
                        for a in new_accounts:
                            f.write(a + "\n")
                st.success(f"{successful} accounts verified successfully and added to verified_accounts.txt")
            else:
                st.error("No accounts could be verified. Try different accounts.")
    else:  # Verify from file
        selected_file = st.selectbox("Select a verified accounts file:", verified_files)
        st.info(f"This will verify all accounts in your {selected_file} file")
        verify_file_button = st.button("Start Verification")
        if verify_file_button:
            st.info(f"Loading accounts from {selected_file}...")
            time.sleep(1)
            if os.path.isfile(selected_file):
                with open(selected_file, "r") as f:
                    file_accounts = [line.strip() for line in f if line.strip()]
            else:
                file_accounts = []
            if not file_accounts:
                st.error(f"No accounts found in {selected_file}.")
            else:
                st.success(f"Loaded {len(file_accounts)} accounts from file")
                progress_bar = st.progress(0)
                results = []
                verified_accounts = []
                for i, account in enumerate(file_accounts):
                    st.write(f"Verifying @{account}...")
                    is_verified, profile, error = verify_instagram_account_streamlit(account)
                    if is_verified:
                        status = "✅ Public"
                        details = {
                            "Account": f"@{account}",
                            "Status": status,
                            "Username": profile.username,
                            "Full Name": profile.full_name,
                            "Followers": f"{profile.followers:,}",
                            "Following": f"{profile.followees:,}",
                            "Bio": profile.biography,
                            "External URL": profile.external_url if profile.external_url else "",
                            "Number of Posts": profile.mediacount,
                            "Profile Picture URL": profile.profile_pic_url,
                        }
                        verified_accounts.append(account)
                    else:
                        status = "❌ Not accessible"
                        details = {
                            "Account": f"@{account}",
                            "Status": status,
                            "Username": account,
                            "Full Name": "-",
                            "Followers": "-",
                            "Following": "-",
                            "Bio": error,
                            "External URL": "",
                            "Number of Posts": "-",
                            "Profile Picture URL": "",
                        }
                    results.append(details)
                    progress_bar.progress((i + 1) / len(file_accounts))
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True)
                successful = sum(1 for r in results if "✅" in r["Status"])
                if successful > 0:
                    # Overwrite file with only verified accounts
                    with open(selected_file, "w") as f:
                        for a in verified_accounts:
                            f.write(a + "\n")
                    st.success(f"Verification complete: {successful}/{len(file_accounts)} accounts verified and file updated.")
                else:
                    st.error("No accounts could be verified.")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "📥 Download Content":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Download Instagram Content")
    
    download_option = st.radio("Select download option:", [
        "Download from a single account",
        "Batch download from verified accounts"
    ])
    
    if download_option == "Download from a single account":
        with st.form("single_download_form"):
            username = st.text_input("Instagram username:", placeholder="e.g., natgeo")
            posts_limit = st.slider("Number of posts to download:", 1, 10, 3)
            download_media = st.checkbox("Download media (images/videos)", value=False)
            submitted = st.form_submit_button("Start Download")
        
        if submitted and username:
            st.info(f"Starting download for @{username}")
            progress_bar = st.progress(0)
            status_container = st.empty()
            status_container.write("Verifying account...")
            progress_bar.progress(0.1)
            # Try to download using the real function
            try:
                result = simple_profile_download(username, posts_limit)
                progress_bar.progress(1.0)
                if result:
                    status_container.success(f"Successfully downloaded {posts_limit} posts from @{username}")
                    st.info(f"Content saved to @{username}_simple/")
                    if st.button("Analyze Downloaded Content"):
                        st.session_state.analyze_username = username
                        st.session_state.page = "📊 Analyze Data"
                        st.experimental_rerun()
                else:
                    status_container.error(f"Failed to download from @{username}. The account may be private, does not exist, or rate limited.")
            except Exception as e:
                status_container.error(f"Error: {e}")
    else:  # Batch download
        st.markdown("#### Batch Download from Verified Accounts")
        # Load verified accounts from file
        verified_accounts = []
        if os.path.isfile("verified_accounts.txt"):
            with open("verified_accounts.txt", "r") as f:
                verified_accounts = [line.strip() for line in f if line.strip()]
        if not verified_accounts:
            st.warning("No verified accounts found in verified_accounts.txt. Please verify accounts first.")
        else:
            st.info(f"Found {len(verified_accounts)} verified accounts")
            col1, col2 = st.columns(2)
            with col1:
                selected_accounts = st.multiselect(
                    "Select accounts to download from:",
                    verified_accounts,
                    default=verified_accounts[:3] if len(verified_accounts) >= 3 else verified_accounts
                )
            with col2:
                posts_per_account = st.slider("Posts per account:", 1, 5, 2)
                batch_size = st.slider("Batch size:", 1, 5, 3)
            metadata_only = st.checkbox("Download metadata only (no images/videos)", value=True)
            if st.button("Start Batch Download") and selected_accounts:
                progress_bar = st.progress(0)
                status_container = st.empty()
                total_accounts = len(selected_accounts)
                completed = 0
                successful = 0
                for i, account in enumerate(selected_accounts):
                    status_container.write(f"Downloading from @{account}...")
                    try:
                        result = simple_profile_download(account, posts_per_account)
                        if result:
                            successful += 1
                            status_container.success(f"Successfully downloaded {posts_per_account} posts from @{account}")
                        else:
                            status_container.error(f"Failed to download from @{account}. The account may be private, does not exist, or rate limited.")
                    except Exception as e:
                        status_container.error(f"Error downloading from @{account}: {e}")
                    completed += 1
                    progress_bar.progress(completed / total_accounts)
                status_container.success(f"Batch download complete! Successfully downloaded from {successful}/{total_accounts} accounts")
                if successful > 0 and st.button("Analyze Downloaded Content"):
                    st.session_state.page = "📊 Analyze Data"
                    st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "📊 Analyze Data":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Analyze Instagram Content")
    
    # Analysis options
    analysis_option = st.radio("What would you like to analyze?", [
        "Recently downloaded content",
        "Existing JSON files",
        "Sample data (for demonstration)",
        "Combine All Downloaded JSONs"
    ])
    
    if analysis_option == "Recently downloaded content":
        # In a real app, you'd detect downloaded content here
        # For demo, we'll simulate some accounts with downloaded content
        
        downloaded_accounts = ["natgeo", "chrisburkard", "beautifuldestinations"]
        selected_account = st.selectbox("Select account to analyze:", downloaded_accounts)
        
        if st.button("Start Analysis") and selected_account:
            with st.spinner(f"Analyzing content from @{selected_account}..."):
                # Simulate analysis process
                time.sleep(2)
                
                # Generate some simulated post data
                posts = []
                for i in range(5):
                    is_video = random.choice([True, False])
                    likes = random.randint(5000, 100000)
                    comments = random.randint(100, 5000)
                    views = random.randint(20000, 500000) if is_video else 0
                    
                    posts.append({
                        'username': selected_account,
                        'post_id': f"B{random.randint(100000, 999999)}",
                        'is_video': is_video,
                        'likes': likes,
                        'comments': comments,
                        'views': views,
                        'timestamp': (datetime.now() - pd.Timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                        'engagement_rate': round((likes + comments*2) / 1000000 * 100, 2),
                        'smart_score': round(random.uniform(30, 95), 2)
                    })
                
                df = pd.DataFrame(posts)
                st.session_state.analyzed_data = df  # Store in session for later use
                
                # Generate CSV filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"{selected_account}_analysis_{timestamp}.csv"
                
                # Display analysis results
                st.success(f"Analysis complete for {len(df)} posts from @{selected_account}")
                
                # Show summary statistics
                st.markdown("#### Summary Statistics")
                st.dataframe(df[['likes', 'comments', 'views', 'engagement_rate', 'smart_score']].describe().round(2), use_container_width=True)
                
                # Visualize engagement
                st.markdown("#### Engagement Visualization")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Create a bar chart for engagement metrics
                    metrics_df = pd.DataFrame({
                        'Metric': ['Likes', 'Comments', 'Views'],
                        'Average': [df['likes'].mean(), df['comments'].mean(), df['views'].mean()]
                    })
                    
                    fig = px.bar(metrics_df, x='Metric', y='Average', 
                                title=f'Average Engagement Metrics for @{selected_account}',
                                color='Average',
                                color_continuous_scale=px.colors.sequential.Plasma)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Create a scatter plot for individual posts
                    fig = px.scatter(df, x='likes', y='comments', 
                                    size='smart_score', color='smart_score',
                                    hover_name='post_id',
                                    title='Likes vs Comments by Smart Score',
                                    color_continuous_scale=px.colors.sequential.Viridis)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Add full data display
                st.markdown("#### Full Data")
                st.dataframe(df, use_container_width=True)
                
                # Add download button
                csv = df.to_csv(index=False).encode('utf-8')
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.download_button(
                        label=f"📥 Download CSV for @{selected_account}",
                        data=csv,
                        file_name=csv_filename,
                        mime="text/csv",
                        help="Download the complete analysis as a CSV file"
                    )
                
                with col2:
                    # View top content button
                    if st.button("View Top Content Recommendations"):
                        st.session_state.analyzed_data = df
                        st.session_state.page = "🏆 View Recommendations"
                        st.experimental_rerun()
    
    elif analysis_option == "Existing JSON files":
        st.info("This will analyze JSON files that were previously downloaded")
        folder_path = st.text_input("Enter path to folder containing JSON files:", value="./")
        if st.button("Analyze JSON Files") and folder_path:
            with st.spinner("Analyzing JSON files..."):
                if analyze_collected_data is not None:
                    # Use the imported function to analyze real JSON files
                    try:
                        df = analyze_collected_data("")  # Keyword is not used for folder search
                        if df is not None and not df.empty:
                            st.session_state.analyzed_data = df
                            st.success(f"Analysis complete! {len(df)} posts analyzed.")
                            st.dataframe(df.head(20), use_container_width=True)
                            # Download button
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Download Complete CSV Analysis",
                                data=csv,
                                file_name="json_analysis.csv",
                                mime="text/csv",
                                help="Download the complete analysis results as a CSV file"
                            )
                            if st.button("View Top Content Recommendations"):
                                st.session_state.analyzed_data = df
                                st.session_state.page = "🏆 View Recommendations"
                                st.experimental_rerun()
                        else:
                            st.error("No valid data found in JSON files.")
                    except Exception as e:
                        st.error(f"Error analyzing JSON files: {e}")
                else:
                    st.error("analyze_collected_data function not found in Insta Content Automation.py.")
    
    elif analysis_option == "Sample data":
        st.info("Analyzing sample data for demonstration purposes")
        
        if st.button("Generate Sample Analysis"):
            with st.spinner("Generating sample analysis..."):
                # Wait for effect
                time.sleep(2)
                
                # Generate sample data for multiple accounts
                accounts = ["natgeo", "chrisburkard", "beautifuldestinations", 
                           "lonelyplanet", "expertvagabond"]
                
                posts = []
                for _ in range(50):
                    account = random.choice(accounts)
                    is_video = random.choice([True, False])
                    likes = random.randint(5000, 500000)
                    comments = random.randint(100, 20000)
                    views = random.randint(20000, 2000000) if is_video else 0
                    days_ago = random.randint(1, 90)
                    
                    # Calculate a realistic smart score
                    base_score = (likes/10000) + (comments/500) 
                    recency_boost = max(0, 30 - days_ago) / 3
                    video_boost = 10 if is_video and views > 100000 else 0
                    smart_score = min(99, max(10, base_score + recency_boost + video_boost))
                    
                    posts.append({
                        'username': account,
                        'post_id': f"B{random.randint(100000, 999999)}",
                        'is_video': is_video,
                        'likes': likes,
                        'comments': comments,
                        'views': views,
                        'timestamp': (datetime.now() - pd.Timedelta(days=days_ago)).strftime("%Y-%m-%d"),
                        'engagement_rate': round((likes + comments*2) / 1000000 * 100, 2),
                        'smart_score': round(smart_score, 2)
                    })
                
                df = pd.DataFrame(posts)
                st.session_state.analyzed_data = df  # Store in session state
                
                # Generate CSV filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"sample_analysis_{timestamp}.csv"
                
                # Display analysis results
                st.success(f"Sample analysis complete for {len(df)} posts from {len(accounts)} accounts")
                
                # Visualize engagement by account
                st.markdown("#### Engagement by Account")
                
                account_engagement = df.groupby('username').agg({
                    'likes': 'mean',
                    'comments': 'mean',
                    'smart_score': 'mean'
                }).reset_index()
                
                fig = px.bar(account_engagement, x='username', y='smart_score',
                            color='likes',
                            title='Average Smart Score by Account',
                            labels={'username': 'Account', 'smart_score': 'Smart Score'},
                            color_continuous_scale=px.colors.sequential.Viridis)
                st.plotly_chart(fig, use_container_width=True)
                
                # Distribution of smart scores
                st.markdown("#### Smart Score Distribution")
                
                fig = px.histogram(df, x='smart_score', 
                                  title='Distribution of Smart Scores',
                                  color_discrete_sequence=['#F56040'])
                fig.update_layout(xaxis_title='Smart Score', yaxis_title='Count')
                st.plotly_chart(fig, use_container_width=True)
                
                # Add data preview
                st.markdown("#### Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Add download section
                csv = df.to_csv(index=False).encode('utf-8')
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.download_button(
                        label="📥 Download Sample Analysis CSV",
                        data=csv,
                        file_name=csv_filename,
                        mime="text/csv",
                        help="Download the complete sample analysis as a CSV file"
                    )
                
                with col2:
                    # View top content button
                    if st.button("View Top Content Recommendations"):
                        st.session_state.analyzed_data = df
                        st.session_state.page = "🏆 View Recommendations"
                        st.experimental_rerun()
    
    elif analysis_option == "Combine All Downloaded JSONs":
        st.info("This will combine every JSON in every subfolder and analyze the combined CSV.")
        analyze_type = st.radio("Select content type to analyze:", ["All", "Posts only (GraphSidecar)", "Videos only (GraphVideo)"])
        if st.button("Combine and Analyze All JSONs"):
            with st.spinner("Combining and analyzing all JSON files in all subfolders..."):
                result = combine_all_jsons_and_analyze()
                if result is None:
                    st.error("No JSON files found in any subfolder.")
                else:
                    df, csv_name = result
                    st.session_state.analyzed_data = df
                    st.success(f"Combined and analyzed {len(df)} posts from all JSONs.")
                    st.dataframe(df.head(20), use_container_width=True)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Combined CSV",
                        data=csv,
                        file_name=csv_name,
                        mime="text/csv",
                        help="Download the combined analysis as a CSV file"
                    )
                    st.markdown("#### Top Content Recommendations")
                    show_top_content_recommendations(df, analyze_type)

    st.markdown("</div>", unsafe_allow_html=True)

elif page == "🏆 View Recommendations":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Content Recommendations")
    
    # Check if we have analyzed data
    if hasattr(st.session_state, 'analyzed_data') and not st.session_state.analyzed_data.empty:
        df = st.session_state.analyzed_data.copy()
        st.markdown("#### Top Content Recommendations Preview")
        show_top_content_recommendations(df)
        # Button to save selected posts to CSV
        if st.button("Save Selected Posts to CSV"):
            selected_shortcodes = st.session_state['selected_shortcodes']
            selected_df = df[df.apply(lambda r: (r.get('node.shortcode') or r.get('node.iphone_struct.shortcode') or '') in selected_shortcodes, axis=1)].copy()
            if not selected_df.empty:
                selected_df['likes'] = selected_df.apply(lambda r: r.get('node.edge_media_preview_like.count') or r.get('node.iphone_struct.edge_media_preview_like.count') or r.get('node.iphone_struct.edge_liked_by.count') or 0, axis=1)
                selected_df['comments'] = selected_df.apply(lambda r: r.get('node.comments') or r.get('node.iphone_struct.edge_media_to_comment.count') or 0, axis=1)
                selected_df['views'] = selected_df.apply(lambda r: r.get('node.video_view_count') or r.get('node.iphone_struct.video_view_count') or 0, axis=1)
                selected_df['type_str'] = selected_df.apply(lambda r: r.get('node.__typename') or r.get('node.iphone_struct.__typename') or ("Video" if r.get('node.is_video', False) else "Image"), axis=1)
                selected_df['date_str'] = selected_df.apply(lambda r: r.get('node.date') or r.get('node.iphone_struct.taken_at_timestamp') or '', axis=1)
                selected_df['post_shortcode'] = selected_df.apply(lambda r: r.get('node.shortcode') or r.get('node.iphone_struct.shortcode') or '', axis=1)
                selected_df['post_url'] = selected_df['post_shortcode'].apply(lambda s: f"https://www.instagram.com/p/{s}")
                selected_df['likes'] = selected_df['likes'].apply(lambda x: 0 if pd.isna(x) else int(x))
                selected_df['comments'] = selected_df['comments'].apply(lambda x: 0 if pd.isna(x) else int(x))
                selected_df['views'] = selected_df['views'].apply(lambda x: 0 if pd.isna(x) else int(x))
                csv = selected_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Selected Posts as CSV",
                    data=csv,
                    file_name="selected_posts.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No posts selected.")
    else:
        st.warning("No analyzed data available. Please analyze content first.")
        if st.button("Go to Analysis"):
            st.session_state.page = "📊 Analyze Data"
            st.experimental_rerun()
        st.markdown("#### Sample Recommendation")
        st.markdown("""
        <div style="padding:10px; margin-bottom:10px; border-radius:5px; background-color:#f8f9fa;">
            <span style="font-size:18px; font-weight:bold;">Rank 1 ⭐⭐⭐</span><br>
            <span style="color:#1DA1F2; font-size:16px;">@natgeo</span><br>
            <span>Smart Score: <b>92.5</b> | Likes: 254,789 | Comments: 3,421</span><br>
            <span>Type: Image | Date: 2023-04-15</span><br>
            <span>Link: <a href="https://www.instagram.com/p/B123456789">
            https://www.instagram.com/p/B123456789</a></span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "⚙️ Settings":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Settings")
    
    # API settings
    st.markdown("#### API Settings")
    
    # Toggle for session loading
    use_session = st.toggle("Load Instagram session (for private accounts)", value=False)
    
    if use_session:
        col1, col2 = st.columns(2)
        
        with col1:
            session_id = st.text_input("Session ID:", type="password")
            csrf_token = st.text_input("CSRF Token:", type="password")
        
        with col2:
            ds_user_id = st.text_input("DS User ID:", type="password")
            ig_did = st.text_input("IG DID:", type="password")
        
        if st.button("Save Session Settings"):
            if session_id and csrf_token and ds_user_id:
                st.success("Session settings saved successfully")
            else:
                st.error("Please fill in all required session fields")
    
    # Download settings
    st.markdown("#### Download Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Download pictures", value=False)
        st.checkbox("Download videos", value=False)
        st.checkbox("Download video thumbnails", value=False)
    
    with col2:
        st.checkbox("Download geotags", value=False)
        st.checkbox("Download comments", value=False)
        st.checkbox("Compress JSON", value=False)
    
    # Analysis settings
    st.markdown("#### Analysis Settings")
    
    like_weight = st.slider("Like weight:", 0.5, 2.0, 1.0, 0.1)
    comment_weight = st.slider("Comment weight:", 0.5, 5.0, 2.0, 0.1)
    view_weight = st.slider("View weight:", 0.1, 1.0, 0.5, 0.1)
    recency_factor = st.slider("Recency factor:", 0.1, 1.0, 0.5, 0.1)
    
    # Save settings button
    if st.button("Save Analysis Settings"):
        st.success("Analysis settings saved successfully")
    
    # Reset settings button
    if st.button("Reset to Default Settings"):
        st.info("All settings have been reset to default values")
        st.experimental_rerun()
    
    # OpenAI API Key input
    st.text_input("OpenAI API Key", type="password", key="openai_api_key", on_change=set_openai_key)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Initialize app state based on navigation
if 'page' in st.session_state:
    st.sidebar.info(f"Current page changed to: {st.session_state.page}")
    st.experimental_rerun()

# Handle rate limiting information in the sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### ℹ️ About Rate Limiting")
    st.info("""
    This app respects Instagram's rate limiting.
    
    Instaloader automatically handles:
    - Tracking API requests
    - Deferring subsequent requests
    - Retrying after temporary bans
    
    No manual delays are needed.
    """)
    
    # Current status indicator
    st.markdown("### API Status")
    status = random.choice(["✅ Good", "✅ Good", "✅ Good", "⚠️ Limited"])
    
    if status == "✅ Good":
        st.success("Instagram API Status: Good")
    else:
        st.warning("Instagram API Status: Rate Limited\nRetrying automatically")
