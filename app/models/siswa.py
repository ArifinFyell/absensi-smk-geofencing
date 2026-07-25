from app.models import db

class Siswa(db.Model):
    __tablename__ = 'siswa'

    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(20), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    kelas_id = db.Column(db.Integer, db.ForeignKey('kelas.id'), nullable=False)
    jurusan_id = db.Column(db.Integer, db.ForeignKey('jurusan.id'), nullable=False)
    jenis_kelamin = db.Column(db.String(20), default='Laki-Laki') # Laki-Laki / Perempuan
    alamat = db.Column(db.Text, nullable=True)
    no_hp = db.Column(db.String(20), nullable=True)
    foto = db.Column(db.String(255), default='default_student.png')
    status = db.Column(db.String(20), default='Aktif')

    absensi_list = db.relationship('Absensi', backref='siswa_rel', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'nis': self.nis,
            'nama': self.nama,
            'kelas_id': self.kelas_id,
            'kelas_nama': self.kelas_rel.nama_kelas if self.kelas_rel else '-',
            'jurusan_id': self.jurusan_id,
            'jurusan_kode': self.jurusan_rel.kode if self.jurusan_rel else '-',
            'jenis_kelamin': self.jenis_kelamin,
            'alamat': self.alamat or '-',
            'no_hp': self.no_hp or '-',
            'foto': self.foto,
            'status': self.status
        }
