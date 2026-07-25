from datetime import datetime, date
from app.models import db

class Absensi(db.Model):
    __tablename__ = 'absensi'

    id = db.Column(db.Integer, primary_key=True)
    siswa_id = db.Column(db.Integer, db.ForeignKey('siswa.id'), nullable=False)
    jadwal_id = db.Column(db.Integer, db.ForeignKey('jadwal.id'), nullable=True)
    tanggal = db.Column(db.Date, default=date.today, nullable=False)
    jam_masuk = db.Column(db.String(10), nullable=False) # e.g. "07:03:15"
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    jarak = db.Column(db.Float, nullable=True) # distance in meters
    foto = db.Column(db.String(255), nullable=False) # relative upload path
    status = db.Column(db.String(20), default='Hadir') # Hadir, Terlambat, Terlambat Berat, Izin, Sakit, Belum Hadir
    device = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    browser = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'siswa_id': self.siswa_id,
            'nis': self.siswa_rel.nis if self.siswa_rel else '-',
            'nama': self.siswa_rel.nama if self.siswa_rel else '-',
            'kelas': self.siswa_rel.kelas_rel.nama_kelas if self.siswa_rel and self.siswa_rel.kelas_rel else '-',
            'jurusan': self.siswa_rel.jurusan_rel.kode if self.siswa_rel and self.siswa_rel.jurusan_rel else '-',
            'jadwal_id': self.jadwal_id,
            'mata_pelajaran': self.jadwal_rel.mata_pelajaran if self.jadwal_rel else 'Umum',
            'guru_nama': self.jadwal_rel.guru_rel.nama if self.jadwal_rel and self.jadwal_rel.guru_rel else 'Pengajar SMK',
            'tanggal': self.tanggal.strftime('%Y-%m-%d') if isinstance(self.tanggal, date) else str(self.tanggal),
            'jam_masuk': self.jam_masuk,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'jarak': round(self.jarak, 1) if self.jarak is not None else 0,
            'foto': self.foto,
            'status': self.status,
            'device': self.device or 'Mobile Web',
            'ip_address': self.ip_address or '127.0.0.1',
            'browser': self.browser or 'Chrome'
        }
