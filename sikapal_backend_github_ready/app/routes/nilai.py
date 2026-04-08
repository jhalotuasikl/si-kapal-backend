# app/routes/nilai.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models.nilai import Nilai
from app.models.murid import Murid
from app.models.jadwal import Jadwal
from app.models.jadwal_guru import JadwalGuru
from app.models.kelas import Kelas
from app.models.mata_pelajaran import MataPelajaran
from app.models.guru import Guru

nilai_bp = Blueprint("nilai", __name__)

def konversi_huruf(nilai):
    if nilai >= 85: return "A"
    if nilai >= 75: return "B"
    if nilai >= 65: return "C"
    if nilai >= 50: return "D"
    return "E"

def jadwal_milik_guru(id_jadwal: int, id_guru: int) -> bool:
    return db.session.query(JadwalGuru).filter_by(
        id_jadwal=id_jadwal,
        id_guru=id_guru
    ).first() is not None


# =====================================================
# ✅ INPUT NILAI (BERDASARKAN JADWAL)
# =====================================================
@nilai_bp.route("/guru/nilai", methods=["POST"])
@jwt_required()
def input_nilai():
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    data = request.json or {}

    id_jadwal = data.get("id_jadwal")
    id_murid = data.get("id_murid")
    semester = data.get("semester")
    tahun_ajaran = data.get("tahun_ajaran")
    nilai_angka = data.get("nilai_angka")

    if not all([id_jadwal, id_murid, semester, tahun_ajaran, nilai_angka]):
        return jsonify({"message": "Data tidak lengkap"}), 400

    try:
        nilai = float(nilai_angka)
    except:
        return jsonify({"message": "Nilai harus angka"}), 400

    if nilai < 0 or nilai > 100:
        return jsonify({"message": "Nilai 0 - 100"}), 400

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "id_guru tidak ada di token"}), 400

    # ✅ validasi jadwal milik guru
    if not jadwal_milik_guru(int(id_jadwal), int(id_guru)):
        return jsonify({"message": "Jadwal tidak valid"}), 403

    jadwal = Jadwal.query.get_or_404(id_jadwal)

    # ✅ validasi murid sesuai kelas jadwal
    murid = Murid.query.get_or_404(id_murid)
    if murid.id_kelas != jadwal.id_kelas:
        return jsonify({"message": "Murid bukan kelas ini"}), 403

    # ✅ cek duplikat (jadwal+murid+semester+tahun)
    cek = Nilai.query.filter_by(
        id_jadwal=id_jadwal,
        id_murid=id_murid,
        semester=semester,
        tahun_ajaran=tahun_ajaran
    ).first()

    if cek:
        return jsonify({"message": "Nilai sudah ada, gunakan edit"}), 409

    huruf = konversi_huruf(nilai)

    new = Nilai(
        id_jadwal=id_jadwal,
        id_murid=id_murid,
        semester=semester,
        tahun_ajaran=tahun_ajaran,
        nilai_angka=nilai,
        nilai_huruf=huruf,
        status_kirim=False
    )

    db.session.add(new)
    db.session.commit()

    return jsonify({
        "message": "Nilai tersimpan",
        "id_nilai": new.id_nilai,
        "huruf": huruf
    }), 201


# =====================================================
# ✅ NILAI MURID (JWT) - join ke guru via jadwal_guru
# =====================================================
@nilai_bp.route("/murid/nilai", methods=["GET"])
@jwt_required()
def nilai_murid():
    claims = get_jwt()
    if claims.get("role") != "murid":
        return jsonify({"message": "Akses ditolak"}), 403

    id_murid = claims.get("id_murid")
    if not id_murid:
        return jsonify({"message": "id_murid tidak ada di token"}), 400

    data = (
        db.session.query(Nilai, Jadwal, Kelas, MataPelajaran, Guru)
        .join(Jadwal, Jadwal.id_jadwal == Nilai.id_jadwal)
        .join(Kelas, Kelas.id_kelas == Jadwal.id_kelas)
        .join(MataPelajaran, MataPelajaran.id_mapel == Jadwal.id_mapel)
        .outerjoin(JadwalGuru, JadwalGuru.id_jadwal == Jadwal.id_jadwal)
        .outerjoin(Guru, Guru.id_guru == JadwalGuru.id_guru)
        .filter(Nilai.id_murid == id_murid)
        .order_by(Nilai.tahun_ajaran.desc(), Nilai.semester.desc())
        .all()
    )

    return jsonify([
        {
            "id_nilai": n.id_nilai,
            "semester": n.semester,
            "tahun": n.tahun_ajaran,
            "nilai": n.nilai_angka,
            "huruf": n.nilai_huruf,
            "kelas": k.nama_kelas,
            "mapel": m.nama_mapel,
            "guru": g.nama_guru if g else None
        }
        for n, j, k, m, g in data
    ]), 200


