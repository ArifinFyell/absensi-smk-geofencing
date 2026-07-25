from app.models import db

class HariLibur(db.Model):
    """Model untuk hari libur / tanggal yang dikecualikan dari jadwal."""
    __tablename__ = 'hari_libur'

    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.Date, nullable=False, unique=True)
    keterangan = db.Column(db.String(255), nullable=True)      # e.g. "Libur Nasional", "Libur Sekolah"
    dibuat_oleh = db.Column(db.String(100), nullable=True)     # 'admin' atau nama guru
    # null = berlaku untuk semua; isi guru_id = hanya untuk guru itu
    guru_id = db.Column(db.Integer, db.ForeignKey('guru.id'), nullable=True)

    guru = db.relationship('Guru', backref='hari_libur_list', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'tanggal': self.tanggal.strftime('%Y-%m-%d'),
            'keterangan': self.keterangan,
            'dibuat_oleh': self.dibuat_oleh,
            'guru_id': self.guru_id
        }
