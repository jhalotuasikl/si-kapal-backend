# app/routes/jadwal.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime

from app import db
from app.models.jadwal import Jadwal
from app.models.kelas import Kelas
from app.models.mata_pelajaran import MataPelajaran
from app.models.jadwal_guru import JadwalGuru
from app.models.guru import Guru
from app.models.murid import Murid

jadwal_bp = Blueprint("jadwal", __name__)

# =========================
# helper: cek jadwal milik guru login
# =========================
def jadwal_milik_guru(id_jadwal: int, id_guru: int) -> bool:
    return db.session.query(JadwalGuru).filter_by(
        id_jadwal=id_jadwal,
        id_guru=id_guru
    ).first() is not None


# =====================================================
# LIST JADWAL (FILTER) - ADMIN (opsional)
# =====================================================
@jadwal_bp.route("/jadwal", methods=["GET"])
@jwt_required()
def list_jadwal():
    claims = get_jwt()
    role = claims.get("role")

    id_kelas = request.args.get("id_kelas")
    hari = request.args.get("hari")

    query = Jadwal.query

    if id_kelas:
        query = query.filter_by(id_kelas=id_kelas)

    if hari:
        query = query.filter_by(hari=hari)

    data = query.order_by(Jadwal.hari, Jadwal.jam_mulai).all()

    return jsonify([
        {
            "id_jadwal": j.id_jadwal,
            "id_kelas": j.id_kelas,
            "id_mapel": j.id_mapel,
            "hari": j.hari,
            "jam_mulai": j.jam_mulai.strftime("%H:%M"),
            "jam_selesai": j.jam_selesai.strftime("%H:%M"),
        } for j in data
    ]), 200


# =====================================================
# DETAIL
# =====================================================
@jadwal_bp.route("/jadwal/<int:id_jadwal>", methods=["GET"])
@jwt_required()
def detail_jadwal(id_jadwal):
    j = Jadwal.query.get_or_404(id_jadwal)
    return jsonify({
        "id_jadwal": j.id_jadwal,
        "id_kelas": j.id_kelas,
        "id_mapel": j.id_mapel,
        "hari": j.hari,
        "jam_mulai": j.jam_mulai.strftime("%H:%M"),
        "jam_selesai": j.jam_selesai.strftime("%H:%M")
    }), 200


# =====================================================
# CREATE (ADMIN ONLY)
# =====================================================
@jadwal_bp.route("/jadwal", methods=["POST"])
@jwt_required()
def create_jadwal():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Hanya admin"}), 403

    data = request.json or {}

    wajib = ["id_kelas", "id_mapel", "hari", "jam_mulai", "jam_selesai"]
    for f in wajib:
        if not data.get(f):
            return jsonify({"message": f"{f} wajib"}), 400

    # parse jam
    try:
        jam_mulai = datetime.strptime(data["jam_mulai"], "%H:%M").time()
        jam_selesai = datetime.strptime(data["jam_selesai"], "%H:%M").time()
    except:
        return jsonify({"message": "Format jam HH:MM"}), 400

    if jam_mulai >= jam_selesai:
        return jsonify({"message": "Jam tidak valid"}), 400

    kelas = Kelas.query.get(data["id_kelas"])
    mapel = MataPelajaran.query.get(data["id_mapel"])
    if not kelas or not mapel:
        return jsonify({"message": "Kelas / Mapel invalid"}), 400

    if mapel not in kelas.mapel:
        return jsonify({"message": "Mapel belum di kelas"}), 400

    jadwal = Jadwal(
        id_kelas=data["id_kelas"],
        id_mapel=data["id_mapel"],
        hari=str(data["hari"]).lower(),
        jam_mulai=jam_mulai,
        jam_selesai=jam_selesai
    )

    db.session.add(jadwal)
    db.session.commit()

    return jsonify({"message": "Jadwal dibuat", "id_jadwal": jadwal.id_jadwal}), 201


# =====================================================
# JADWAL HARI INI (GURU LOGIN) - FIX hari Indonesia
# =====================================================
@jadwal_bp.route("/guru/jadwal-hari-ini", methods=["GET"])
@jwt_required()
def jadwal_hari_ini():
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Khusus guru"}), 403

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "ID guru tidak ditemukan"}), 400

    # mapping weekday -> hari indonesia
    map_hari = {
        "monday": "senin",
        "tuesday": "selasa",
        "wednesday": "rabu",
        "thursday": "kamis",
        "friday": "jumat",
        "saturday": "sabtu",
        "sunday": "minggu"
    }
    hari_ini = map_hari[datetime.now().strftime("%A").lower()]

    data = (
        db.session.query(Jadwal, Kelas, MataPelajaran)
        .join(JadwalGuru, Jadwal.id_jadwal == JadwalGuru.id_jadwal)
        .join(Kelas, Jadwal.id_kelas == Kelas.id_kelas)
        .join(MataPelajaran, Jadwal.id_mapel == MataPelajaran.id_mapel)
        .filter(JadwalGuru.id_guru == id_guru, Jadwal.hari == hari_ini)
        .order_by(Jadwal.jam_mulai)
        .all()
    )

    return jsonify([
        {
            "id_jadwal": j.id_jadwal,
            "hari": j.hari,
            "jam_mulai": j.jam_mulai.strftime("%H:%M"),
            "jam_selesai": j.jam_selesai.strftime("%H:%M"),
            "kelas": k.nama_kelas,
            "mapel": m.nama_mapel,
        } for j, k, m in data
    ]), 200


