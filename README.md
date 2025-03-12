# Media Gallery App

A Flask-based media gallery application that lets you upload images and videos, automatically generates thumbnails, and displays them in a continuously scrolling billboard-style gallery. The app features an admin panel for managing (deleting) media files and supports downloading all media files as a ZIP archive.

## Features

- **Media Upload:** Upload images and videos via mobile or desktop.
- **Thumbnail Generation:** Synchronously creates thumbnails using Pillow (for images) and ffmpeg (for videos).
- **Continuous Auto-Scroll:** On desktop, the gallery auto-scrolls seamlessly (with a toggle to disable/enable auto-scroll). On mobile, auto-scroll is disabled to prevent duplicate images.
- **Admin Panel:** Manage (delete) uploaded files and download all media files as a ZIP archive.
- **Security Enhancements:** Basic HTTP authentication for admin routes, HTTPS enforcement via Flask-Talisman, and rate limiting.

## Requirements

- Python 3.9+
- [Flask](https://flask.palletsprojects.com/)
- [Pillow](https://pillow.readthedocs.io/)
- [ffmpeg](https://ffmpeg.org/) (must be installed and available in your system PATH)
- Docker (optional, for containerized deployment)

## Installation

1. **Clone the Repository**

   ```sh
   git clone https://github.com/yourusername/media-gallery-app.git
   cd media-gallery-app
   ```

2. **Create and Activate a Virtual Environment**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```sh
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install ffmpeg**

   Make sure ffmpeg is installed and available in your PATH. For example, on Ubuntu:

   ```sh
   sudo apt update
   sudo apt install ffmpeg
   ```

## Configuration

The application reads configuration values from environment variables. Create a `.env` file or set these in your environment:

- `SECRET_KEY`: Your Flask secret key.
- `BASIC_AUTH_USERNAME`: Username for the admin panel (default is `admin`).
- `BASIC_AUTH_PASSWORD`: Password for the admin panel (default is `secret`).
- `SENTRY_DSN`: Optional Sentry DSN for error logging.

## Running the App Locally

1. **Run the Application**

   ```sh
   python app.py
   ```

2. **Access the Gallery**

   Open your browser and navigate to [http://localhost:5000](http://localhost:5000).

3. **Access the Admin Panel**

   Navigate to [http://localhost:5000/admin](http://localhost:5000/admin) and enter your admin credentials.

## Running with Docker Compose

This project includes a `Dockerfile` and `docker-compose.yml` for containerized deployment. All the necessary files (such as `Dockerfile`, `docker-compose.yml`, `gunicorn_config.py`, and the source code) are included in the repository.

### Steps to Deploy with Docker Compose

1. **Clone the Repository from GitHub**

   ```sh
   git clone https://github.com/yourusername/media-gallery-app.git
   cd media-gallery-app
   ```

2. **Build and Run the Docker Containers**

   Use Docker Compose to build the image and start the container:

   ```sh
   docker-compose up --build
   ```

   This command builds the Docker image according to the provided `Dockerfile` and starts the Flask app (with Gunicorn) on port 5000.

3. **Access the Application**

   Open your browser and go to [http://localhost:5000](http://localhost:5000) to view the media gallery. The admin panel is accessible at [http://localhost:5000/admin](http://localhost:5000/admin).

4. **Stopping the Application**

   To stop the application, press `Ctrl+C` in the terminal or run:

   ```sh
   docker-compose down
   ```

### File Structure

```plaintext
.
├── app.py                  # Main Flask application
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Dockerfile for building the container image
├── gunicorn_config.py      # Gunicorn configuration for production
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation (this file)
├── .gitignore              # Files and directories to ignore in Git
└── templates
    ├── admin.html          # Admin panel template
    └── index.html          # Gallery (main) template
```

## Customization & UI/UX

- **Auto-Scroll Behavior:**  
  On desktop, the gallery auto-scrolls continuously (billboard effect) with a toggle button to enable/disable this feature. On mobile devices, auto-scroll is disabled by default to avoid duplicate images.

- **Admin Panel:**  
  The admin panel allows deletion of media files and downloading all files as a ZIP archive.

## Troubleshooting

- **ZIP Download Fails:**  
  Ensure that all media files in your upload directory have valid file extensions and that the server process has read access to those files.

- **Thumbnail Creation Issues:**  
  Check that `ffmpeg` is installed and available in your PATH, and that image files are not corrupted.

- **Auto-Scroll Issues:**  
  Auto-scroll is enabled only on desktop (screens ≥768px). On mobile devices, the gallery will display without auto-scroll to prevent duplication.

## License

This project is licensed under the MIT License.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Tailwind CSS](https://tailwindcss.com/) for styling.
- [Pillow](https://pillow.readthedocs.io/) for image processing.
- [ffmpeg](https://ffmpeg.org/) for video thumbnail extraction.
