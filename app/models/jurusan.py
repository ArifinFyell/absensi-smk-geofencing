from app.models import db

class Jurusan(db.Model):
    __tablename__ = 'jurusan'

    id = db.Column(db.Integer, primary_key=True)
    nama_jurusan = db.Column(db.String(100), nullable=False) # e.g. Pengembangan Perangkat Lunak dan Gim
    kode = db.Column(db.String(20), nullable=False, unique=True) # e.g. PPLG

    siswa_list = db.relationship('Siswa', backref='jurusan_rel', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nama_jurusan': self.nama_jurusan,
            'kode': self.kode
        }
