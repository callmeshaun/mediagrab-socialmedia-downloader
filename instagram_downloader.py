import os
import re
import tempfile
import logging
import instaloader
import urllib.parse
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the instaloader instance
L = instaloader.Instaloader(download_videos=True, 
                           download_video_thumbnails=False,
                           download_geotags=False,
                           download_comments=False,
                           save_metadata=False,
                           post_metadata_txt_pattern='')

def is_valid_instagram_url(url):
    """Check if the URL is a valid Instagram post or reel URL."""
    # Basic validation of Instagram URLs
    instagram_pattern = r'^https?://(www\.)?instagram\.com/(p|reel|reels)/[^/]+/?.*$'
    return bool(re.match(instagram_pattern, url))

def extract_shortcode_from_url(url):
    """Extract the shortcode from an Instagram URL."""
    parsed_url = urllib.parse.urlparse(url)
    path_segments = parsed_url.path.strip('/').split('/')
    
    # Handle different URL formats (post, reel, etc.)
    if len(path_segments) >= 2 and path_segments[0] in ['p', 'reel', 'reels']:
        return path_segments[1]
    
    return None

def download_instagram_content(url):
    """
    Download Instagram content from URL.
    Returns a dictionary with the result information.
    """
    try:
        # Extract the shortcode from the URL
        shortcode = extract_shortcode_from_url(url)
        if not shortcode:
            return {
                'success': False,
                'error': 'Invalid Instagram URL format. Could not extract post ID.'
            }
        
        logger.debug(f"Extracted shortcode: {shortcode}")
        
        # Create a temporary directory to store the downloaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Get the post
                post = instaloader.Post.from_shortcode(L.context, shortcode)
                
                # Determine the type of content (image or video)
                is_video = post.is_video
                
                # Get the download URL
                if is_video:
                    media_url = post.video_url
                    media_type = 'video'
                    file_extension = 'mp4'
                else:
                    media_url = post.url
                    media_type = 'image'
                    file_extension = 'jpg'
                
                # For images, we can try to download directly from the URL if instaloader fails
                downloaded_file = None
                try:
                    # First try to use instaloader to download the post
                    L.download_post(post, target=temp_dir)
                    
                    # Find the downloaded file
                    pattern = f'*{shortcode}*.{file_extension}'
                    downloaded_files = list(Path(temp_dir).glob(pattern))
                    
                    if downloaded_files:
                        downloaded_file = str(downloaded_files[0])
                    else:
                        logger.warning(f"Instaloader did not download files that match pattern: {pattern}")
                        # List all files in the temp directory for debugging
                        all_files = list(Path(temp_dir).glob('*'))
                        logger.debug(f"Files in temp directory: {all_files}")
                
                except Exception as e:
                    logger.error(f"Error with instaloader download: {str(e)}")
                
                # If instaloader failed to download, try direct download
                if not downloaded_file:
                    logger.info(f"Attempting direct download from {media_url}")
                    try:
                        response = requests.get(media_url, stream=True, timeout=10)
                        if response.status_code == 200:
                            direct_path = os.path.join(temp_dir, f"instagram_{shortcode}.{file_extension}")
                            with open(direct_path, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            downloaded_file = direct_path
                            logger.info(f"Direct download successful: {downloaded_file}")
                        else:
                            logger.error(f"Failed to download directly: {response.status_code}")
                    except Exception as e:
                        logger.error(f"Error with direct download: {str(e)}")
                
                if not downloaded_file:
                    return {
                        'success': False,
                        'error': f'Failed to download the {media_type}. Please try again later.'
                    }
                
                # For simplicity, we'll still provide the direct URL for preview
                return {
                    'success': True,
                    'media_type': media_type,
                    'media_url': media_url,
                    'username': post.owner_username,
                    'caption': post.caption if post.caption else '',
                    'shortcode': shortcode,
                    'file_path': downloaded_file
                }
                
            except instaloader.exceptions.InstaloaderException as e:
                error_msg = str(e)
                if "401 Unauthorized" in error_msg and "Please wait" in error_msg:
                    logger.error("Rate limit reached. Please wait a few minutes before trying again.")
                    return {
                        'success': False,
                        'error': 'Instagram rate limit reached. Please wait a few minutes before trying again.'
                    }
                else:
                    logger.error(f"Instaloader error: {error_msg}")
                    return {
                        'success': False,
                        'error': f'Instagram error: {error_msg}'
                    }
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }
