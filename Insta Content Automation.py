# %%capture
# !pip install git+https://github.com/SamuMazzi/instaloader.git
# !pip install pandas

from pickle import FALSE
import instaloader
import pandas as pd
import os
import json
import glob
from datetime import datetime
import time
import csv
import numpy as np
import random

# Create Instaloader instance with default settings for public profiles
L = instaloader.Instaloader(download_pictures=False,
                            download_video_thumbnails=False,
                            download_videos=False,
                            download_geotags=False,
                            download_comments=False,
                            save_metadata=True,
                            compress_json=False
                            )

# Optional session loading - comment out if you want to try without session
# L.load_session("", {
#     "csrftoken": "SdJPUcfGkUyTEyhqnWAWqKRgbbMKCzZb",
#     "sessionid": "74033679867%3AnqMT64Q2xnhTvB%3A3%3AAYcZci7A5L_mLSPDddzascqFMz3SbPT914kJS8eCAQ",
#     "ds_user_id": "74033679867",
#     "mid": "aBOTRQAEAAGVvCqwx0Yv0YPmjTEJ",
#     "ig_did": "775B73A4-7FC9-4881-924F-F8DC297A6F4A"
# })

# Simple function to download a single profile based on instaloader documentation
def simple_profile_download(username, posts_limit=5):
    """
    Simple profile downloader following instaloader documentation
    
    Args:
        username (str): Instagram username to download
        posts_limit (int): Maximum number of posts to download
    """
    try:
        print(f"Attempting to download profile: {username} (using simple method)")
        
        # Create folder for profile
        profile_dir = f"@{username}_simple"
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
            
        # Create a separate Instaloader instance for this download
        simple_loader = instaloader.Instaloader(
            download_pictures=True,  # Set to True to download actual media
            download_video_thumbnails=True,
            download_videos=True,
            download_geotags=False,
            download_comments=False,
            save_metadata=True,
            compress_json=False,
            post_metadata_txt_pattern='{caption}',
            dirname_pattern=profile_dir
        )
        
        # Get profile
        profile = instaloader.Profile.from_username(simple_loader.context, username)
        print(f"Found profile: {profile.username} with {profile.mediacount} posts")
        
        # Download recent posts (with limit)
        count = 0
        for post in profile.get_posts():
            try:
                simple_loader.download_post(post, target=profile_dir)
                count += 1
                print(f"Downloaded post {count}/{posts_limit} from {username}")
                
                if count >= posts_limit:
                    break
                    
                # Instaloader handles rate limiting automatically - no need for manual delays
                    
            except instaloader.exceptions.ConnectionException as e:
                if "429" in str(e):
                    print(f"Rate limit reached. Instaloader will automatically retry after cooldown period.")
                    # Let Instaloader handle the retry with its built-in mechanism
                else:
                    print(f"Connection error: {str(e)}")
            except Exception as e:
                print(f"Error downloading post: {str(e)}")
        
        print(f"Completed downloading {count} posts from {username}")
        return count > 0
        
    except instaloader.exceptions.TooManyRequestsException:
        print(f"Instagram rate limit reached for {username}. Instaloader will automatically retry when possible.")
        return False
    except Exception as e:
        print(f"Error downloading profile {username}: {str(e)}")
        return False

# Function to download posts with a specific hashtag
def get_it(keyword, numbers_of_files):
    while numbers_of_files > 0:
        for post in L.get_hashtag_posts(keyword):
            # post is an instance of instaloader.Post
            L.download_post(post, target='#'+keyword)
            numbers_of_files -= 1
            if numbers_of_files == 0:
                break
        print("loop ended for " + keyword)

# Function to download only reels with a specific hashtag
def get_reels(keyword, numbers_of_files):
    count = 0
    for post in L.get_hashtag_posts(keyword):
        # Check if the post is a reel
        if hasattr(post, 'is_video') and post.is_video and hasattr(post, 'video_url'):
            # Only download reels
            L.download_post(post, target='#'+keyword+'_reels')
            count += 1
            if count >= numbers_of_files:
                break
            print(f"Downloaded {count}/{numbers_of_files} reels for #{keyword}")
    print(f"Completed downloading {count} reels for #{keyword}")

# Function to download all reels from a list of public profiles
def get_profile_reels(profile_list, limit=None):
    """
    Download all reels from a list of public Instagram profiles.
    
    Args:
        profile_list (list): List of Instagram usernames to download reels from
        limit (int, optional): Maximum number of reels to download per profile. If None, download all.
    """
    for username in profile_list:
        try:
            # Get profile information
            profile = instaloader.Profile.from_username(L.context, username)
            print(f"Downloading reels from profile: {username}")
            
            # Create directory for this profile's reels
            target_dir = f"@profile_reels"
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            # Initialize counter
            count = 0
            
            # Iterate through profile posts
            for post in profile.get_posts():
                # Check if the post is a reel (is video)
                if hasattr(post, 'is_video') and post.is_video and hasattr(post, 'video_url'):
                    # Download the reel
                    L.download_post(post, target=target_dir)
                    count += 1
                    print(f"Downloaded reel {count} from {username}")
                    
                    # Check if limit reached
                    if limit is not None and count >= limit:
                        break
            
            print(f"Completed downloading {count} reels from {username}")
        
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"Profile {username} does not exist or is private")
        except Exception as e:
            print(f"Error downloading reels from {username}: {str(e)}")