# =====================================================
# ✅ NILAI ADMIN / GURU (filter tetap)
# =====================================================
@nilai_bp.route("/admin/nilai", methods=["GET"])
@jwt_required()
def nilai_admin():
    claims = get_jwt()
    if claims.get("role") not in ["admin", "guru"]:
        return jsonify({"message": "Akses ditolak"}), 403

    q = (
        db.session.query(Nilai, Murid, Jadwal, Kelas, MataPelajaran, Guru)
        .join(Murid, Murid.id_murid == Nilai.id_murid)
        .join(Jadwal, Jadwal.id_jadwal == Nilai.id_jadwal)
        .join(Kelas, Kelas.id_kelas == Jadwal.id_kelas)
        .join(MataPelajaran, MataPelajaran.id_mapel == Jadwal.id_mapel)
        .outerjoin(JadwalGuru, JadwalGuru.id_jadwal == Jadwal.id_jadwal)
        .outerjoin(Guru, Guru.id_guru == JadwalGuru.id_guru)
    )

    if request.args.get("id_kelas"):
        q = q.filter(Jadwal.id_kelas == request.args["id_kelas"])

    if request.args.get("id_mapel"):
        q = q.filter(Jadwal.id_mapel == request.args["id_mapel"])

    if request.args.get("id_murid"):
        q = q.filter(Nilai.id_murid == request.args["id_murid"])

    data = q.order_by(Nilai.tahun_ajaran.desc(), Nilai.semester.desc()).all()

    return jsonify([
        {
            "id": n.id_nilai,
            "id_murid": mur.id_murid,
            "murid": mur.nama_murid,
            "nis": mur.nis,
            "kelas": k.nama_kelas,
            "mapel": m.nama_mapel,
            "guru": g.nama_guru if g else None,
            "semester": n.semester,
            "tahun": n.tahun_ajaran,
            "nilai": n.nilai_angka,
            "huruf": n.nilai_huruf,
            "kirim": n.status_kirim
        }
        for n, mur, j, k, m, g in data
    ]), 200


# =====================================================
# ✅ EDIT NILAI - validasi via jadwal_guru
# =====================================================
@nilai_bp.route("/guru/nilai/<int:id_nilai>", methods=["PUT"])
@jwt_required()
def edit_nilai(id_nilai):
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")
    nilai = Nilai.query.get_or_404(id_nilai)

    if not jadwal_milik_guru(nilai.id_jadwal, id_guru):
        return jsonify({"message": "Bukan nilai anda"}), 403

    data = request.json or {}

    if "nilai_angka" in data:
        try:
            angka = float(data["nilai_angka"])
        except:
            return jsonify({"message": "Nilai invalid"}), 400

        if angka < 0 or angka > 100:
            return jsonify({"message": "Nilai 0-100"}), 400

        nilai.nilai_angka = angka
        nilai.nilai_huruf = konversi_huruf(angka)

    if "semester" in data:
        nilai.semester = data["semester"]

    if "tahun_ajaran" in data:
        nilai.tahun_ajaran = data["tahun_ajaran"]

    db.session.commit()
    return jsonify({"message": "Nilai diperbarui"}), 200


# =====================================================
# ✅ DELETE NILAI - validasi via jadwal_guru
# =====================================================
@nilai_bp.route("/guru/nilai/<int:id_nilai>", methods=["DELETE"])
@jwt_required()
def delete_nilai(id_nilai):
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")
    nilai = Nilai.query.get_or_404(id_nilai)

    if not jadwal_milik_guru(nilai.id_jadwal, id_guru):
        return jsonify({"message": "Bukan nilai anda"}), 403

    db.session.delete(nilai)
    db.session.commit()
    return jsonify({"message": "Nilai dihapus"}), 200


# =====================================================
# ✅ KIRIM KE ADMIN (guru)
# =====================================================
@nilai_bp.route("/admin/nilai/kirim/<int:id_nilai>", methods=["POST"])
@jwt_required()
def kirim_admin(id_nilai):
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")
    nilai = Nilai.query.get_or_404(id_nilai)

    if not jadwal_milik_guru(nilai.id_jadwal, id_guru):
        return jsonify({"message": "Bukan nilai anda"}), 403

    nilai.status_kirim = True
    db.session.commit()
    return jsonify({"message": "Nilai dikirim ke admin"}), 200

