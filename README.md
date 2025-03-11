# Media Gallery App

A lightweight Flask-based media gallery application that allows users to upload images and videos, automatically generates thumbnails, rotates images based on EXIF data, and provides real-time updates. An admin panel is available to manage and delete media files using basic authentication.

## Features

- **Image & Video Upload:** Upload images and videos via the web interface.
- **Automatic Thumbnail Creation:** 
  - For images, thumbnails are created using Pillow.
  - For videos, thumbnails are generated using FFmpeg.
- **Auto-Rotate Images:** Reads EXIF orientation data and rotates images accordingly.
- **Real-Time Updates:** Automatically checks for and displays new media.
- **Admin Panel:** Manage media files (view and delete) with basic authentication.
- **Responsive UI:** Uses [Tailwind CSS](https://tailwindcss.com/) for a modern and responsive design.

## Requirements

- Python 3.6+
- [Flask](https://flask.palletsprojects.com/)
- [Flask-BasicAuth](https://pythonhosted.org/Flask-BasicAuth/)
- [Pillow](https://python-pillow.org/)
- [Werkzeug](https://werkzeug.palletsprojects.com/)
- [FFmpeg](https://ffmpeg.org/) (must be installed and available in your system's PATH)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/media-gallery-app.git
   cd media-gallery-app
   ```

2. **Create and Activate a Virtual Environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install the Python Dependencies:**

   You can install the required Python packages using pip:

   ```bash
   pip install Flask Flask-BasicAuth Pillow
   ```

4. **Install FFmpeg:**

   - **Linux:** Install via your package manager (e.g., `sudo apt-get install ffmpeg`).
   - **macOS:** Use Homebrew (`brew install ffmpeg`).
   - **Windows:** Download from the [FFmpeg website](https://ffmpeg.org/download.html) and ensure the executable is in your system's PATH.

## Configuration

The application configuration is set in `app.py`:

- **UPLOAD_FOLDER:** Directory for storing uploaded media files (default: `static/uploads`).
- **THUMBNAIL_FOLDER:** Directory for storing generated thumbnails (default: `static/thumbnails`).
- **ALLOWED_EXTENSIONS:** Allowed file types (png, jpg, jpeg, gif, mp4, mov, avi).
- **BASIC_AUTH_USERNAME / BASIC_AUTH_PASSWORD:** Credentials for accessing the admin panel (default: `admin` / `secret`).
- **MAX_CONTENT_LENGTH:** Maximum allowed file size for uploads (default: 128MB).

Directories for uploads and thumbnails are automatically created at startup if they do not exist.

## Running the Application

To run the app, simply execute:

```bash
python app.py
```

The server will start at [http://0.0.0.0:5000](http://0.0.0.0:5000).

- **Gallery:** Visit the root URL (`/`) to view and upload media.
- **Admin Panel:** Visit `/admin` and log in using the basic authentication credentials to manage your media files.

## Usage

- **Uploading Media:** Use the upload buttons on the homepage to select files from your device. The app supports both capturing from the camera (on mobile) and selecting files from the gallery.
- **Viewing Media:** Uploaded media will appear in the gallery. Click on any media to open it in a lightbox for an enlarged view.
- **Admin Management:** In the admin panel, you can view media details (upload time and filename) and delete files as needed.

## Contributing

Contributions are welcome! Feel free to fork this repository and submit pull requests with improvements or bug fixes.

## License

This project is open source and available under the [MIT License](LICENSE).
