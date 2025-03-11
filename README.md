# Media Gallery App

A lightweight, Flask-based media gallery application that allows users to upload images and videos, with automatic thumbnail generation, image auto-rotation, and real-time gallery updates. An admin panel with basic authentication is provided for managing media files. This updated version includes enhanced logging, robust error handling, and production-ready deployment with Waitress.

## Features

- **Media Upload:**  
  Upload images and videos directly through the web interface.

- **Automatic Thumbnail Generation:**  
  - **Images:** Thumbnails are generated using [Pillow](https://python-pillow.org/).  
  - **Videos:** Thumbnails are created using [FFmpeg](https://ffmpeg.org/).

- **Auto-Rotate Images:**  
  Automatically rotates images based on EXIF orientation data.

- **Real-Time Updates:**  
  The gallery checks for new media files periodically and updates in real time.

- **Admin Panel:**  
  Manage media files with a secure admin panel protected via basic authentication. Delete files directly from the panel.

- **Enhanced Logging & Error Handling:**  
  - Uses Python's logging module for detailed event tracking.  
  - Custom error handlers for file size issues (HTTP 413) and internal server errors (HTTP 500) return JSON messages.

- **Responsive & Accessible UI:**  
  Built with [Tailwind CSS](https://tailwindcss.com/) and includes toast notifications for feedback and improved accessibility features.

- **Production-Ready Deployment:**  
  Designed to run with [Waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/) for production use.

## Requirements

- **Python 3.6+**
- **Flask**
- **Flask-BasicAuth**
- **Pillow**
- **Werkzeug**
- **FFmpeg:** Must be installed and available in your system's PATH.
- **Waitress:** For production deployment.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/media-gallery-app.git
   cd media-gallery-app
   ```

2. **Set Up a Virtual Environment (Optional but Recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Python Dependencies:**

   ```bash
   pip install Flask Flask-BasicAuth Pillow waitress
   ```

4. **Install FFmpeg:**

   - **Linux:** `sudo apt-get install ffmpeg`
   - **macOS:** `brew install ffmpeg`
   - **Windows:** Download from the [FFmpeg website](https://ffmpeg.org/download.html) and add the executable to your system's PATH.

## Configuration

The application settings are defined in `app.py`:

- **UPLOAD_FOLDER:** Directory for storing uploaded media files (default: `static/uploads`).
- **THUMBNAIL_FOLDER:** Directory for storing generated thumbnails (default: `static/thumbnails`).
- **ALLOWED_EXTENSIONS:** Accepted file types: `png`, `jpg`, `jpeg`, `gif`, `mp4`, `mov`, `avi`.
- **BASIC_AUTH_USERNAME & BASIC_AUTH_PASSWORD:**  
  These are sourced from environment variables. If not set, the defaults are `admin` and `secret` respectively.
- **MAX_CONTENT_LENGTH:** Maximum upload size is set to 128 MB.

The necessary directories are automatically created at startup.

## Running the Application

### Development (Local Testing):

You can run the Flask development server by executing:

```bash
python app.py
```

### Production Deployment:

For a production environment, it is recommended to use Waitress:

```bash
waitress-serve --port=5000 app:app
```

The server will be accessible at [http://0.0.0.0:5000](http://0.0.0.0:5000).

## Usage

- **Gallery:**  
  Navigate to `/` to view and upload media.  
  Uploaded files are processed (rotated if necessary and a thumbnail is generated) and appear in the gallery with real-time updates.

- **Uploading Media:**  
  Use the provided buttons to capture from your camera (mobile) or select files from your device.

- **Admin Panel:**  
  Access the admin panel at `/admin` to manage and delete media files.  
  Basic authentication is required (credentials are set via environment variables or default to `admin`/`secret`).

- **Error Feedback & Notifications:**  
  Toast notifications provide immediate feedback on upload success or errors, and the application logs key events for troubleshooting.

## Logging & Error Handling

- **Logging:**  
  The app uses Python’s built-in logging module to record important events and errors.

- **Error Handlers:**  
  Custom handlers for common errors (e.g., file size errors - HTTP 413, internal errors - HTTP 500) ensure stable operation and return JSON responses.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests with enhancements or bug fixes.

## License

This project is open source and available under the [MIT License](LICENSE).
