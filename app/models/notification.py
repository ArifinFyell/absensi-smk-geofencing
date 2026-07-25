from datetime import datetime
from app.models import db

class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(150), nullable=False)
    pesan = db.Column(db.Text, nullable=False)
    tipe = db.Column(db.String(20), default='info') # info, success, warning, danger
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'judul': self.judul,
            'pesan': self.pesan,
            'tipe': self.tipe,
            'is_read': self.is_read,
            'waktu': self.created_at.strftime('%d %b %Y %H:%M') if self.created_at else ''
        }