# Function to process JSON files into a dataframe
def process_json_to_dataframe(keyword):
    # Look for JSON files in both regular posts and reels folders
    regular_json_files = glob.glob(f"#{keyword}/*.json")
    reels_json_files = glob.glob(f"#{keyword}_reels/*.json")
    json_files = regular_json_files + reels_json_files
    
    all_data = []
    
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                all_data.append(data)
            except json.JSONDecodeError:
                print(f"Error decoding {file}")
    
    # Convert list of dictionaries to dataframe
    df = pd.json_normalize(all_data)
    df.to_csv(f"{keyword}_{df.shape[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)
    return df

# Function to calculate engagement metrics
def calculate_engagement(df):
    # Remove rows with all NaN values
    df = df.dropna(how='all')
    
    # Check unique content types
    if 'node.__typename' in df.columns:
        print("Unique content types:", df['node.__typename'].unique())
    
    # Define weights for engagement score
    like_weight = 1
    comment_weight = 2
    view_weight = 0.5
    
    # Fill NaN values with zeros for numerical columns
    like_col = 'node.edge_media_preview_like.count'
    comment_col = 'node.iphone_struct.edge_media_to_comment.count'
    view_col = 'node.video_view_count'
    
    if like_col in df.columns:
        df[like_col] = df[like_col].fillna(0)
    else:
        df[like_col] = 0
        
    if comment_col in df.columns:
        df[comment_col] = df[comment_col].fillna(0)
    else:
        df[comment_col] = 0
        
    if view_col in df.columns:
        df[view_col] = df[view_col].fillna(0)
    else:
        df[view_col] = 0
    
    # Calculate engagement score
    df['engagement_score'] = (
        df[like_col] * like_weight +
        df[comment_col] * comment_weight +
        df[view_col] * view_weight
    )
    
    # Calculate smart recommendation score (percentage-based)
    # Avoid division by zero
    df['engagement_score_smart_recommendation'] = 0
    mask = df[view_col] > 0
    if any(mask):
        df.loc[mask, 'engagement_score_smart_recommendation'] = (
            (df.loc[mask, like_col] * like_weight +
             df.loc[mask, comment_col] * comment_weight) /
            df.loc[mask, view_col]
        ) * 100
    
    return df

# Function to search Instagram accounts based on a keyword
def search_instagram_accounts(keyword, max_accounts=50):
    """
    Search for Instagram accounts related to a keyword and return a list of midgroup Instagram influencers.
    
    Args:
        keyword (str): Keyword to search for
        max_accounts (int): Maximum number of influencers to return
        
    Returns:
        list: List of Instagram influencers profile related to the keyword
    """
    print(f"Searching for Instagram accounts related to '{keyword}'...")
    
    # Predefined list of popular travel-related accounts
    # This list is used instead of searching Instagram directly, which often gets blocked
    travel_accounts = {
        # Large travel accounts
        "natgeotravel": "National Geographic Travel - Professional photography, global destinations",
        "travelandleisure": "Travel and Leisure Magazine - Luxury travel, resorts, destinations",
        "lonelyplanet": "Lonely Planet - Travel guides, destinations, budget travel",
        "beautifuldestinations": "Beautiful Destinations - Scenic photography, luxury travel",
        "earthpix": "Earth Pix - Nature photography, landscapes, travel inspiration",
        # Mid-size travel accounts
        "nomadicmatt": "Nomadic Matt - Budget travel, backpacking, solo travel",
        "expertvagabond": "Expert Vagabond - Adventure travel, photography, hiking",
        "theplanetd": "The Planet D - Adventure couple, travel tips, destinations",
        "travelbabbo": "Travel Babbo - Family travel, cultural experiences",
        "everchanginghorizon": "Ever Changing Horizon - Outdoor adventures, photography",
        # India-specific travel accounts
        "indiantraveller": "Indian Traveller - Travel across India, hidden gems",
        "india_ig": "India Instagram - Cultural highlights, festivals, landscapes",
        "himalayas_ig": "Himalayas Instagram - Mountain adventures, trekking",
        "rajasthan_tourism": "Rajasthan Tourism - Desert landscapes, palaces, culture",
        "incredibleindia": "Incredible India - Official tourism account, diverse destinations",
        # Adventure-specific accounts
        "backpackerstory": "Backpacker Story - Budget travel, hostels, backpacking",
        "outdoortones": "Outdoor Tones - Nature, camping, hiking photography",
        "solotravelers": "Solo Travelers - Tips for traveling alone, solo adventures",
        "adventuresoflilnicki": "Adventures of Lil Nicki - Off the beaten path travel",
        "adventurefaktory": "Adventure Faktory - Adventure travel, extreme sports",
        # Budget travel accounts
        "thebrokebackpacker": "The Broke Backpacker - Budget travel, backpacking guides",
        "thepoorexplorer": "The Poor Explorer - Affordable travel, budget tips",
        "budgettraveller": "Budget Traveller - Economic travel, hostels, tips",
        "globalhelpswap": "Global Help Swap - Responsible travel on a budget",
        # Cultural travel accounts
        "cntraveler": "Condé Nast Traveler - Luxury travel, cultural experiences",
        "culturalxplorer": "Cultural Explorer - Cultural immersion, local experiences",
        "worldnomads": "World Nomads - Travel stories, cultural insights",
        # Food travel accounts
        "foodieindia": "Foodie India - Indian cuisine, street food, restaurant recommendations",
        "migrationology": "Migrationology - Food-focused travel, street food",
        "food_nomad": "Food Nomad - Culinary journeys, food markets",
        # Eco and sustainable travel
        "ecotravelist": "Eco Travelist - Sustainable travel, eco-friendly destinations",
        "earthwanderers": "Earth Wanderers - Ethical travel, conservation",
        # Photography-focused travel
        "travelphotoguides": "Travel Photo Guides - Photography tips, scenic locations",
        "indiapictures": "India Pictures - Visual journey through India's landscapes",
        # Various Indian destinations
        "keralatourism": "Kerala Tourism - Backwaters, beaches, Ayurveda",
        "himalayan_adventurer": "Himalayan Adventurer - Trekking, climbing, mountain life",
        "goatrekking": "Goa Trekking - Beach life, water sports, coastal adventures",
        "indianbackpacker": "Indian Backpacker - Budget travel across India",
        "roadsofrajasthan": "Roads of Rajasthan - Desert journeys, historical sites"
    }
    
    # Filter accounts based on the keyword
    filtered_accounts = {}
    keywords = [k.lower() for k in keyword.split()]
    
    for account, description in travel_accounts.items():
        # Check if any keyword matches in the account name or description
        if any(key in account.lower() for key in keywords) or any(key in description.lower() for key in keywords):
            filtered_accounts[account] = description
    
    # If no matches found with strict filtering, return some accounts related to the main theme
    if not filtered_accounts:
        # Identify main theme
        if 'india' in keyword.lower():
            theme = 'india'
        elif 'adventure' in keyword.lower():
            theme = 'adventure'
        elif 'budget' in keyword.lower() or 'cheap' in keyword.lower():
            theme = 'budget'
        elif 'food' in keyword.lower() or 'cuisine' in keyword.lower():
            theme = 'food'
        elif 'photo' in keyword.lower() or 'photography' in keyword.lower():
            theme = 'photography'
        else:
            theme = 'travel'
            
        # Filter by identified theme
        for account, description in travel_accounts.items():
            if theme in account.lower() or theme in description.lower():
                filtered_accounts[account] = description
    
    # Sort accounts by relevance (this is a simple algorithm that could be improved)
    sorted_accounts = []
    for account, description in filtered_accounts.items():
        # Calculate a simple relevance score
        score = 0
        for key in keywords:
            # Account name matches are weighted more heavily
            if key in account.lower():
                score += 3
            # Description matches
            if key in description.lower():
                score += 1
        
        sorted_accounts.append((account, score))
    
    # Sort by score (higher is better)
    sorted_accounts.sort(key=lambda x: x[1], reverse=True)
    
    # Return just the account names, limited to max_accounts
    result = [account for account, _ in sorted_accounts[:max_accounts]]
    
    print(f"Found {len(result)} accounts matching '{keyword}'")
    
    return result

# Function to download and process account data
def download_account_data(accounts, posts_per_account=5):
    """
    Download JSON data for each account's posts and aggregate into a dataframe.
    
    Args:
        accounts (list): List of Instagram usernames
        posts_per_account (int): Number of posts to download per account
        
    Returns:
        pd.DataFrame: Dataframe with aggregated account data
    """
    all_posts_data = []
    
    for username in accounts:
        print(f"Downloading data for {username}...")
        try:
            # Instaloader handles rate limiting automatically - no need for manual delays
            
            # Get profile
            profile = instaloader.Profile.from_username(L.context, username)
            print(f"Successfully connected to profile: {username}")
            
            # Create folder for profile data
            profile_dir = f"@{username}_data"
            if not os.path.exists(profile_dir):
                os.makedirs(profile_dir)
            
            # Initialize counter
            post_count = 0
            
            # Iterate through profile posts
            for post in profile.get_posts():
                try:
                    print(f"Processing post {post.shortcode} from {username}...")
                    
                    # Extract relevant data for our summary (without downloading)
                    post_data = {
                        'username': username,
                        'post_id': post.shortcode,
                        'is_video': post.is_video,
                        'likes': post.likes,
                        'comments': post.comments,
                        'views': getattr(post, 'video_view_count', 0) if post.is_video else 0,
                        'caption': post.caption if post.caption else "",
                        'hashtags': ' '.join(post.caption_hashtags) if hasattr(post, 'caption_hashtags') and post.caption_hashtags else "",
                        'timestamp': post.date_local.strftime("%Y-%m-%d %H:%M:%S"),
                        'url': f"https://www.instagram.com/p/{post.shortcode}",
                        'followers': profile.followers,
                        'download': False  # Column for marking which posts to download
                    }
                    
                    # Now try to download the JSON
                    try:
                        # Optional: only download metadata, not the actual post
                        L.download_post(post, target=profile_dir)
                        print(f"Downloaded metadata for post {post.shortcode}")
                    except instaloader.exceptions.ConnectionException as e:
                        if "429" in str(e):
                            print(f"Rate limit reached. Post metadata download paused - will retry automatically.")
                            # Let Instaloader handle the retry with its built-in mechanism
                        else:
                            print(f"Error downloading metadata for post {post.shortcode}: {str(e)}")
                    except Exception as e:
                        print(f"Error downloading metadata for post {post.shortcode}: {str(e)}")
                        # Even if download fails, we still have the basic data
                    
                    all_posts_data.append(post_data)
                    
                    post_count += 1
                    print(f"Added post {post_count}/{posts_per_account} from {username}")
                    
                    if post_count >= posts_per_account:
                        break
                        
                except Exception as e:
                    print(f"Error processing post from {username}: {str(e)}")
            
            print(f"Completed processing {post_count} posts from {username}")
            
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"Profile {username} does not exist or is private")
        except instaloader.exceptions.TooManyRequestsException:
            print(f"Instagram rate limit reached for {username}. Instaloader will handle retries automatically.")
            print(f"Try again later or reduce the number of accounts being processed.")
        except Exception as e:
            print(f"Error downloading data from {username}: {str(e)}")
        
        # No need for additional delay between accounts - Instaloader handles rate limiting
    
    # Convert to dataframe
    if all_posts_data:
        df = pd.DataFrame(all_posts_data)
        return df
    else:
        print("No data collected from accounts")
        return pd.DataFrame()

