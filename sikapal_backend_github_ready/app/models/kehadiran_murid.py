# app/models/kehadiran_murid.py
from app.extensions import db
from datetime import date

class KehadiranMurid(db.Model):
    __tablename__ = "kehadiran_murid"

    id_kehadiran = db.Column(db.Integer, primary_key=True)

    id_jadwal = db.Column(db.Integer, db.ForeignKey("jadwal.id_jadwal"), nullable=False)
    id_murid = db.Column(db.Integer, db.ForeignKey("murid.id_murid"), nullable=False)

    tanggal = db.Column(db.Date, default=date.today, nullable=False)  # ✅ TAMBAH INI
    pertemuan = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    jadwal = db.relationship("Jadwal", back_populates="kehadiran")
    murid = db.relationship("Murid", back_populates="kehadiran")