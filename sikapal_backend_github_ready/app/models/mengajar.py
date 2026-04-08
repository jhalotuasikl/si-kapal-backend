from app.extensions import db
from datetime import datetime

class LaporanMengajar(db.Model):

    __tablename__ = "laporan_mengajar"

    id_laporan = db.Column(db.Integer, primary_key=True)

    id_monitor = db.Column(db.Integer)

    materi = db.Column(db.Text)
    catatan = db.Column(db.Text)
    jumlah_hadir = db.Column(db.Integer)

    waktu_input = db.Column(
        db.DateTime,
        default=datetime.now
    )