# Function to download content based on marked items in the sheet
def download_selected_content(csv_file):
    """
    Download content for posts marked in the CSV file.
    
    Args:
        csv_file (str): Path to the CSV file with marked posts
    """
    try:
        # Read the CSV
        df = pd.read_csv(csv_file)
        
        # Filter for posts marked for download
        download_df = df[df['download'] == True]
        
        if download_df.empty:
            print("No posts marked for download")
            return
        
        print(f"Found {len(download_df)} posts marked for download")
        
        # Create downloads directory
        download_dir = "selected_downloads"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        # Download each marked post
        for _, row in download_df.iterrows():
            try:
                username = row['username']
                post_id = row['post_id']
                
                print(f"Downloading post {post_id} from {username}...")
                
                # Get post by shortcode
                post = instaloader.Post.from_shortcode(L.context, post_id)
                
                # Download with pictures and videos
                download_instance = instaloader.Instaloader(
                    download_pictures=True,
                    download_videos=True,
                    download_video_thumbnails=True,
                    download_geotags=True,
                    save_metadata=True
                )
                
                # Download post
                download_instance.download_post(post, target=download_dir)
                
                print(f"Successfully downloaded post {post_id}")
                
                # Add delay to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"Error downloading post {post_id}: {str(e)}")
        
        print(f"Completed downloading selected posts to {download_dir}")
        
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")

