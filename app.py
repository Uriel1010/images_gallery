from flask import Flask, render_template, request, send_from_directory, jsonify, abort
from flask_basicauth import BasicAuth
import os
from datetime import datetime
from PIL import Image
from werkzeug.utils import secure_filename
import subprocess
import logging

app = Flask(__name__)
app.config.update({
    'UPLOAD_FOLDER': 'static/uploads',
    'THUMBNAIL_FOLDER': 'static/thumbnails',
    'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'},
    'BASIC_AUTH_USERNAME': os.environ.get('BASIC_AUTH_USERNAME', 'admin'),
    'BASIC_AUTH_PASSWORD': os.environ.get('BASIC_AUTH_PASSWORD', 'secret'),
    'MAX_CONTENT_LENGTH': 128 * 1024 * 1024  # 128MB
})

basic_auth = BasicAuth(app)
logger = app.logger
logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def rotate_image(image_path):
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

def get_media_files():
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
def index():
    media_files = get_media_files()
    return render_template('index.html', media_files=media_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'status': 'error', 'message': 'No files selected'}), 400

    files = request.files.getlist('files')
    results = []

    for file in files:
        if file.filename == '':
            results.append({'status': 'error', 'message': 'Empty filename'})
            continue

        if file and allowed_file(file.filename):
            try:
                ext = file.filename.rsplit('.', 1)[1].lower()
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                filename = f"{timestamp}_{secure_filename(file.filename)}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                if ext in {'mp4', 'mov', 'avi'}:
                    thumbnail = create_thumbnail(filepath, is_video=True)
                else:
                    rotate_image(filepath)
                    thumbnail = create_thumbnail(filepath, is_video=False)

                if thumbnail:
                    results.append({
                        'status': 'success',
                        'filename': filename,
                        'type': 'video' if ext in {'mp4', 'mov', 'avi'} else 'image'
                    })
                else:
                    results.append({'status': 'error', 'message': 'Thumbnail creation failed', 'filename': filename})
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}")
                results.append({'status': 'error', 'message': str(e)})
        else:
            results.append({'status': 'error', 'message': 'Invalid file type', 'filename': file.filename})

    return jsonify({'results': results})

@app.route('/updates')
def check_updates():
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
def admin_panel():
    media_files = []
    try:
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(f):
                media_files.append({
                    'filename': f,
                    'upload_time': datetime.fromtimestamp(os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], f)))
                })
        media_files.sort(key=lambda x: x['upload_time'], reverse=True)
    except Exception as e:
        logger.error(f"Error loading admin panel files: {e}")
    return render_template('admin.html', media_files=media_files)

@app.route('/delete/<filename>', methods=['DELETE'])
@basic_auth.required
def delete_image(filename):
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))

@app.route('/thumbnails/<filename>')
def thumbnail_file(filename):
    try:
        return send_from_directory(app.config['THUMBNAIL_FOLDER'], secure_filename(filename))
    except Exception as e:
        logger.error(f"Error serving thumbnail for {filename}: {e}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))

@app.route('/icon.png')
def serve_icon():
    return send_from_directory('static', 'icon.png')

# Error Handlers for improved stability
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'status': 'error', 'message': 'File too large'}), 413

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# In production, do not use the Flask development server.
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)
    # For local testing you may use Flask's built-in server,
    # but in production run the app with Waitress:
    #   waitress-serve --port=5000 app:app
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
