from app.models import db

class SettingGeofence(db.Model):
    __tablename__ = 'setting_geofence'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False, default=0.334612)
    longitude = db.Column(db.Float, nullable=False, default=101.026415)
    radius = db.Column(db.Integer, nullable=False, default=100) # meter


class SettingJam(db.Model):
    __tablename__ = 'setting_jam'

    id = db.Column(db.Integer, primary_key=True)
    jam_hadir_mulai = db.Column(db.String(10), default='06:45')
    jam_hadir_selesai = db.Column(db.String(10), default='07:15')
    jam_terlambat_selesai = db.Column(db.String(10), default='07:30')
    jam_tutup = db.Column(db.String(10), default='17:00')


class SettingSekolah(db.Model):
    __tablename__ = 'setting_sekolah'

    id = db.Column(db.Integer, primary_key=True)
    nama_sekolah = db.Column(db.String(150), default='SMKN 1 BANGKINANG')
    alamat_sekolah = db.Column(db.Text, default='Jl. Tuanku Tambusai No. 1, Bangkinang, Kampar, Riau')
    logo = db.Column(db.String(255), default='logo_smkn1.png')
    tahun_ajaran = db.Column(db.String(30), default='2025/2026')
    semester = db.Column(db.String(20), default='Ganjil')
