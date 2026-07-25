from app.models import db

class Kelas(db.Model):
    __tablename__ = 'kelas'

    id = db.Column(db.Integer, primary_key=True)
    nama_kelas = db.Column(db.String(50), nullable=False, unique=True) # e.g. X PPLG
    wali_kelas = db.Column(db.String(100), nullable=True)
    tingkat = db.Column(db.String(10), default='X') # X, XI, XII

    siswa_list = db.relationship('Siswa', backref='kelas_rel', lazy=True)
    jadwal_list = db.relationship('Jadwal', backref='kelas_rel', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nama_kelas': self.nama_kelas,
            'wali_kelas': self.wali_kelas or '-',
            'tingkat': self.tingkat
        }
