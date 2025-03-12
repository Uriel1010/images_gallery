# Media Gallery App

A Flask-based media gallery application that lets you upload images and videos, automatically generates thumbnails, and displays them in a continuously scrolling billboard-style gallery. The app features an admin panel for managing (deleting) media files and supports downloading all media files as a ZIP archive.

## Features

- **Media Upload:** Upload images and videos via mobile or desktop.
- **Thumbnail Generation:** Synchronously creates thumbnails using Pillow (for images) and ffmpeg (for videos).
- **Continuous Auto-Scroll:** On desktop, the gallery auto-scrolls seamlessly (with a toggle to disable/enable auto-scroll).
- **Responsive Design:** On mobile devices, the auto-scroll is disabled and the gallery displays normally.
- **Admin Panel:** Manage uploaded files (delete) and download all media files as a ZIP archive.
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

   Make sure ffmpeg is installed and available in your PATH. On Ubuntu, for example:

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

## Running with Docker

This project includes a Dockerfile and docker-compose configuration for containerized deployment.

1. **Build and Run Containers**

   ```sh
   docker-compose up --build
   ```

2. **Access the App**

   The app will be available at [http://localhost:5000](http://localhost:5000).

## File Structure

```plaintext
.
├── app.py                  # Main Flask application
├── docker-compose.yml      # Docker Compose configuration
├── dockerfile              # Dockerfile for building the container image
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
  On desktop, the gallery auto-scrolls continuously (billboard effect) with a toggle button to enable/disable this feature. On mobile, auto-scroll is disabled to prevent duplicated images.

- **Admin Panel:**  
  The admin panel allows deletion of media files and downloading all files as a ZIP archive.

## Troubleshooting

- **ZIP Download Fails:**  
  Ensure that all media files in your upload directory have valid file extensions and that the server process has read access to those files.

- **Thumbnail Creation Issues:**  
  Check that `ffmpeg` is installed and available in your PATH, and that image files are not corrupted.

- **Auto-Scroll Issues:**  
  The auto-scroll is enabled only on desktop (screens ≥768px). On mobile devices, the gallery will not auto-scroll and images will display only once.

## License

This project is licensed under the MIT License.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Tailwind CSS](https://tailwindcss.com/) for styling.
- [Pillow](https://pillow.readthedocs.io/) for image processing.
- [ffmpeg](https://ffmpeg.org/) for video thumbnail extraction.