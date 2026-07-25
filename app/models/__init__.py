from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.user import User
from app.models.guru import Guru
from app.models.kelas import Kelas
from app.models.jurusan import Jurusan
from app.models.siswa import Siswa
from app.models.jadwal import Jadwal
from app.models.absensi import Absensi
from app.models.setting import SettingGeofence, SettingJam, SettingSekolah
from app.models.activity_log import ActivityLog
from app.models.notification import Notification
from app.models.hari_libur import HariLibur
