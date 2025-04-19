import os
import logging
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash, session
from werkzeug.middleware.proxy_fix import ProxyFix
from instagram_downloader import download_instagram_content, is_valid_instagram_url

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

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
