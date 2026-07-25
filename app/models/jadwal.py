from app.models import db

class Jadwal(db.Model):
    __tablename__ = 'jadwal'

    id = db.Column(db.Integer, primary_key=True)
    hari = db.Column(db.String(10), nullable=False) # Senin, Selasa, Rabu, Kamis, Jumat
    jam_mulai = db.Column(db.String(10), nullable=False) # e.g. "07.20" or "07:20"
    jam_selesai = db.Column(db.String(10), nullable=False) # e.g. "08.00" or "08:00"
    mata_pelajaran = db.Column(db.String(100), nullable=False)
    guru_id = db.Column(db.Integer, db.ForeignKey('guru.id'), nullable=True)
    kelas_id = db.Column(db.Integer, db.ForeignKey('kelas.id'), nullable=False)

    absensi_list = db.relationship('Absensi', backref='jadwal_rel', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'hari': self.hari,
            'jam_mulai': self.jam_mulai,
            'jam_selesai': self.jam_selesai,
            'mata_pelajaran': self.mata_pelajaran,
            'guru_id': self.guru_id,
            'guru_nama': self.guru_rel.nama if self.guru_rel else '-',
            'kelas_id': self.kelas_id,
            'kelas_nama': self.kelas_rel.nama_kelas if self.kelas_rel else '-'
        }
