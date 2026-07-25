import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smkn1bangkinang-secret-key-2026-absensi-geofence'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database: SQLite by default, easy setup; supports MySQL via DB_URL env if provided
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'database', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # SMKN 1 Bangkinang Default Geofence Settings
    DEFAULT_LATITUDE = 0.334612
    DEFAULT_LONGITUDE = 101.026415
    DEFAULT_RADIUS = 100  # meters