# New function to calculate smart recommendation scores
def calculate_smart_recommendation_score(df):
    """
    Calculate a smart recommendation score based on multiple engagement factors.
    
    Args:
        df (pd.DataFrame): Dataframe with post data
        
    Returns:
        pd.DataFrame: Dataframe with added smart recommendation scores
    """
    # Make a copy to avoid warnings
    df = df.copy()
    
    # Ensure numerical columns are numeric
    numeric_cols = ['likes', 'comments', 'views', 'followers']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Basic engagement metrics
    df['engagement_rate'] = ((df['likes'] + df['comments'] * 2) / df['followers'].clip(lower=1) * 100).fillna(0)
    
    # Video-specific metrics
    mask = (df['is_video'] == True) & (df['views'] > 0)
    df['view_to_like_ratio'] = 0
    df.loc[mask, 'view_to_like_ratio'] = (df.loc[mask, 'likes'] / df.loc[mask, 'views'].clip(lower=1) * 100)
    
    # Comment to like ratio (higher is better)
    df['comment_ratio'] = (df['comments'] / (df['likes'] + 1) * 100).fillna(0)
    
    # Content recency score (newer content scores higher)
    if 'timestamp' in df.columns:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            # Calculate days since post
            now = pd.Timestamp.now()
            df['days_since_post'] = ((now - df['timestamp']).dt.total_seconds() / (60 * 60 * 24)).fillna(30)
            # Recent content gets higher scores (max of 100 for posts made today, exponential decay)
            df['recency_score'] = 100 * np.exp(-0.05 * df['days_since_post'])
        except:
            df['recency_score'] = 50  # Default if timestamp conversion fails
    else:
        df['recency_score'] = 50  # Default if no timestamp
    
    # Content type bonus (videos may get a bonus if they perform well)
    df['content_type_score'] = 0
    video_mask = (df['is_video'] == True) & (df['view_to_like_ratio'] > 5)
    df.loc[video_mask, 'content_type_score'] = 20
    
    # Calculate the final smart score
    # Weights can be adjusted based on importance of each factor
    df['smart_score'] = (
        0.35 * df['engagement_rate'] +
        0.20 * df['view_to_like_ratio'] +
        0.15 * df['comment_ratio'] +
        0.15 * df['recency_score'] +
        0.15 * df['content_type_score']
    )
    
    # Normalize to 0-100 scale for easier understanding
    if len(df) > 1:  # Only normalize if we have more than one post
        min_score = df['smart_score'].min()
        max_score = df['smart_score'].max()
        if max_score > min_score:  # Avoid division by zero
            df['smart_score'] = 100 * (df['smart_score'] - min_score) / (max_score - min_score)
        else:
            df['smart_score'] = 50  # If all scores are the same
    
    # Round to 2 decimal places
    df['smart_score'] = df['smart_score'].round(2)
    
    # Add a rank column - use fillna to handle NaN values
    df['rank'] = df['smart_score'].rank(ascending=False, method='min').fillna(0).astype(int)
    
    # Add intelligence indicators
    conditions = [
        df['smart_score'] >= 75,
        df['smart_score'] >= 50,
        df['smart_score'] >= 25
    ]
    choices = ['⭐⭐⭐', '⭐⭐', '⭐']
    df['recommendation'] = np.select(conditions, choices, default='')
    
    return df

# Function to verify if an account is public and accessible
def verify_instagram_account(username):
    """
    Verify if an Instagram account is public and accessible.
    
    Args:
        username (str): Instagram username to verify
        
    Returns:
        tuple: (is_accessible, profile_object or None, error_message or None)
    """
    print(f"Verifying account accessibility: @{username}")
    try:
        # Add delay before verification
        time.sleep(3)
        
        # Try to get profile
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Check if profile is private
        if profile.is_private:
            print(f"@{username} is a private account and cannot be accessed.")
            return (False, None, "Private account")
        
        # Check followers count (optional: to filter very small or very large accounts)
        followers = profile.followers
        print(f"@{username} is public with {followers} followers.")
        
        # Successfully verified
        return (True, profile, None)
        
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"@{username} does not exist.")
        return (False, None, "Profile does not exist")
    
    except instaloader.exceptions.LoginRequiredException:
        print(f"Login required to access @{username}.")
        return (False, None, "Login required")
        
    except Exception as e:
        print(f"Error verifying @{username}: {str(e)}")
        return (False, None, str(e))

# Function to safely download from a single verified profile
def download_from_single_profile(username, posts_limit=5, max_retries=3):
    """
    Safely download data from a single verified Instagram profile.
    Now primarily uses the simpler method based on Instaloader documentation.
    
    Args:
        username (str): Instagram username to download from
        posts_limit (int): Maximum number of posts to download
        max_retries (int): Maximum number of retry attempts for failed requests
        
    Returns:
        pd.DataFrame or None: DataFrame with post data or None if failed
    """
    print(f"Downloading data from profile: {username}")
    
    # Create storage directory
    profile_dir = f"@{username}_data"
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
    
    try:
        # Create a dedicated Instaloader instance for this download
        L_profile = instaloader.Instaloader(
            download_pictures=False,  # Only metadata for analysis
            download_video_thumbnails=False,
            download_videos=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=True,
            compress_json=False
        )
        
        # Get profile
        profile = instaloader.Profile.from_username(L_profile.context, username)
        print(f"Successfully connected to profile: {username}")
        print(f"Profile info: @{username}, Followers: {profile.followers}, Following: {profile.followees}")
        
        # List to store post data
        posts_data = []
        # Initialize counter
        post_count = 0
        
        # Iterate through profile posts using standard method
        for post in profile.get_posts():
            try:
                # Extract basic data
                post_data = {
                    'username': username,
                    'post_id': post.shortcode,
                    'is_video': post.is_video,
                    'likes': post.likes,
                    'comments': post.comments,
                    'views': getattr(post, 'video_view_count', 0) if post.is_video else 0,
                    'caption': post.caption if post.caption else "",
                    'hashtags': ' '.join(post.caption_hashtags) if hasattr(post, 'caption_hashtags') and post.caption_hashtags else "",
                    'timestamp': post.date_local.strftime("%Y-%m-%d %H:%M:%S"),
                    'url': f"https://www.instagram.com/p/{post.shortcode}",
                    'followers': profile.followers,
                    'download': False
                }
                
                # Add to data collection
                posts_data.append(post_data)
                
                # Download the post metadata
                L_profile.download_post(post, target=profile_dir)
                
                post_count += 1
                print(f"Downloaded post {post_count} from {username}")
                
                # No need for manual delay - Instaloader handles rate limiting
                
                # Check if limit reached
                if post_count >= posts_limit:
                    break
                
            except instaloader.exceptions.ConnectionException as e:
                if "429" in str(e):
                    print(f"Instagram rate limit reached. Instaloader will handle this automatically.")
                    # Let Instaloader handle the retry
                else:
                    print(f"Error processing post from {username}: {str(e)}")
            except Exception as e:
                print(f"Error processing post from {username}: {str(e)}")
        
        print(f"Completed downloading {post_count} posts from {username}")
        
        # Create DataFrame if we have data
        if posts_data:
            df = pd.DataFrame(posts_data)
            
            # Save raw data
            csv_path = os.path.join(profile_dir, f"{username}_raw_data.csv")
            df.to_csv(csv_path, index=False)
            print(f"Raw data saved to {csv_path}")
            
            return df
        else:
            print("No posts data collected")
            
            # If standard method fails completely, try simple_profile_download as fallback
            print("Trying simple method as fallback...")
            if simple_profile_download(username, posts_limit):
                print(f"Successfully downloaded {username} using simple fallback method")
                return pd.DataFrame({'username': [username], 'success': [True]})
            return None
        
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Profile {username} does not exist or is private")
        return None
    except instaloader.exceptions.LoginRequiredException:
        print(f"Login required for {username}, trying simple method instead...")
        # Try the simple method as fallback for login required
        if simple_profile_download(username, posts_limit):
            print(f"Successfully downloaded {username} using simple method")
            return pd.DataFrame({'username': [username], 'success': [True]})
        return None
    except instaloader.exceptions.TooManyRequestsException:
        print(f"Instagram rate limit reached for {username}. Instaloader will handle retries automatically.")
        print(f"Trying simple method as alternative...")
        # Try the simple method as fallback for rate limiting
        if simple_profile_download(username, posts_limit):
            print(f"Successfully downloaded {username} using simple method")
            return pd.DataFrame({'username': [username], 'success': [True]})
        return None
    except Exception as e:
        print(f"Error downloading data from {username}: {str(e)}")
        print("Trying simple method as fallback...")
        # Try the simple method as fallback for other errors
        if simple_profile_download(username, posts_limit):
            print(f"Successfully downloaded {username} using simple method")
            return pd.DataFrame({'username': [username], 'success': [True]})
        return None