# =====================================================
# ✅ GURU: REKAP NILAI BELUM DIKIRIM
# =====================================================
@nilai_bp.route("/guru/nilai/rekap", methods=["GET"])
@jwt_required()
def rekap_nilai_guru():
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")

    id_kelas = request.args.get("id_kelas", type=int)
    id_mapel = request.args.get("id_mapel", type=int)

    q = (
        db.session.query(Nilai, Murid, Jadwal, Kelas, MataPelajaran)
        .join(Murid, Murid.id_murid == Nilai.id_murid)
        .join(Jadwal, Jadwal.id_jadwal == Nilai.id_jadwal)
        .join(Kelas, Kelas.id_kelas == Jadwal.id_kelas)
        .join(MataPelajaran, MataPelajaran.id_mapel == Jadwal.id_mapel)
        .join(JadwalGuru, JadwalGuru.id_jadwal == Jadwal.id_jadwal)
        .filter(JadwalGuru.id_guru == id_guru)
        .filter(Nilai.status_kirim == False)
    )

    if id_kelas:
        q = q.filter(Jadwal.id_kelas == id_kelas)

    if id_mapel:
        q = q.filter(Jadwal.id_mapel == id_mapel)

    data = q.all()

    return jsonify([
        {
            "id_nilai": n.id_nilai,
            "id_jadwal": j.id_jadwal,
            "nama_murid": mur.nama_murid,
            "nis": mur.nis,
            "nama_kelas": k.nama_kelas,
            "nama_mapel": m.nama_mapel,
            "nilai_angka": n.nilai_angka,
            "nilai_huruf": n.nilai_huruf,
        }
        for n, mur, j, k, m in data
    ]), 200

@nilai_bp.route("/guru/nilai/<int:id_jadwal>", methods=["GET"])
@jwt_required()
def get_murid_by_jadwal(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "id_guru tidak ada di token"}), 400

    # validasi jadwal milik guru
    if not jadwal_milik_guru(id_jadwal, id_guru):
        return jsonify({"message": "Jadwal tidak valid"}), 403

    jadwal = Jadwal.query.get_or_404(id_jadwal)

    murid_list = Murid.query.filter_by(id_kelas=jadwal.id_kelas).all()

    return jsonify([
        {
            "id_murid": m.id_murid,
            "nama_murid": m.nama_murid,
            "nis": getattr(m, "nis", None)
        }
        for m in murid_list
    ]), 200

# =====================================================
# ✅ GURU: LIST NILAI BERDASARKAN JADWAL
# frontend: GET /api/guru/nilai/jadwal/<id_jadwal>
# =====================================================
@nilai_bp.route("/guru/nilai/jadwal/<int:id_jadwal>", methods=["GET"])
@jwt_required()
def get_nilai_by_jadwal_guru(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "id_guru tidak ada di token"}), 400

    if not jadwal_milik_guru(id_jadwal, id_guru):
        return jsonify({"message": "Jadwal tidak valid"}), 403

    data = (
        db.session.query(Nilai, Murid, Jadwal, Kelas, MataPelajaran, Guru)
        .join(Murid, Murid.id_murid == Nilai.id_murid)
        .join(Jadwal, Jadwal.id_jadwal == Nilai.id_jadwal)
        .join(Kelas, Kelas.id_kelas == Jadwal.id_kelas)
        .join(MataPelajaran, MataPelajaran.id_mapel == Jadwal.id_mapel)
        .outerjoin(JadwalGuru, JadwalGuru.id_jadwal == Jadwal.id_jadwal)
        .outerjoin(Guru, Guru.id_guru == JadwalGuru.id_guru)
        .filter(Nilai.id_jadwal == id_jadwal)
        .order_by(Murid.nama_murid.asc())
        .all()
    )

    return jsonify([
        {
            "id": n.id_nilai,
            "id_nilai": n.id_nilai,
            "id_jadwal": j.id_jadwal,
            "id_murid": mur.id_murid,
            "murid": mur.nama_murid,
            "nis": mur.nis,
            "kelas": k.nama_kelas,
            "mapel": m.nama_mapel,
            "guru": g.nama_guru if g else None,
            "semester": n.semester,
            "tahun": n.tahun_ajaran,
            "nilai": n.nilai_angka,
            "huruf": n.nilai_huruf,
            "kirim": n.status_kirim
        }
        for n, mur, j, k, m, g in data
    ]), 200


