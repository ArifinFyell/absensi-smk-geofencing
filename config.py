import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smkn1bangkinang-secret-key-2026-absensi-geofence'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Handing Vercel serverless environment (Read-only filesystem)
    IS_VERCEL = os.environ.get('VERCEL') == '1'
    DATA_DIR = '/tmp' if IS_VERCEL else os.path.join(BASE_DIR, 'database')
    
    # Database: SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(DATA_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join('/tmp', 'uploads') if IS_VERCEL else os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # SMKN 1 Bangkinang Default Geofence Settings
    DEFAULT_LATITUDE = 0.334612
    DEFAULT_LONGITUDE = 101.026415
    DEFAULT_RADIUS = 100  # meters
