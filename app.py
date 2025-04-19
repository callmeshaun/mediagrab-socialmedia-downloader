import os
import logging
import shutil
import requests
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash, session
from werkzeug.middleware.proxy_fix import ProxyFix
from instagram_downloader import download_instagram_content, is_valid_instagram_url

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Create downloads folder if it doesn't exist
DOWNLOAD_FOLDER = os.path.join(app.root_path, 'downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET'])
def index():
    """Render the main page of the application."""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """Process Instagram URL and attempt to download content."""
    instagram_url = request.form.get('instagram_url', '')
    
    if not instagram_url:
        flash('Please enter an Instagram URL', 'danger')
        return redirect(url_for('index'))
    
    if not is_valid_instagram_url(instagram_url):
        flash('Invalid Instagram URL. Please enter a valid Instagram post or reel URL.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Attempt to download content
        result = download_instagram_content(instagram_url)
        
        if result['success']:
            # If we have a file path, save it to our downloads folder
            if 'file_path' in result and os.path.exists(result['file_path']):
                # Create a filename
                shortcode = result['shortcode']
                file_extension = 'mp4' if result['media_type'] == 'video' else 'jpg'
                filename = f"instagram_{shortcode}.{file_extension}"
                
                # Set destination path
                dest_path = os.path.join(DOWNLOAD_FOLDER, filename)
                
                # Copy the file to our download folder
                shutil.copy2(result['file_path'], dest_path)
                
                # Update the result with our local file path
                result['local_file_path'] = dest_path
                result['download_filename'] = filename
            
            # Store the result in session for display
            session['download_result'] = result
            flash('Content successfully retrieved!', 'success')
        else:
            flash(f"Error: {result['error']}", 'danger')
            
        return redirect(url_for('index'))
    
    except Exception as e:
        logging.error(f"Download error: {str(e)}")
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('index'))

@app.route('/download_file/<filename>')
def download_file(filename):
    """Serve the downloaded file to the user."""
    try:
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        
        if not os.path.exists(file_path):
            # Check if we have a URL in the session that we can download directly
            if 'download_result' in session and session['download_result'].get('media_url'):
                # Extract necessary info from session
                media_url = session['download_result']['media_url']
                media_type = session['download_result'].get('media_type', 'image')
                
                logger.info(f"Attempting direct download from {media_url} to {file_path}")
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Download the file
                try:
                    response = requests.get(media_url, stream=True, timeout=10)
                    if response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        logger.info(f"Direct download successful to: {file_path}")
                    else:
                        logger.error(f"Failed to download directly: {response.status_code}")
                        raise Exception(f"Failed to download file: HTTP {response.status_code}")
                except Exception as e:
                    logger.error(f"Error with direct download: {str(e)}")
                    raise
            else:
                flash('The requested file does not exist.', 'danger')
                return redirect(url_for('index'))
        
        # Double-check the file exists after attempted download
        if not os.path.exists(file_path):
            flash('Failed to download the file. Please try again.', 'danger')
            return redirect(url_for('index'))
        
        # Determine content type
        content_type = 'video/mp4' if filename.endswith('.mp4') else 'image/jpeg'
        
        # Explicitly specify attachment disposition to force download
        return send_file(
            file_path,
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        flash(f"Error downloading file: {str(e)}", 'danger')
        return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear_result():
    """Clear the download result from session."""
    if 'download_result' in session:
        session.pop('download_result')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('index.html', error="Server error occurred. Please try again later."), 500