# =====================================================
# ✅ GURU: KIRIM SEMUA NILAI DALAM 1 JADWAL KE ADMIN
# frontend: POST /api/guru/nilai/kirim/<id_jadwal>
# =====================================================
@nilai_bp.route("/guru/nilai/kirim/<int:id_jadwal>", methods=["POST"])
@jwt_required()
def kirim_semua_nilai_jadwal_ke_admin(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "id_guru tidak ada di token"}), 400

    if not jadwal_milik_guru(id_jadwal, id_guru):
        return jsonify({"message": "Jadwal tidak valid"}), 403

    nilai_list = Nilai.query.filter_by(id_jadwal=id_jadwal).all()

    if not nilai_list:
        return jsonify({"message": "Belum ada nilai pada jadwal ini"}), 404

    for n in nilai_list:
        n.status_kirim = True

    db.session.commit()

    return jsonify({
        "message": "Semua nilai pada jadwal berhasil dikirim ke admin",
        "id_jadwal": id_jadwal,
        "jumlah": len(nilai_list)
    }), 200


# =====================================================
# ✅ ADMIN: LIHAT NILAI TERKIRIM BERDASARKAN JADWAL
# frontend: GET /api/admin/nilai/jadwal/<id_jadwal>
# =====================================================
@nilai_bp.route("/admin/nilai/jadwal/<int:id_jadwal>", methods=["GET"])
@jwt_required()
def admin_nilai_by_jadwal(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Akses ditolak"}), 403

    data = (
        db.session.query(Nilai, Murid, Jadwal, Kelas, MataPelajaran, Guru)
        .join(Murid, Murid.id_murid == Nilai.id_murid)
        .join(Jadwal, Jadwal.id_jadwal == Nilai.id_jadwal)
        .join(Kelas, Kelas.id_kelas == Jadwal.id_kelas)
        .join(MataPelajaran, MataPelajaran.id_mapel == Jadwal.id_mapel)
        .outerjoin(JadwalGuru, JadwalGuru.id_jadwal == Jadwal.id_jadwal)
        .outerjoin(Guru, Guru.id_guru == JadwalGuru.id_guru)
        .filter(Nilai.id_jadwal == id_jadwal)
        .filter(Nilai.status_kirim == True)
        .order_by(Murid.nama_murid.asc())
        .all()
    )

    return jsonify([
        {
            "id": n.id_nilai,
            "id_nilai": n.id_nilai,
            "id_jadwal": j.id_jadwal,
            "id_murid": mur.id_murid,
            "murid": mur.nama_murid,
            "nis": mur.nis,
            "kelas": k.nama_kelas,
            "mapel": m.nama_mapel,
            "guru": g.nama_guru if g else None,
            "semester": n.semester,
            "tahun": n.tahun_ajaran,
            "nilai": n.nilai_angka,
            "huruf": n.nilai_huruf,
            "kirim": n.status_kirim
        }
        for n, mur, j, k, m, g in data
    ]), 200


# =====================================================
# ✅ ADMIN: LIST SEMUA JADWAL
# frontend: GET /api/jadwal
# kalau route ini belum ada di jadwal.py, bisa pakai sementara di sini
# =====================================================
@nilai_bp.route("/jadwal", methods=["GET"])
@jwt_required()
def semua_jadwal():
    claims = get_jwt()
    if claims.get("role") not in ["admin", "guru"]:
        return jsonify({"message": "Akses ditolak"}), 403

    data = (
        db.session.query(Jadwal, Kelas, MataPelajaran)
        .join(Kelas, Kelas.id_kelas == Jadwal.id_kelas)
        .join(MataPelajaran, MataPelajaran.id_mapel == Jadwal.id_mapel)
        .order_by(Kelas.nama_kelas.asc(), MataPelajaran.nama_mapel.asc())
        .all()
    )

    return jsonify([
        {
            "id_jadwal": j.id_jadwal,
            "id_kelas": j.id_kelas,
            "id_mapel": j.id_mapel,
            "kelas": k.nama_kelas,
            "nama_kelas": k.nama_kelas,
            "mapel": m.nama_mapel,
            "nama_mapel": m.nama_mapel,
            "hari": j.hari,
            "jam_mulai": str(j.jam_mulai)[:5] if j.jam_mulai else "",
            "jam_selesai": str(j.jam_selesai)[:5] if j.jam_selesai else "",
        }
        for j, k, m in data
    ]), 200