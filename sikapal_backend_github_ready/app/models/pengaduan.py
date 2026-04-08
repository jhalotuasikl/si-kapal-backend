from app.extensions import db
from datetime import datetime


class Pengaduan(db.Model):
    __tablename__ = "pengaduan"

    id_pengaduan = db.Column(db.Integer, primary_key=True)

    id_murid = db.Column(
        db.Integer,
        db.ForeignKey("murid.id_murid"),
        nullable=False
    )

    mode_pelaporan = db.Column(
        db.Enum("terbuka", "rahasia", "anonim", name="mode_pelaporan_enum"),
        nullable=False
    )

    kategori_pengaduan = db.Column(
        db.Enum(
            "akademik",
            "absensi",
            "nilai",
            "bullying",
            "fasilitas",
            "lainnya",
            name="kategori_pengaduan_enum"
        ),
        nullable=False
    )

    isi_pengaduan = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.Enum(
            "menunggu",
            "diproses",
            "selesai",
            "ditolak",
            name="status_pengaduan_enum"
        ),
        nullable=False,
        default="menunggu"
    )

    catatan_admin = db.Column(db.Text, nullable=True)

    tanggal_pengaduan = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    tanggal_ditindaklanjuti = db.Column(
        db.DateTime,
        nullable=True
    )

    # relasi ke murid
    murid = db.relationship("Murid", backref="pengaduan_list", lazy=True)

    def to_dict(self):
        return {
            "id_pengaduan": self.id_pengaduan,
            "id_murid": self.id_murid,
            "nama_murid": self.murid.nama_murid if self.murid else None,
            "nis": self.murid.nis if self.murid else None,
            "id_kelas": self.murid.id_kelas if self.murid else None,
            "nama_kelas": self.murid.kelas.nama_kelas if self.murid and self.murid.kelas else None,
            "mode_pelaporan": self.mode_pelaporan,
            "kategori_pengaduan": self.kategori_pengaduan,
            "isi_pengaduan": self.isi_pengaduan,
            "status": self.status,
            "catatan_admin": self.catatan_admin,
            "tanggal_pengaduan": self.tanggal_pengaduan.strftime("%Y-%m-%d %H:%M:%S") if self.tanggal_pengaduan else None,
            "tanggal_ditindaklanjuti": self.tanggal_ditindaklanjuti.strftime("%Y-%m-%d %H:%M:%S") if self.tanggal_ditindaklanjuti else None
        }