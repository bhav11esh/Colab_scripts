# Instagram Content Automation

A script for automated Instagram content analysis, download, and engagement scoring.

## Features

- Download content from public Instagram profiles without requiring login
- Analyze engagement metrics for multiple accounts
- Calculate smart recommendation scores based on likes, comments, views, followers, and content recency
- Process verified accounts in batches with smart error handling
- Analyze Instagram content from JSON files even when API access is limited
- Work with Instagram's rate limiting for reliable operation

## About Rate Limiting

This script leverages Instaloader's built-in rate limiting mechanisms:

- **Automatic Rate Control**: Instaloader automatically implements rate limiting to respect Instagram's API limits by tracking requests and deferring subsequent ones.
- **Retry Mechanism**: When a request is denied due to rate limiting (429 error), Instaloader will automatically retry after the temporary ban expires.
- **No Manual Delays Needed**: Manual sleep/delay calls between requests are unnecessary as Instaloader handles the timing internally.
- **Smart Fallbacks**: When rate limits are hit, the script will try alternative download methods.

## Usage

The script offers multiple operation modes:

1. **Verify Account**: Check if an Instagram account is accessible
2. **Download from Account**: Download content from a specific account
3. **Analyze Collected Data**: Analyze previously downloaded content
4. **Process Verified Accounts**: Batch process accounts from verified_accounts.txt
5. **Search for Accounts**: Find Instagram accounts based on keywords
6. **Download using Profile Reels Approach**: Alternative download method
7. **Analyze Existing JSON Files**: Process already downloaded JSON files

## Getting Started

1. Install requirements:
   ```
   pip install git+https://github.com/SamuMazzi/instaloader.git pandas
   ```

2. Run the script:
   ```
   python "Insta Content Automation.py"
   ```

3. Select a mode and follow the prompts

## Error Handling

The script handles various Instagram API errors:

- **429 Too Many Requests**: Handled by Instaloader's built-in rate limiting
- **404 Not Found**: Profile might no longer exist or changed username
- **403 Forbidden**: May require login or temporary restriction
- **401 Unauthorized**: Likely requires authentication

## Tips for Best Results

- Start with a small number of profiles and posts per profile
- Use verified public accounts with significant follower counts
- Be patient with rate limiting - Instaloader will handle retries automatically
- If a profile fails, try another one rather than retrying the same profile
- Use option 7 to analyze existing JSON files when direct downloads aren't possible

## Test Script

Use `test_instaloader.py` to verify that basic Instaloader functionality works with your account:

```
python test_instaloader.py natgeo
```

Replace `natgeo` with any public Instagram profile. 