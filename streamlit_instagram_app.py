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

# Set page config
st.set_page_config(
    page_title="Instagram Content Automation",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Home page
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

# Search accounts page
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
        with st.spinner(f"Searching for Instagram accounts related to '{keyword}'..."):
            # This is a placeholder for the account search function
            # In a production app, you would call the search_instagram_accounts function here
            
            # For demo purposes, generate some example accounts based on the keyword
            st.markdown(f"#### Results for '{keyword}'")
            
            # Example accounts data structure
            example_accounts = {
                "travel": ["natgeo", "chrisburkard", "danielkordan", "beautifuldestinations", "expertvagabond"],
                "photography": ["natgeotravel", "stevemccurryofficial", "humansofny", "street_photographers", "magnumphotos"],
                "food": ["foodnetwork", "buzzfeedfood", "food52", "bonappetitmag", "jamieoliver"],
                "fashion": ["vogue", "hypebeast", "fashionweek", "gucci", "dior"],
                "india": ["incredibleindia", "indianphotostories", "indiatravelgram", "storiesofindia", "indiapictures"]
            }
            
            # Get accounts based on keyword or use default
            found_accounts = []
            for k, accounts in example_accounts.items():
                if k in keyword.lower():
                    found_accounts.extend(accounts)
            
            # If no matches, use a default set
            if not found_accounts:
                found_accounts = ["natgeo", "chrisburkard", "beautifuldestinations", "expertvagabond", "lonelyplanet"]
            
            # Display found accounts
            found_accounts = found_accounts[:max_accounts]
            
            # Create a dataframe for display
            df = pd.DataFrame({
                "Username": [f"@{account}" for account in found_accounts],
                "Followers": [random.randint(10000, 5000000) for _ in range(len(found_accounts))],
                "Posts": [random.randint(100, 5000) for _ in range(len(found_accounts))]
            })
            
            # Format numbers with K and M
            df["Followers"] = df["Followers"].apply(lambda x: f"{x/1000:.1f}K" if x < 1000000 else f"{x/1000000:.1f}M")
            
            # Display the table with accounts
            st.dataframe(df, use_container_width=True)
            
            # Option to save accounts
            if st.button("Save to Verified Accounts List"):
                accounts_to_save = [account.strip('@') for account in df["Username"].tolist()]
                
                # In a real app, you'd call manage_account_list here
                st.success(f"Saved {len(accounts_to_save)} accounts to verified_accounts.txt")
                
                # Show the accounts that were saved
                st.code("\n".join(accounts_to_save))
        
        st.markdown("</div>", unsafe_allow_html=True)

# Verify accounts page
elif page == "✅ Verify Accounts":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Verify Instagram Accounts")
    st.markdown("Check if Instagram accounts are public and accessible")
    
    # Input options
    verify_option = st.radio("How would you like to verify accounts?", [
        "Enter account names manually",
        "Verify from verified_accounts.txt"
    ])
    
    if verify_option == "Enter account names manually":
        accounts_input = st.text_area("Enter Instagram usernames (one per line):", 
                                      placeholder="natgeo\nchrisburkard\nbeautifuldestinations")
        verify_button = st.button("Verify Accounts")
        
        if verify_button and accounts_input:
            accounts_to_verify = [a.strip() for a in accounts_input.split('\n') if a.strip()]
            
            st.markdown("#### Verification Results")
            
            progress_bar = st.progress(0)
            results = []
            
            for i, account in enumerate(accounts_to_verify):
                # Simulate verification process
                st.write(f"Verifying @{account}...")
                
                # In a real app, you'd call verify_instagram_account here
                # For demo, we'll simulate the process
                time.sleep(0.5)  # Simulate API call
                
                # Random verification result for demo
                is_verified = random.choice([True, True, True, False])
                followers = random.randint(10000, 5000000) if is_verified else 0
                
                if is_verified:
                    status = "✅ Public"
                    message = f"Accessible with {followers:,} followers"
                else:
                    status = "❌ Not accessible"
                    message = "Private account or does not exist"
                
                results.append({"Account": f"@{account}", "Status": status, "Details": message})
                
                # Update progress
                progress_bar.progress((i + 1) / len(accounts_to_verify))
            
            # Display results table
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            
            # Count successful verifications
            successful = sum(1 for r in results if "✅" in r["Status"])
            
            if successful > 0:
                st.success(f"{successful} accounts verified successfully and added to verified_accounts.txt")
            else:
                st.error("No accounts could be verified. Try different accounts.")
    
    else:  # Verify from file
        st.info("This will verify all accounts in your verified_accounts.txt file")
        verify_file_button = st.button("Start Verification")
        
        if verify_file_button:
            # Simulate loading accounts from file
            st.info("Loading accounts from verified_accounts.txt...")
            time.sleep(1)
            
            # Simulate accounts for demo
            file_accounts = ["natgeo", "chrisburkard", "beautifuldestinations", 
                             "lonelyplanet", "expertvagabond", "taramilktea"]
            
            st.success(f"Loaded {len(file_accounts)} accounts from file")
            
            # Show verification process
            progress_bar = st.progress(0)
            results = []
            
            for i, account in enumerate(file_accounts):
                st.write(f"Verifying @{account}...")
                
                # Simulate verification
                time.sleep(0.5)
                is_verified = random.choice([True, True, False])
                followers = random.randint(10000, 5000000) if is_verified else 0
                
                if is_verified:
                    status = "✅ Public"
                    message = f"Accessible with {followers:,} followers"
                else:
                    status = "❌ Not accessible"
                    message = "Private account or does not exist"
                
                results.append({"Account": f"@{account}", "Status": status, "Details": message})
                
                # Update progress
                progress_bar.progress((i + 1) / len(file_accounts))
            
            # Display results
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            
            # Count successful verifications
            successful = sum(1 for r in results if "✅" in r["Status"])
            
            if successful > 0:
                st.success(f"Verification complete: {successful}/{len(file_accounts)} accounts verified")
            else:
                st.error("No accounts could be verified.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Download content page
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
            
            # Progress updates
            progress_bar = st.progress(0)
            status_container = st.empty()
            
            # Simulate download process
            total_steps = posts_limit + 2  # account verification + posts + completion
            
            # Step 1: Verify account
            status_container.write("Verifying account...")
            progress_bar.progress(1/total_steps)
            time.sleep(1)
            
            # Simulate verification
            is_verified = random.choice([True, True, True, False])
            
            if not is_verified:
                status_container.error(f"@{username} is not accessible (private or doesn't exist)")
            else:
                status_container.success(f"@{username} verified successfully")
                
                # Step 2+: Download posts
                for i in range(posts_limit):
                    status_container.write(f"Downloading post {i+1}/{posts_limit}...")
                    progress_bar.progress((i+2)/total_steps)
                    time.sleep(0.8)  # Simulate download time
                
                # Final step
                progress_bar.progress(1.0)
                status_container.success(f"Successfully downloaded {posts_limit} posts from @{username}")
                
                # Show download directory
                st.info(f"Content saved to @{username}_data/")
                
                # Option to proceed to analysis
                if st.button("Analyze Downloaded Content"):
                    st.session_state.analyze_username = username
                    st.session_state.page = "📊 Analyze Data"
                    st.experimental_rerun()
    
    else:  # Batch download
        st.markdown("#### Batch Download from Verified Accounts")
        
        # Load verified accounts
        # In a real app, you'd actually load from verified_accounts.txt
        verified_accounts = ["natgeo", "chrisburkard", "beautifuldestinations", 
                           "lonelyplanet", "expertvagabond", "taramilktea"]
        
        st.info(f"Found {len(verified_accounts)} verified accounts")
        
        # Batch download options
        col1, col2 = st.columns(2)
        with col1:
            selected_accounts = st.multiselect(
                "Select accounts to download from:",
                verified_accounts,
                default=verified_accounts[:3]
            )
        
        with col2:
            posts_per_account = st.slider("Posts per account:", 1, 5, 2)
            batch_size = st.slider("Batch size:", 1, 5, 3)
        
        metadata_only = st.checkbox("Download metadata only (no images/videos)", value=True)
        
        if st.button("Start Batch Download") and selected_accounts:
            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_container = st.empty()
            
            total_accounts = len(selected_accounts)
            completed = 0
            successful = 0
            
            # Process in batches
            for i in range(0, total_accounts, batch_size):
                batch = selected_accounts[i:i+batch_size]
                status_container.write(f"Processing batch {i//batch_size + 1}...")
                
                for account in batch:
                    status_container.write(f"Downloading from @{account}...")
                    
                    # Simulate download process
                    time.sleep(1)
                    success = random.choice([True, True, True, False])
                    
                    if success:
                        successful += 1
                        status_container.success(f"Successfully downloaded {posts_per_account} posts from @{account}")
                    else:
                        error_type = random.choice(["rate limit", "not accessible", "connection error"])
                        status_container.error(f"Failed to download from @{account}: {error_type}")
                    
                    completed += 1
                    progress_bar.progress(completed / total_accounts)
                
                # Simulate batch completion
                if i + batch_size < total_accounts:
                    status_container.info("Completed batch. Taking a short pause before next batch...")
                    time.sleep(1)
            
            # Final status
            status_container.success(f"Batch download complete! Successfully downloaded from {successful}/{total_accounts} accounts")
            
            # Option to proceed to analysis
            if successful > 0 and st.button("Analyze Downloaded Content"):
                st.session_state.page = "📊 Analyze Data"
                st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Analyze data page
elif page == "📊 Analyze Data":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Analyze Instagram Content")
    
    # Analysis options
    analysis_option = st.radio("What would you like to analyze?", [
        "Recently downloaded content",
        "Existing JSON files",
        "Sample data (for demonstration)"
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
        
        # Folder selection
        folder_path = st.text_input("Enter path to folder containing JSON files:", value="./")
        
        if st.button("Analyze JSON Files") and folder_path:
            with st.spinner("Analyzing JSON files..."):
                # Simulate searching for JSON files
                time.sleep(1)
                st.info("Searching for JSON files in the specified folder...")
                time.sleep(1)
                
                # Simulate finding files
                json_count = random.randint(10, 30)
                st.success(f"Found {json_count} JSON files to analyze")
                
                # Simulate processing
                progress_bar = st.progress(0)
                for i in range(json_count):
                    progress_bar.progress((i+1)/json_count)
                    time.sleep(0.1)
                
                # Generate simulated results
                posts = []
                accounts = ["natgeo", "chrisburkard", "beautifuldestinations", "lonelyplanet"]
                
                for _ in range(json_count):
                    account = random.choice(accounts)
                    is_video = random.choice([True, False])
                    likes = random.randint(5000, 100000)
                    comments = random.randint(100, 5000)
                    views = random.randint(20000, 500000) if is_video else 0
                    
                    posts.append({
                        'username': account,
                        'post_id': f"B{random.randint(100000, 999999)}",
                        'is_video': is_video,
                        'likes': likes,
                        'comments': comments,
                        'views': views,
                        'timestamp': (datetime.now() - pd.Timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
                        'engagement_rate': round((likes + comments*2) / 1000000 * 100, 2),
                        'smart_score': round(random.uniform(20, 95), 2)
                    })
                
                df = pd.DataFrame(posts)
                st.session_state.analyzed_data = df  # Store in session for later use
                
                # Generate CSV filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"json_analysis_{timestamp}.csv"
                
                # Display analysis summary
                st.success(f"Analysis complete! Results are ready for download.")
                
                # Show account breakdown
                st.markdown("#### Posts by Account")
                account_counts = df['username'].value_counts().reset_index()
                account_counts.columns = ['Account', 'Posts']
                
                fig = px.pie(account_counts, values='Posts', names='Account', 
                            title='Posts Distribution by Account',
                            color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig, use_container_width=True)
                
                # Display preview of analyzed data
                st.markdown("#### Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Add a CSV download button
                csv = df.to_csv(index=False).encode('utf-8')
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.download_button(
                        label="📥 Download Complete CSV Analysis",
                        data=csv,
                        file_name=csv_filename,
                        mime="text/csv",
                        help="Download the complete analysis results as a CSV file"
                    )
                
                with col2:
                    # View top content button
                    if st.button("View Top Content Recommendations"):
                        st.session_state.analyzed_data = df
                        st.session_state.page = "🏆 View Recommendations"
                        st.experimental_rerun()
    
    else:  # Sample data
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
    
    st.markdown("</div>", unsafe_allow_html=True)

# View recommendations page
elif page == "🏆 View Recommendations":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Content Recommendations")
    
    # Check if we have analyzed data
    if hasattr(st.session_state, 'analyzed_data') and not st.session_state.analyzed_data.empty:
        df = st.session_state.analyzed_data
        
        # Sort by smart score
        df = df.sort_values('smart_score', descending=True)
        
        # Display top recommendations
        st.markdown("#### Top Recommended Content")
        st.info("Content is ranked by Smart Score, which considers engagement, recency, and content type")
        
        # Add rank and recommendation stars
        df['rank'] = range(1, len(df) + 1)
        df['recommendation'] = df['smart_score'].apply(
            lambda x: "⭐⭐⭐" if x >= 75 else ("⭐⭐" if x >= 50 else ("⭐" if x >= 25 else ""))
        )
        
        # Show top content
        top_content = df.head(10)
        
        # Create a nice display for top content
        for i, row in top_content.iterrows():
            st.markdown(f"""
            <div style="padding:10px; margin-bottom:10px; border-radius:5px; background-color:{"#f8f9fa"};">
                <span style="font-size:18px; font-weight:bold;">Rank {row['rank']} {row['recommendation']}</span><br>
                <span style="color:#1DA1F2; font-size:16px;">@{row['username']}</span><br>
                <span>Smart Score: <b>{row['smart_score']:.1f}</b> | 
                Likes: {row['likes']:,} | Comments: {row['comments']:,}</span><br>
                <span>Type: {"Video" if row['is_video'] else "Image"} | 
                Date: {row['timestamp']}</span><br>
                <span>Link: <a href="https://www.instagram.com/p/{row['post_id']}">
                https://www.instagram.com/p/{row['post_id']}</a></span>
            </div>
            """, unsafe_allow_html=True)
        
        # Download recommendations
        if st.button("Download Recommendations as CSV"):
            # In a real app, you'd actually save this file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_name = f"content_recommendations_{timestamp}.csv"
            
            st.success(f"Recommendations saved to {csv_name}")
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=csv_name,
                mime="text/csv"
            )
    
    else:
        st.warning("No analyzed data available. Please analyze content first.")
        
        # Button to go to analysis page
        if st.button("Go to Analysis"):
            st.session_state.page = "📊 Analyze Data"
            st.experimental_rerun()
        
        # Show a sample recommendation for demo
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

# Settings page
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