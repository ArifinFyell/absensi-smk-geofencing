from app.models import db

class Guru(db.Model):
    __tablename__ = 'guru'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    nama = db.Column(db.String(100), nullable=False)
    nip = db.Column(db.String(30), unique=True, nullable=True)
    email = db.Column(db.String(100), nullable=True)
    no_hp = db.Column(db.String(20), nullable=True)
    foto = db.Column(db.String(255), default='default_avatar.png')
    status = db.Column(db.String(20), default='Aktif')
    is_email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    # Wali kelas: FK ke Kelas (nullable, hanya diisi jika guru ini adalah wali kelas)
    wali_kelas_id = db.Column(db.Integer, db.ForeignKey('kelas.id'), nullable=True)

    user = db.relationship('User', backref='guru_profile', uselist=False)
    jadwal_list = db.relationship('Jadwal', backref='guru_rel', lazy=True)
    wali_kelas_rel = db.relationship('Kelas', foreign_keys=[wali_kelas_id], backref='wali_kelas_guru', lazy=True, uselist=False)

    @property
    def is_wali_kelas(self):
        return self.wali_kelas_id is not None

    def to_dict(self):
        return {
            'id': self.id,
            'nama': self.nama,
            'nip': self.nip or '-',
            'email': self.email or '-',
            'no_hp': self.no_hp or '-',
            'foto': self.foto,
            'status': self.status
        }
