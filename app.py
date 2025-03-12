#!/usr/bin/env python3
"""
Flask Media Gallery Application

This version runs without Celery/Redis. It handles uploads,
synchronous thumbnail generation (using ffmpeg for videos and Pillow for images),
and basic file management (rotate, delete) with an admin interface.
Additionally, it supports downloading all media files as a ZIP archive.
"""

import os
import re
import logging
import subprocess
from datetime import datetime
from io import BytesIO
import zipfile

from flask import (
    Flask, render_template, request, send_from_directory, jsonify, abort,
    redirect, url_for, flash, send_file
)
from flask_basicauth import BasicAuth
from flask_talisman import Talisman
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from PIL import Image
from werkzeug.utils import secure_filename
import sentry_sdk

# Initialize Sentry for error logging if a valid DSN is provided.
SENTRY_DSN = os.environ.get('SENTRY_DSN', '').strip()
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-key')

# Enforce HTTPS and set secure headers.
Talisman(app, force_https=False, content_security_policy=None)

# Set up caching with a simple configuration.
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Initialize rate limiting.
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

app.config.update({
    'UPLOAD_FOLDER': 'static/uploads',
    'THUMBNAIL_FOLDER': 'static/thumbnails',
    'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'},
    'BASIC_AUTH_USERNAME': os.environ.get('BASIC_AUTH_USERNAME', 'admin'),
    'BASIC_AUTH_PASSWORD': os.environ.get('BASIC_AUTH_PASSWORD', 'secret'),
    'MAX_CONTENT_LENGTH': 128 * 1024 * 1024  # 128MB
})

# Ensure the upload and thumbnail directories exist.
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)

basic_auth = BasicAuth(app)
logger = app.logger
logging.basicConfig(level=logging.INFO)


def allowed_file(filename):
    """Check if the filename has an allowed extension."""
    filename = secure_filename(filename)
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def sanitize_filename(filename):
    """Sanitize filename by allowing only alphanumerics, underscores, dashes, and dots."""
    return re.sub(r'[^A-Za-z0-9_.-]', '', filename)


def rotate_image(image_path):
    """Rotate image based on its EXIF orientation tag."""
    try:
        with Image.open(image_path) as img:
            exif = img.getexif()
            orientation = exif.get(0x0112)
            if orientation:
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
                img.save(image_path)
    except Exception as e:
        logger.error(f"Rotation failed for {image_path}: {e}")


def create_thumbnail(path, is_video=False):
    """
    Create a thumbnail for the given media file.
    For videos, use ffmpeg to capture a frame.
    For images, generate a thumbnail with max dimensions of 800x800.
    """
    try:
        base_name = os.path.splitext(os.path.basename(path))[0]
        thumbnail_filename = f"{base_name}.jpg"
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
        if is_video:
            subprocess.run([
                'ffmpeg', '-i', path, '-ss', '00:00:01', '-vframes', '1',
                thumbnail_path, '-y'
            ], check=True)
        else:
            with Image.open(path) as img:
                img.thumbnail((800, 800))
                img.save(thumbnail_path)
        return thumbnail_path
    except Exception as e:
        logger.error(f"Thumbnail creation failed for {path}: {e}")
        return None


@cache.cached(timeout=60, key_prefix='media_files')
def get_media_files():
    """Return a sorted list of media files in the upload folder."""
    media_files = []
    try:
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(f):
                media_files.append(f)
        media_files.sort(key=lambda x: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], x)), reverse=True)
    except Exception as e:
        logger.error(f"Error listing media files: {e}")
    return media_files


@app.route('/')
@limiter.limit("10 per minute")
def index():
    """Render the main gallery page."""
    media_files = get_media_files()
    return render_template('index.html', media_files=media_files)


