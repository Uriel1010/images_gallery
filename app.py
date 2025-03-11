from flask import Flask, render_template, request, send_from_directory
from flask_basicauth import BasicAuth
import os
from datetime import datetime
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)
app.config.update({
    'UPLOAD_FOLDER': 'static/uploads',
    'THUMBNAIL_FOLDER': 'static/thumbnails',
    'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'},
    'BASIC_AUTH_USERNAME': 'admin',
    'BASIC_AUTH_PASSWORD': 'secret',
    'MAX_CONTENT_LENGTH': 128 * 1024 * 1024  # 128MB
})

basic_auth = BasicAuth(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def rotate_image(image_path):
    try:
        img = Image.open(image_path)
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
            img.close()
    except Exception as e:
        print(f"Rotation failed: {e}")

def create_thumbnail(path, is_video=False):
    try:
        if is_video:
            thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], 
                         os.path.basename(path).split('.')[0] + '.jpg')
            subprocess.run([
                'ffmpeg', '-i', path, '-ss', '00:00:01', '-vframes', '1',
                thumbnail_path, '-y'
            ], check=True)
            return thumbnail_path
        else:
            with Image.open(path) as img:
                img.thumbnail((800, 800))
                thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], 
                                            os.path.basename(path))
                img.save(thumbnail_path)
                return thumbnail_path
    except Exception as e:
        print(f"Thumbnail creation failed: {e}")
        return None

@app.route('/')
def index():
    media_files = []
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(f):
            media_files.append(f)
    media_files.sort(key=lambda x: os.path.getmtime(
        os.path.join(app.config['UPLOAD_FOLDER'], x)), reverse=True)
    return render_template('index.html', media_files=media_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return {'status': 'error', 'message': 'No files selected'}, 400
    
    files = request.files.getlist('files')
    results = []
    
    for file in files:
        if file.filename == '':
            results.append({'status': 'error', 'message': 'Empty filename'})
            continue
            
        if file and allowed_file(file.filename):
            try:
                ext = file.filename.rsplit('.', 1)[1].lower()
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{timestamp}_{secure_filename(file.filename)}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                if ext in {'mp4', 'mov', 'avi'}:
                    thumbnail = create_thumbnail(filepath, is_video=True)
                else:
                    rotate_image(filepath)
                    thumbnail = create_thumbnail(filepath)
                
                if thumbnail:
                    results.append({
                        'status': 'success', 
                        'filename': filename, 
                        'type': 'video' if ext in {'mp4', 'mov', 'avi'} else 'image'
                    })
                else:
                    results.append({'status': 'error', 'message': 'Thumbnail failed'})
            except Exception as e:
                results.append({'status': 'error', 'message': str(e)})
        else:
            results.append({'status': 'error', 'message': 'Invalid file type'})
    
    return {'results': results}

@app.route('/updates')
def check_updates():
    try:
        count = int(request.args.get('count', 0))
        all_files = sorted(os.listdir(app.config['UPLOAD_FOLDER']),
                          key=lambda x: os.path.getmtime(
                              os.path.join(app.config['UPLOAD_FOLDER'], x)),
                          reverse=True)
        return {'newImages': all_files[:len(all_files)-count]}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/admin')
@basic_auth.required
def admin_panel():
    media_files = []
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(f):
            media_files.append({
                'filename': f,
                'upload_time': datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], f))
                )
            })
    media_files.sort(key=lambda x: x['upload_time'], reverse=True)
    return render_template('admin.html', media_files=media_files)

@app.route('/delete/<filename>', methods=['DELETE'])
@basic_auth.required
def delete_image(filename):
    try:
        safe_filename = secure_filename(filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], 
                                   safe_filename.split('.')[0] + '.jpg')
        
        if os.path.exists(upload_path):
            os.remove(upload_path)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            
        return {'status': 'success'}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], 
                              secure_filename(filename))

@app.route('/thumbnails/<filename>')
def thumbnail_file(filename):
    try:
        return send_from_directory(app.config['THUMBNAIL_FOLDER'], 
                                 secure_filename(filename))
    except:
        return send_from_directory(app.config['UPLOAD_FOLDER'], 
                                 secure_filename(filename))

@app.route('/icon.png')
def serve_icon():
    return send_from_directory('static', 'icon.png')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)