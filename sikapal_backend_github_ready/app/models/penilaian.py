from app.extensions import db

class PenilaianGuru(db.Model):
    __tablename__ = "penilaian_guru"

    id_penilaian = db.Column(db.Integer, primary_key=True)
    id_guru = db.Column(db.Integer)
    id_murid = db.Column(db.Integer)
    skor = db.Column(db.Integer)
    komentar = db.Column(db.Text)