# Function to download multiple profiles using the working approach
def download_from_multiple_profiles(profile_list, posts_per_profile=3):
    """
    Download data from multiple profiles using the approach from get_profile_reels.
    
    Args:
        profile_list (list): List of Instagram usernames to download from
        posts_per_profile (int): Number of posts to download per profile
        
    Returns:
        pd.DataFrame: Combined dataframe with all posts data
    """
    all_data = []
    
    for username in profile_list:
        df = download_from_single_profile(username, posts_limit=posts_per_profile)
        if df is not None and not df.empty:
            all_data.append(df)
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"Collected data from {len(all_data)} profiles, total {len(combined_df)} posts")
        return combined_df
    else:
        print("No data collected from any profiles")
        return pd.DataFrame()

# Function to maintain a list of verified public accounts
def manage_account_list(action='load', accounts_to_add=None, filename='verified_accounts.txt'):
    """
    Manage a list of verified public Instagram accounts.
    
    Args:
        action (str): 'load', 'save', 'add', or 'verify'
        accounts_to_add (list): List of accounts to add when action='add'
        filename (str): File to store the accounts
        
    Returns:
        list: Current list of verified accounts
    """
    verified_accounts = []
    
    # Load existing accounts
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            verified_accounts = [line.strip() for line in f.readlines() if line.strip()]
    
    if action == 'load':
        print(f"Loaded {len(verified_accounts)} verified accounts")
        return verified_accounts
        
    elif action == 'add' and accounts_to_add:
        # Add new accounts to list
        for account in accounts_to_add:
            if account not in verified_accounts:
                verified_accounts.append(account)
                
        # Save updated list
        with open(filename, 'w') as f:
            for account in verified_accounts:
                f.write(f"{account}\n")
                
        print(f"Added {len(accounts_to_add)} accounts to verified list")
        print(f"Total verified accounts: {len(verified_accounts)}")
        return verified_accounts
        
    elif action == 'verify':
        # Verify each account in the list
        verified = []
        for account in verified_accounts:
            # Try the simple verification method first
            try:
                # Create a temporary Instaloader instance
                temp_loader = instaloader.Instaloader()
                
                # Get profile
                profile = instaloader.Profile.from_username(temp_loader.context, account)
                
                # Check if profile is private
                if profile.is_private:
                    print(f"@{account} is a private account and cannot be accessed.")
                else:
                    print(f"@{account} is public with {profile.followers} followers.")
                    verified.append(account)
                    
            except Exception as e:
                print(f"Error verifying @{account}: {str(e)}")
            
            # Add delay between verifications
            time.sleep(3)
            
        # Update the file with only verified accounts
        with open(filename, 'w') as f:
            for account in verified:
                f.write(f"{account}\n")
                
        print(f"Verified {len(verified)} out of {len(verified_accounts)} accounts")
        return verified
        
    return verified_accounts

# Function to analyze data from all processed accounts
def analyze_collected_data(keyword):
    """
    Analyze all collected data from verified accounts.
    Priority on JSON files rather than CSV files.
    
    Args:
        keyword (str): Keyword for the analysis
        
    Returns:
        pd.DataFrame: Combined and analyzed data
    """
    print(f"Analyzing collected data for keyword: {keyword}")
    print("Prioritizing JSON files for analysis...")
    
    # Search patterns to look in
    dir_patterns = [
        '@*_verified_data',  # Old download_from_single_profile
        '@*_data',           # New download_from_single_profile
        '@profile_reels',    # get_profile_reels
        '#*',                # get_it (hashtag downloads)
        '#*_reels'           # get_reels (hashtag reels)
    ]
    
    # Look for JSON files first
    json_files = []
    for dir_pattern in dir_patterns:
        for dir_name in glob.glob(dir_pattern):
            if os.path.isdir(dir_name):
                print(f"Checking directory: {dir_name}")
                json_pattern = os.path.join(dir_name, "*.json")
                matching_jsons = glob.glob(json_pattern)
                if matching_jsons:
                    json_files.extend(matching_jsons)
                    print(f"  Found {len(matching_jsons)} JSON files in {dir_name}")
    
    print(f"Found {len(json_files)} JSON files to analyze")
    
    if not json_files:
        print("No JSON files found for analysis")
        print("TIP: Try using the demo mode (option 4) to see the analysis in action with sample data")
        print("     or run option 7 to analyze existing JSON files in specific folders")
        return None
    
    # Process JSON files
    json_data = []
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Determine the structure of the JSON (instaloader vs. direct API)
                if 'instaloader' in data:
                    # This is an instaloader-formatted JSON
                    node = data.get('node', {})
                    owner = node.get('owner', {})
                    
                    # Extract basic data from the instaloader format
                    extracted_data = {
                        'username': owner.get('username', data.get('username', 'unknown')),
                        'post_id': node.get('shortcode', data.get('shortcode', '')),
                        'is_video': node.get('is_video', data.get('is_video', False)),
                        'likes': node.get('edge_media_preview_like', {}).get('count', 
                                node.get('likes', data.get('likes', 0))),
                        'comments': node.get('edge_media_to_comment', {}).get('count', 
                                  node.get('comments', data.get('comments', 0))),
                        'views': node.get('video_view_count', 
                                node.get('video_view_count', 0)) if node.get('is_video', False) else 0,
                        'caption': node.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', 
                                 node.get('caption', data.get('caption', ''))),
                        'hashtags': ' '.join(data.get('caption_hashtags', [])) if 'caption_hashtags' in data else '',
                        'timestamp': node.get('taken_at_timestamp', 
                                   data.get('date_utc', data.get('timestamp', ''))),
                        'url': f"https://www.instagram.com/p/{node.get('shortcode', '')}",
                        'followers': owner.get('edge_followed_by', {}).get('count', 
                                   owner.get('followers', data.get('followers', 0))),
                        'download': False
                    }
                else:
                    # Direct API format or other format
                    extracted_data = {
                        'username': data.get('owner', {}).get('username', data.get('username', 'unknown')),
                        'post_id': data.get('shortcode', ''),
                        'is_video': data.get('is_video', False),
                        'likes': data.get('likes', 0),
                        'comments': data.get('comments', 0),
                        'views': data.get('video_view_count', 0) if data.get('is_video', False) else 0,
                        'caption': data.get('caption', ''),
                        'hashtags': ' '.join(data.get('caption_hashtags', [])) if 'caption_hashtags' in data else '',
                        'timestamp': data.get('date_local', data.get('timestamp', '')),
                        'url': f"https://www.instagram.com/p/{data.get('shortcode', '')}",
                        'followers': data.get('owner', {}).get('followers', 0),
                        'download': False
                    }
                
                # Print some key stats to verify
                print(f"Processed JSON: {file}")
                print(f"  Username: {extracted_data['username']}, Post ID: {extracted_data['post_id']}")
                print(f"  Likes: {extracted_data['likes']}, Comments: {extracted_data['comments']}")
                
                json_data.append(extracted_data)
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
    
    # Create dataframe from JSON data
    if not json_data:
        print("No valid data extracted from JSON files")
        return None
    
    combined_df = pd.DataFrame(json_data)
    print(f"Combined data contains {len(combined_df)} posts from {combined_df['username'].nunique()} accounts")
    
    # Calculate smart recommendation scores
    print("Calculating smart recommendation scores...")
    scored_df = calculate_smart_recommendation_score(combined_df)
    
    # Sort by smart score
    scored_df = scored_df.sort_values('smart_score', ascending=False)
    
    # Save combined analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"{keyword}_json_analysis_{timestamp}.csv"
    scored_df.to_csv(csv_filename, index=False)
    print(f"Analysis saved to {csv_filename}")
    
    return scored_df

