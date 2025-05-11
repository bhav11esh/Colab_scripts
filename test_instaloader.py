#!/usr/bin/env python3
"""
Test script for Instaloader - simple profile download without login
Based on https://instaloader.github.io/ documentation
"""

import instaloader
import os
import time
import sys

def simple_profile_download(username, posts_limit=3):
    """Simple profile downloader following instaloader documentation"""
    
    try:
        print(f"Attempting to download profile: {username}")
        
        # Create folder for profile
        profile_dir = f"@{username}_test"
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
            
        # Create a separate Instaloader instance for this download
        L = instaloader.Instaloader(
            download_pictures=True,
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
        profile = instaloader.Profile.from_username(L.context, username)
        print(f"Found profile: {profile.username} with {profile.mediacount} posts")
        
        # Download recent posts (with limit)
        count = 0
        for post in profile.get_posts():
            try:
                L.download_post(post, target=profile_dir)
                count += 1
                print(f"Downloaded post {count}/{posts_limit} from {username}")
                
                if count >= posts_limit:
                    break
                    
                # No need for manual delay - Instaloader handles rate limiting automatically
                    
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
        print(f"Instagram rate limit reached for {username}. Instaloader will automatically retry.")
        print(f"This can happen when too many requests are made in a short time period.")
        return False
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Profile {username} does not exist or is private.")
        return False
    except instaloader.exceptions.LoginRequiredException:
        print(f"Instagram requires login to access this profile. Try a more public profile.")
        return False
    except Exception as e:
        print(f"Error downloading profile {username}: {str(e)}")
        return False

if __name__ == "__main__":
    # Get username from command line or use default
    username = sys.argv[1] if len(sys.argv) > 1 else "natgeo"
    
    # Try to download
    print(f"Testing Instaloader with username: {username}")
    print(f"Note: Instaloader automatically handles rate limiting - no need for manual delays")
    
    success = simple_profile_download(username, posts_limit=2)
    
    if success:
        print(f"✅ Successfully downloaded from {username} without login!")
    else:
        print(f"❌ Failed to download from {username}. Try another public profile.") 