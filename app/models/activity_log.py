from datetime import datetime
from app.models import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    aktivitas = db.Column(db.Text, nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'aktivitas': self.aktivitas,
            'waktu': self.tanggal.strftime('%H:%M:%S') if self.tanggal else '',
            'tanggal': self.tanggal.strftime('%d %b %Y') if self.tanggal else ''
        }