# Main function for the new workflow
def instagram_content_automation(keyword, max_accounts=10, posts_per_account=5):
    """
    Main function to:
    1. Search for Instagram accounts based on a keyword
    2. Download JSON data for each account
    3. Aggregate the data into a sheet format
    4. Generate a CSV file that can be imported to Google Sheets
    5. Allow downloading selected content
    
    Args:
        keyword (str): Keyword to search for
        max_accounts (int): Maximum number of accounts to search
        posts_per_account (int): Number of posts to analyze per account
    """
    print(f"Starting Instagram content automation for keyword: '{keyword}'")
    
    # 1. Search for accounts
    accounts = search_instagram_accounts(keyword, max_accounts)
    
    if not accounts:
        print("No accounts found. Try a different keyword.")
        return
    
    # 2 & 3. Download and aggregate account data
    posts_data = download_account_data(accounts, posts_per_account)
    
    if posts_data.empty:
        print("No post data collected. Try again with different parameters.")
        return
    
    # 3.5 Calculate smart recommendation scores
    print("Calculating smart recommendation scores...")
    posts_data = calculate_smart_recommendation_score(posts_data)
    
    # Sort by smart score (highest first)
    posts_data = posts_data.sort_values('smart_score', ascending=False)
    
    # 4. Generate CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"{keyword}_content_{timestamp}.csv"
    posts_data.to_csv(csv_filename, index=False)
    
    print(f"\nContent data saved to {csv_filename}")
    print(f"Number of accounts analyzed: {len(accounts)}")
    print(f"Total posts collected: {len(posts_data)}")
    
    # Display top 5 recommended posts
    if len(posts_data) > 0:
        print("\nTOP 5 RECOMMENDED CONTENT:")
        top_posts = posts_data.head(5)
        for i, row in top_posts.iterrows():
            print(f"{row['rank']}. {row['recommendation']} @{row['username']} - Score: {row['smart_score']} - {row['url']}")
    
    print(f"\nINSTRUCTIONS:")
    print(f"1. Import {csv_filename} into Google Sheets")
    print(f"2. Review the content (sorted by smart score) and mark 'True' in the 'download' column for posts you want to download")
    print(f"3. Export from Google Sheets back to CSV with the same filename")
    print(f"4. Run the download_selected_content('{csv_filename}') function to download marked content")
    
    return posts_data, csv_filename

# Main function to run the entire process
def run_instagram_analysis(keyword, num_files):
    print(f"Downloading {num_files} posts with hashtag #{keyword}...")
    get_it(keyword, num_files)
    
    print(f"Downloading {num_files} reels with hashtag #{keyword}...")
    get_reels(keyword, num_files)

    print(f"Downloading {num_files} reels with profiles...")
    profiles = ['a.corporate.nomad','bengaluru__trekkers','nammatrip']
    get_profile_reels(profiles, limit=3)  


    print(f"Processing JSON files for #{keyword}...")
    df = process_json_to_dataframe(keyword)
    
    print("Calculating engagement metrics...")
    df = calculate_engagement(df)
    
    # Save to CSV with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"{keyword}_{num_files}_{timestamp}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Analysis complete! Results saved to {csv_filename}")
    
    # Return top 5 posts by engagement score
    if len(df) > 0:
        print("\nTop 5 posts by engagement score:")
        top_posts = df.sort_values('engagement_score', ascending=False).head(5)
        return top_posts
    else:
        print("No posts found!")
        return None