# =====================================================
# JADWAL GURU (SEMUA) - sudah benar (pakai jadwal_guru)
# =====================================================
@jadwal_bp.route("/guru/jadwal", methods=["GET"])
@jwt_required()
def get_jadwal_guru():
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Khusus guru"}), 403

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "ID guru tidak ditemukan"}), 400

    data = (
        db.session.query(Jadwal, Kelas, MataPelajaran)
        .join(JadwalGuru, Jadwal.id_jadwal == JadwalGuru.id_jadwal)
        .join(Kelas, Jadwal.id_kelas == Kelas.id_kelas)
        .join(MataPelajaran, Jadwal.id_mapel == MataPelajaran.id_mapel)
        .filter(JadwalGuru.id_guru == id_guru)
        .order_by(Jadwal.hari, Jadwal.jam_mulai)
        .all()
    )

    return jsonify([
        {
            "id_jadwal": j.id_jadwal,
            "hari": j.hari,
            "jam_mulai": j.jam_mulai.strftime("%H:%M"),
            "jam_selesai": j.jam_selesai.strftime("%H:%M"),
            "kelas": k.nama_kelas,
            "mapel": m.nama_mapel,
        } for j, k, m in data
    ]), 200


# =====================================================
# ✅ MURID BY JADWAL (INI YANG DIPAKAI FLUTTER)
# =====================================================
@jadwal_bp.route("/guru/jadwal/<int:id_jadwal>/murid", methods=["GET"])
@jwt_required()
def get_murid_by_jadwal(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Khusus guru"}), 403

    id_guru = claims.get("id_guru")

    # validasi jadwal milik guru (via jadwal_guru)
    from app.models.jadwal_guru import JadwalGuru
    cek = JadwalGuru.query.filter_by(id_jadwal=id_jadwal, id_guru=id_guru).first()
    if not cek:
        return jsonify({"message": "Jadwal tidak valid"}), 403

    jadwal = Jadwal.query.get_or_404(id_jadwal)

    from app.models.murid import Murid
    murid = Murid.query.filter_by(id_kelas=jadwal.id_kelas).order_by(Murid.nama_murid.asc()).all()

    return jsonify([
        {"id_murid": m.id_murid, "nama_murid": m.nama_murid, "nis": m.nis}
        for m in murid
    ]), 200


# =====================================================
# GET JADWAL PER KELAS (ADMIN/GURU/MURID)
# Dipakai DetailKelasPage -> KelasService.getJadwalKelas()
# =====================================================
@jadwal_bp.route("/jadwal/kelas/<int:id_kelas>", methods=["GET"])
@jwt_required()
def jadwal_by_kelas(id_kelas):
    claims = get_jwt()

    if claims.get("role") not in ["admin", "guru", "murid"]:
        return jsonify({"message": "Akses ditolak"}), 403

    data = db.session.query(Jadwal).filter_by(id_kelas=id_kelas).order_by(
        Jadwal.hari.asc(),
        Jadwal.jam_mulai.asc()
    ).all()

    result = []

    for j in data:
        # ambil semua guru yang di-assign ke jadwal ini (bisa kosong)
        guru_list = [jg.guru for jg in j.jadwal_guru] if j.jadwal_guru else []
        guru_names = ", ".join([g.nama_guru for g in guru_list]) if guru_list else None
        guru_ids = [g.id_guru for g in guru_list] if guru_list else []

        result.append({
            "id_jadwal": j.id_jadwal,
            "id_kelas": j.id_kelas,
            "id_mapel": j.id_mapel,
            "nama_mapel": j.mapel.nama_mapel if j.mapel else None,
            "hari": j.hari,
            "jam_mulai": j.jam_mulai.strftime("%H:%M") if j.jam_mulai else None,
            "jam_selesai": j.jam_selesai.strftime("%H:%M") if j.jam_selesai else None,

            # guru bisa lebih dari 1
            "nama_guru": guru_names,
            "guru_ids": guru_ids,
        })

    return jsonify(result), 200


# =====================================================
# ADMIN: ASSIGN GURU KE JADWAL (MANY-TO-MANY)
# Endpoint: POST /api/admin/jadwal/<id_jadwal>/guru
# Body: { "id_guru": 1 }
# =====================================================
@jadwal_bp.route("/admin/jadwal/<int:id_jadwal>/guru", methods=["POST"])
@jwt_required()
def admin_assign_guru_to_jadwal(id_jadwal):
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"message": "Hanya admin"}), 403

    data = request.json or {}
    id_guru = data.get("id_guru")

    if not id_guru:
        return jsonify({"message": "id_guru wajib"}), 400

    jadwal = Jadwal.query.get_or_404(id_jadwal)

    guru = Guru.query.get_or_404(id_guru)

    # cek duplikat
    exist = JadwalGuru.query.filter_by(id_jadwal=id_jadwal, id_guru=id_guru).first()
    if exist:
        return jsonify({"message": "Guru sudah di-assign"}), 409

    link = JadwalGuru(id_jadwal=id_jadwal, id_guru=id_guru)
    db.session.add(link)
    db.session.commit()

    return jsonify({
        "message": "Guru berhasil di-assign ke jadwal",
        "id_jadwal": id_jadwal,
        "id_guru": id_guru,
        "nama_guru": guru.nama_guru,
    }), 201