@app.route('/upload', methods=['POST'])
@limiter.limit("5 per minute")
def upload_file():
    """
    Handle file uploads.

    Saves the file, rotates it if necessary, and creates a thumbnail synchronously.
    """
    if 'files' not in request.files:
        return jsonify({'status': 'error', 'message': 'No files selected'}), 400

    files = request.files.getlist('files')
    results = []

    for file in files:
        if file.filename == '':
            results.append({'status': 'error', 'message': 'Empty filename'})
            continue

        filename = sanitize_filename(file.filename)
        if file and allowed_file(filename):
            try:
                ext = filename.rsplit('.', 1)[1].lower()
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                new_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                file.save(filepath)

                if ext not in {'mp4', 'mov', 'avi'}:
                    rotate_image(filepath)

                is_video = ext in {'mp4', 'mov', 'avi'}
                create_thumbnail(filepath, is_video)

                results.append({
                    'status': 'success',
                    'filename': new_filename,
                    'type': 'video' if is_video else 'image'
                })
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
                results.append({'status': 'error', 'message': str(e)})
        else:
            results.append({'status': 'error', 'message': 'Invalid file type', 'filename': file.filename})

    return jsonify({'results': results})


@app.route('/updates')
@limiter.limit("20 per minute")
def check_updates():
    """Check for new files in the upload folder since the last update."""
    try:
        count = int(request.args.get('count', 0))
        all_files = sorted(os.listdir(app.config['UPLOAD_FOLDER']),
                           key=lambda x: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], x)),
                           reverse=True)
        new_files = all_files[:len(all_files)-count] if count < len(all_files) else []
        return jsonify({'newImages': new_files})
    except Exception as e:
        logger.error(f"Error checking updates: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/admin')
@basic_auth.required
@limiter.limit("10 per minute")
def admin_panel():
    """
    Admin panel for managing media files.

    Supports pagination and file deletion.
    """
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    per_page = 10
    media_list = []
    try:
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(f):
                media_list.append({
                    'filename': f,
                    'upload_time': datetime.fromtimestamp(os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], f)))
                })
        media_list.sort(key=lambda x: x['upload_time'], reverse=True)
        total = len(media_list)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_media = media_list[start:end]
    except Exception as e:
        logger.error(f"Error loading admin panel files: {e}")
        paginated_media = []
        total = 0
    return render_template('admin.html', media_files=paginated_media, page=page, total=total, per_page=per_page)


@app.route('/rename/<filename>', methods=['POST'])
@basic_auth.required
def rename_file(filename):
    """(Deprecated) Rename a media file from the admin panel."""
    new_name = request.form.get('new_name')
    if not new_name:
        flash("New name is required", "error")
        return redirect(url_for('admin_panel'))
    new_name = sanitize_filename(new_name)
    safe_filename = secure_filename(filename)
    old_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    new_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{new_name}"
    new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    try:
        os.rename(old_path, new_path)
        flash("File renamed successfully", "success")
    except Exception as e:
        logger.error(f"Error renaming file {filename}: {e}")
        flash("Error renaming file", "error")
    return redirect(url_for('admin_panel'))


@app.route('/delete/<filename>', methods=['DELETE'])
@basic_auth.required
@limiter.limit("5 per minute")
def delete_image(filename):
    """Delete a media file and its thumbnail."""
    try:
        safe_filename = secure_filename(filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], f"{os.path.splitext(safe_filename)[0]}.jpg")

        if os.path.exists(upload_path):
            os.remove(upload_path)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error deleting file {filename}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/download_all')
@basic_auth.required
def download_all():
    """Download all media files as a zip archive."""
    try:
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
                for file in files:
                    if allowed_file(file):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, app.config['UPLOAD_FOLDER'])
                        zf.write(file_path, arcname)
        memory_file.seek(0)
        # Use download_name (Flask >=2.2) instead of deprecated attachment_filename
        return send_file(memory_file, download_name="media_files.zip", as_attachment=True)
    except Exception as e:
        logger.error(f"Error creating zip file: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to create zip file'}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve an uploaded file."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))


@app.route('/thumbnails/<filename>')
def thumbnail_file(filename):
    """Serve a thumbnail file."""
    try:
        return send_from_directory(app.config['THUMBNAIL_FOLDER'], secure_filename(filename))
    except Exception as e:
        logger.error(f"Error serving thumbnail for {filename}: {e}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))


@app.route('/icon.png')
def serve_icon():
    """Serve the default icon."""
    return send_from_directory('static', 'icon.png')


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors."""
    return jsonify({'status': 'error', 'message': 'File too large'}), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    # For local testing only (production should run with Gunicorn).
    app.run(host='0.0.0.0', port=5000)