# Run the analysis with sample data
if __name__ == "__main__":
    keyword = "travel experiences"
    
    # Import necessary libraries
    import numpy as np
    import random
    
    print("Instagram Content Automation - Multi-Account Approach")
    print("-----------------------------------------------------")
    
    # Get user input for mode
    mode = input("Select mode (1=Verify account, 2=Download from account, 3=Analyze collected data, 4=Process verified accounts list, 5=Search for accounts, 6=Download using profile_reels approach, 7=Analyze existing JSON files): ")
    
    if mode == "1":
        # Verify an account
        username = input("Enter Instagram username to verify: ")
        is_accessible, profile, error = verify_instagram_account(username)
        if is_accessible:
            print(f"@{username} is verified and accessible!")
            # Add to verified accounts list
            manage_account_list(action='add', accounts_to_add=[username])
        else:
            print(f"@{username} verification failed: {error}")
    
    elif mode == "2":
        # Download data from a verified account
        username = input("Enter Instagram username to download from: ")
        posts_limit = int(input("How many posts to download (recommended 1-5): "))
        
        df = download_from_single_profile(username, posts_limit=posts_limit)
        
        if df is not None and not df.empty:
            print(f"Successfully downloaded data from @{username}")
            print(f"Collected {len(df)} posts")
        else:
            print(f"Failed to download data from @{username}")
    
    elif mode == "3":
        # Analyze all collected data
        analyzed_df = analyze_collected_data(keyword)
        
        if analyzed_df is not None and not analyzed_df.empty:
            # Display top 5 recommended posts
            print("\nTOP 5 RECOMMENDED CONTENT:")
            top_posts = analyzed_df.head(5)
            for i, row in top_posts.iterrows():
                print(f"{row['rank']}. {row['recommendation']} @{row['username']} - Score: {row['smart_score']} - {row['url']}")
        else:
            print("No data available for analysis. Please download data from accounts first.")
    
    elif mode == "4":
        # Process all verified accounts from the file
        print("\nProcessing all accounts from verified_accounts.txt")
        
        # Load verified accounts list
        accounts = manage_account_list(action='load')
        
        if not accounts:
            print("No verified accounts found in verified_accounts.txt")
            print("Use mode 1 to verify and add accounts, or mode 5 to search for accounts")
        else:
            print(f"Found {len(accounts)} verified accounts")
            
            # Get number of posts per account and maximum accounts to process
            try:
                posts_per_account = int(input("Enter number of posts to download per account (1-3 recommended): "))
                posts_per_account = max(1, min(posts_per_account, 5))  # Limit between 1-5
            except:
                posts_per_account = 1
                print("Using 1 post per account")
                
            try:
                max_accounts = int(input("Enter maximum number of accounts to process (0 for all): "))
                if max_accounts <= 0:
                    max_accounts = len(accounts)
            except:
                max_accounts = len(accounts)
                print(f"Processing all {max_accounts} accounts")
                
            # Process accounts in batches
            batch_size = 5
            processed_count = 0
            all_data = []
            
            # Select random sample of accounts if max_accounts < total accounts
            if max_accounts < len(accounts):
                selected_accounts = random.sample(accounts, max_accounts)
                print(f"Randomly selected {max_accounts} accounts from {len(accounts)} total")
            else:
                selected_accounts = accounts
            
            # Process in batches
            for i in range(0, len(selected_accounts), batch_size):
                batch = selected_accounts[i:i+batch_size]
                print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} accounts)")
                
                for username in batch:
                    print(f"\nProcessing account: @{username}")
                    df = download_from_single_profile(username, posts_limit=posts_per_account)
                    
                    if df is not None and not df.empty:
                        all_data.append(df)
                        processed_count += 1
                        print(f"Successfully collected {len(df)} posts from @{username}")
                    else:
                        print(f"Failed to collect data from @{username}")
                    
                    # No need for manual delay - Instaloader handles rate limiting
                
                # Still keep a shorter pause between batches for better user experience
                # but let the user know it's just for UX, not for rate limiting
                if i + batch_size < len(selected_accounts):
                    batch_pause = 5
                    print(f"\nCompleted batch {i//batch_size + 1}. Taking a short {batch_pause} second pause before next batch...")
                    print("(This is just a user interface pause, Instaloader handles actual API rate limiting)")
                    time.sleep(batch_pause)
            
            print(f"\nCompleted processing {processed_count} accounts")
            
            # Combine all data if available
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                print(f"Combined data contains {len(combined_df)} posts from {combined_df['username'].nunique()} accounts")
                
                # Calculate smart recommendation scores
                print("\nCalculating smart recommendation scores...")
                scored_df = calculate_smart_recommendation_score(combined_df)
                
                # Sort by smart score
                scored_df = scored_df.sort_values('smart_score', ascending=False)
                
                # Save combined analysis
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"verified_accounts_analysis_{timestamp}.csv"
                scored_df.to_csv(csv_filename, index=False)
                print(f"Analysis saved to {csv_filename}")
                
                # Display top posts
                top_count = min(5, len(scored_df))
                if top_count > 0:
                    print(f"\nTOP {top_count} RECOMMENDED CONTENT:")
                    top_df = scored_df.head(top_count)
                    for i, row in top_df.iterrows():
                        print(f"{row['rank']}. {row['recommendation']} @{row['username']} - Score: {row['smart_score']} - {row['url']}")
            else:
                print("No data collected from any accounts")
    
    elif mode == "5":
        # Search for accounts using keywords
        search_keyword = input("Enter keyword to search for Instagram accounts: ")
        max_accounts = int(input("Maximum number of accounts to find (recommended 5-10): "))
        
        print(f"\nSearching for Instagram accounts related to '{search_keyword}'...")
        print("This may take a while and might be blocked by Instagram. Please be patient.")
        
        # Try to find accounts
        try:
            accounts = search_instagram_accounts(search_keyword, max_accounts)
            
            if accounts and len(accounts) > 0:
                print(f"\nFound {len(accounts)} accounts related to '{search_keyword}':")
                for i, account in enumerate(accounts, 1):
                    print(f"{i}. @{account}")
                
                # Option to verify and save these accounts
                save_option = input("\nWould you like to verify and save these accounts? (y/n): ")
                if save_option.lower() == 'y':
                    # Verify each account
                    verified_accounts = []
                    for account in accounts:
                        is_accessible, _, _ = verify_instagram_account(account)
                        if is_accessible:
                            verified_accounts.append(account)
                        time.sleep(3)  # Add delay between verifications
                    
                    # Save verified accounts
                    if verified_accounts:
                        manage_account_list(action='add', accounts_to_add=verified_accounts)
                        print(f"Added {len(verified_accounts)} verified accounts to your list.")
                    else:
                        print("No accounts were verified successfully.")
            else:
                print(f"No accounts found for keyword '{search_keyword}'.")
                print("Instagram may be blocking automated searches. Try a different keyword or try again later.")
        
        except Exception as e:
            print(f"Error searching for accounts: {str(e)}")
            print("Instagram may be blocking automated searches. Try again later.")
    
    elif mode == "6":
        # Download using profile_reels approach
        print("\nDownloading using the get_profile_reels approach (which is working)")
        print("This method uses the same approach as the working get_profile_reels function")
        
        # Get list of accounts to download from
        use_predefined = input("Use verified accounts list? (y/n): ")
        
        if use_predefined.lower() == 'y':
            accounts = manage_account_list(action='load')
            
            if accounts and len(accounts) > 0:
                print(f"\nFound {len(accounts)} accounts in verified_accounts.txt")
                
                # Select which accounts to use
                selection = input("Enter account numbers to download from (comma-separated, e.g. 1,3,5) or 'all' or 'random': ")
                
                if selection.lower() == 'all':
                    selected_accounts = accounts
                elif selection.lower() == 'random':
                    num_accounts = min(3, len(accounts))
                    try:
                        num_accounts = int(input(f"How many random accounts to use (max {len(accounts)}): "))
                        num_accounts = min(num_accounts, len(accounts))
                    except:
                        pass
                    selected_accounts = random.sample(accounts, num_accounts)
                else:
                    try:
                        indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                        selected_accounts = [accounts[idx] for idx in indices if 0 <= idx < len(accounts)]
                    except:
                        print("Invalid selection. Using first 3 accounts.")
                        selected_accounts = accounts[:min(3, len(accounts))]
            else:
                print("No accounts found in verified_accounts.txt. Using default accounts.")
                selected_accounts = accounts[:min(3, len(accounts))]
        else:
            # Manual input
            accounts_input = input("Enter Instagram accounts to download from (comma-separated): ")
            selected_accounts = [acc.strip() for acc in accounts_input.split(',')]
        
        # Get number of posts per account
        try:
            posts_per_account = int(input("How many posts to download per account (1-3 recommended): "))
            posts_per_account = min(max(1, posts_per_account), 5)  # Limit between 1-5
        except:
            posts_per_account = 1
            print("Using 1 post per account")
        
        print(f"\nDownloading from {len(selected_accounts)} accounts: {', '.join(selected_accounts)}")
        print(f"Posts per account: {posts_per_account}")
        
        # Download from selected accounts
        combined_df = download_from_multiple_profiles(selected_accounts, posts_per_profile=posts_per_account)
        
        if not combined_df.empty:
            # Calculate smart recommendation scores
            print("\nCalculating smart recommendation scores...")
            scored_df = calculate_smart_recommendation_score(combined_df)
            
            # Sort by smart score
            scored_df = scored_df.sort_values('smart_score', ascending=False)
            
            # Save combined analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{keyword}_profile_reels_approach_{timestamp}.csv"
            scored_df.to_csv(csv_filename, index=False)
            print(f"Analysis saved to {csv_filename}")
            
            # Display top 5 recommended posts
            print("\nTOP 5 RECOMMENDED CONTENT:")
            top_posts = scored_df.head(5)
            for i, row in top_posts.iterrows():
                print(f"{row['rank']}. {row['recommendation']} @{row['username']} - Score: {row['smart_score']} - {row['url']}")
        else:
            print("No data collected. Try again with different accounts or fewer posts.")
    
    elif mode == "7":
        # Analyze existing JSON files without making any API calls
        print("\nAnalyzing existing JSON files without making any Instagram API calls")
        print("This is useful if you've previously downloaded content and just want to analyze it")
        
        folder_path = input("Enter path to folder containing JSON files (or press Enter for current directory): ")
        if not folder_path:
            folder_path = "."
        
        # Find all JSON files in the given directory and its subdirectories
        json_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".json"):
                    json_files.append(os.path.join(root, file))
        
        if not json_files:
            print(f"No JSON files found in {folder_path}")
            print("Please make sure you have previously downloaded Instagram content")
        else:
            print(f"Found {len(json_files)} JSON files")
            
            # Process JSON files
            all_data = []
            for file in json_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Determine the structure of the JSON (instaloader vs. direct API)
                        if 'instaloader' in data:
                            # This is an instaloader-formatted JSON
                            node = data.get('node', {})
                            owner = node.get('owner', {})
                            
                            # Extract important data from the instaloader format
                            extracted_data = {
                                'username': owner.get('username', data.get('username', 'unknown')),
                                'post_id': node.get('shortcode', data.get('shortcode', '')),
                                'is_video': node.get('is_video', data.get('is_video', False)),
                                'likes': node.get('edge_media_preview_like', {}).get('count', 
                                        node.get('likes', data.get('likes', 0))),
                                'comments': node.get('edge_media_to_comment', {}).get('count', 
                                          node.get('comments', data.get('comments', 0))),
                                'views': node.get('video_view_count', 
                                        node.get('video_view_count', 0)) if node.get('is_video', False) else 0,
                                'caption': node.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', 
                                         node.get('caption', data.get('caption', ''))),
                                'hashtags': ' '.join(data.get('caption_hashtags', [])) if 'caption_hashtags' in data else '',
                                'timestamp': node.get('taken_at_timestamp', 
                                           data.get('date_utc', data.get('timestamp', ''))),
                                'url': f"https://www.instagram.com/p/{node.get('shortcode', '')}",
                                'followers': owner.get('edge_followed_by', {}).get('count', 
                                           owner.get('followers', data.get('followers', 0))),
                                'download': False
                            }
                        else:
                            # Direct API format or other format
                            extracted_data = {
                                'username': data.get('owner', {}).get('username', data.get('username', 'unknown')),
                                'post_id': data.get('shortcode', ''),
                                'is_video': data.get('is_video', False),
                                'likes': data.get('likes', 0),
                                'comments': data.get('comments', 0),
                                'views': data.get('video_view_count', 0) if data.get('is_video', False) else 0,
                                'caption': data.get('caption', ''),
                                'hashtags': ' '.join(data.get('caption_hashtags', [])) if 'caption_hashtags' in data else '',
                                'timestamp': data.get('date_local', data.get('timestamp', '')),
                                'url': f"https://www.instagram.com/p/{data.get('shortcode', '')}",
                                'followers': data.get('owner', {}).get('followers', 0),
                                'download': False
                            }
                        
                        all_data.append(extracted_data)
                        print(f"Processed {file}")
                except Exception as e:
                    print(f"Error processing {file}: {str(e)}")
            
            if all_data:
                # Convert to dataframe
                df = pd.DataFrame(all_data)
                
                # Calculate smart recommendation scores
                print("\nCalculating smart recommendation scores...")
                scored_df = calculate_smart_recommendation_score(df)
                
                # Sort by smart score
                scored_df = scored_df.sort_values('smart_score', ascending=False)
                
                # Save analysis
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"{keyword}_json_analysis_{timestamp}.csv"
                scored_df.to_csv(csv_filename, index=False)
                print(f"Analysis saved to {csv_filename}")
                
                # Display top posts
                top_posts = min(len(scored_df), 5)
                if top_posts > 0:
                    print(f"\nTOP {top_posts} RECOMMENDED CONTENT:")
                    top_df = scored_df.head(top_posts)
                    for i, row in top_df.iterrows():
                        print(f"{row['rank']}. {row['recommendation']} @{row['username']} - Score: {row['smart_score']} - {row['url']}")
                else:
                    print("No content to recommend")
            else:
                print("No valid data extracted from JSON files")
    
    else:
        print("Invalid mode selected. Please run again and select a valid option.")