# =====================================================
# ADMIN: UNASSIGN GURU DARI JADWAL
# Endpoint: DELETE /api/admin/jadwal/<id_jadwal>/guru/<id_guru>
# =====================================================
@jadwal_bp.route("/admin/jadwal/<int:id_jadwal>/guru/<int:id_guru>", methods=["DELETE"])
@jwt_required()
def admin_unassign_guru_from_jadwal(id_jadwal, id_guru):
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"message": "Hanya admin"}), 403

    link = JadwalGuru.query.filter_by(id_jadwal=id_jadwal, id_guru=id_guru).first()
    if not link:
        return jsonify({"message": "Relasi tidak ada"}), 404

    db.session.delete(link)
    db.session.commit()

    return jsonify({"message": "Guru dihapus dari jadwal"}), 200

@jadwal_bp.route("/admin/jadwal/<int:id_jadwal>/guru", methods=["GET"])
@jwt_required()
def admin_get_guru_jadwal(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Hanya admin"}), 403

    data = (
        db.session.query(Guru)
        .join(JadwalGuru, Guru.id_guru == JadwalGuru.id_guru)
        .filter(JadwalGuru.id_jadwal == id_jadwal)
        .order_by(Guru.nama_guru.asc())
        .all()
    )

    return jsonify([
        {"id_guru": g.id_guru, "nama_guru": g.nama_guru}
        for g in data
    ]), 200
@jadwal_bp.route("/admin/jadwal/<int:id_jadwal>/murid", methods=["GET"])
@jwt_required()
def admin_get_murid_by_jadwal(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Hanya admin"}), 403

    jadwal = Jadwal.query.get_or_404(id_jadwal)

    murid = Murid.query.filter_by(id_kelas=jadwal.id_kelas)\
        .order_by(Murid.nama_murid.asc()).all()

    return jsonify([
        {"id_murid": m.id_murid, "nama_murid": m.nama_murid, "nis": m.nis}
        for m in murid
    ]), 200


# =====================================================
# JADWAL HARI INI (MURID LOGIN) - REALTIME DASHBOARD
# =====================================================
@jadwal_bp.route("/murid/jadwal-hari-ini", methods=["GET"])
@jwt_required()
def jadwal_hari_ini_murid():
    claims = get_jwt()
    if claims.get("role") != "murid":
        return jsonify({"message": "Khusus murid"}), 403

    id_murid = claims.get("id_murid")
    if not id_murid:
        return jsonify({"message": "ID murid tidak ditemukan"}), 400

    murid = Murid.query.get(id_murid)
    if not murid:
        return jsonify({"message": "Murid tidak ditemukan"}), 404

    if not murid.id_kelas:
        return jsonify([]), 200

    map_hari = {
        "monday": "senin",
        "tuesday": "selasa",
        "wednesday": "rabu",
        "thursday": "kamis",
        "friday": "jumat",
        "saturday": "sabtu",
        "sunday": "minggu"
    }
    hari_ini = map_hari[datetime.now().strftime("%A").lower()]

    data = (
        db.session.query(Jadwal, Kelas, MataPelajaran)
        .join(Kelas, Jadwal.id_kelas == Kelas.id_kelas)
        .join(MataPelajaran, Jadwal.id_mapel == MataPelajaran.id_mapel)
        .filter(
            Jadwal.id_kelas == murid.id_kelas,
            Jadwal.hari == hari_ini
        )
        .order_by(Jadwal.jam_mulai.asc())
        .all()
    )

    result = []

    for j, k, m in data:
        guru_list = [jg.guru for jg in j.jadwal_guru] if j.jadwal_guru else []
        nama_guru = ", ".join([g.nama_guru for g in guru_list]) if guru_list else "-"

        result.append({
            "id_jadwal": j.id_jadwal,
            "hari": j.hari,
            "jam_mulai": j.jam_mulai.strftime("%H:%M"),
            "jam_selesai": j.jam_selesai.strftime("%H:%M"),
            "kelas": k.nama_kelas,
            "mapel": m.nama_mapel,
            "guru": nama_guru,
        })

    return jsonify(result), 200