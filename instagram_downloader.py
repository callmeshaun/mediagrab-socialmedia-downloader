import os
import re
import tempfile
import logging
import instaloader
import urllib.parse
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the instaloader instance
L = instaloader.Instaloader()

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
                
                # Download the post to the temporary directory
                L.download_post(post, target=temp_dir)
                
                # Find the downloaded file
                downloaded_files = list(Path(temp_dir).glob(f'*{shortcode}*.{file_extension}'))
                
                if not downloaded_files:
                    return {
                        'success': False,
                        'error': f'Failed to download the {media_type}.'
                    }
                
                downloaded_file = str(downloaded_files[0])
                
                # For simplicity, we'll use the direct URL
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
                logger.error(f"Instaloader error: {str(e)}")
                return {
                    'success': False,
                    'error': f'Instagram error: {str(e)}'
                }
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }
