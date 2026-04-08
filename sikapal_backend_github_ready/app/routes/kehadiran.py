# app/routes/kehadiran.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import date

from app.extensions import db
from app.models.jadwal import Jadwal
from app.models.jadwal_guru import JadwalGuru
from app.models.kehadiran_murid import KehadiranMurid
from app.models.murid import Murid

kehadiran_bp = Blueprint("kehadiran", __name__)

def jadwal_milik_guru(id_jadwal: int, id_guru: int) -> bool:
    return db.session.query(JadwalGuru).filter_by(
        id_jadwal=id_jadwal,
        id_guru=id_guru
    ).first() is not None


# =====================================================
# INPUT ABSENSI MURID (BERDASARKAN JADWAL)
# =====================================================
@kehadiran_bp.route("/kehadiran", methods=["POST"])
@jwt_required()
def input_kehadiran():
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    data = request.json or {}

    id_jadwal = data.get("id_jadwal")
    id_murid = data.get("id_murid")
    pertemuan = data.get("pertemuan")
    status = data.get("status")
    tanggal_in = data.get("tanggal")  # opsional: kalau mau input tanggal manual

    if not all([id_jadwal, id_murid, pertemuan, status]):
        return jsonify({"message": "Data tidak lengkap"}), 400

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "ID guru tidak ditemukan"}), 400

    # ✅ validasi jadwal milik guru via jadwal_guru
    if not jadwal_milik_guru(int(id_jadwal), int(id_guru)):
        return jsonify({"message": "Jadwal tidak valid untuk guru ini"}), 403

    jadwal = Jadwal.query.get_or_404(id_jadwal)

    # ✅ validasi murid ada di kelas jadwal
    murid = Murid.query.get_or_404(id_murid)
    if murid.id_kelas != jadwal.id_kelas:
        return jsonify({"message": "Murid bukan di kelas jadwal ini"}), 403

    # tanggal default hari ini
    tgl = date.today()
    if tanggal_in:
        try:
            y, m, d = map(int, str(tanggal_in).split("-"))
            tgl = date(y, m, d)
        except:
            return jsonify({"message": "Format tanggal harus YYYY-MM-DD"}), 400

    # update / insert
    absen = KehadiranMurid.query.filter_by(
        id_jadwal=id_jadwal,
        id_murid=id_murid,
        pertemuan=pertemuan
    ).first()

    if absen:
        absen.status = status
        absen.tanggal = tgl
        db.session.commit()
        return jsonify({"message": "Absensi diperbarui"}), 200

    hadir = KehadiranMurid(
        id_jadwal=id_jadwal,
        id_murid=id_murid,
        pertemuan=pertemuan,
        status=status,
        tanggal=tgl
    )
    db.session.add(hadir)
    db.session.commit()

    return jsonify({"message": "Absensi tersimpan"}), 201


# =====================================================
# GET ABSEN MURID (PER JADWAL)
# =====================================================
@kehadiran_bp.route("/kehadiran/murid/<int:id_jadwal>", methods=["GET"])
@jwt_required()
def get_absen_murid(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "murid":
        return jsonify({"message": "Akses ditolak"}), 403

    id_murid = claims.get("id_murid")
    if not id_murid:
        return jsonify({"message": "ID murid tidak ditemukan"}), 400

    data = (KehadiranMurid.query
            .filter_by(id_jadwal=id_jadwal, id_murid=id_murid)
            .order_by(KehadiranMurid.pertemuan)
            .all())

    return jsonify([
        {
            "id_kehadiran": d.id_kehadiran,
            "pertemuan": d.pertemuan,
            "status": d.status,
            "tanggal": str(d.tanggal)
        } for d in data
    ]), 200


# =====================================================
# LAPORAN ABSENSI GURU PER JADWAL (opsional filter pertemuan)
# =====================================================
@kehadiran_bp.route("/guru/absensi/<int:id_jadwal>", methods=["GET"])
@jwt_required()
def laporan_guru(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "ID guru tidak ditemukan"}), 400

    if not jadwal_milik_guru(id_jadwal, id_guru):
        return jsonify({"message": "Jadwal tidak valid untuk guru ini"}), 403

    pertemuan = request.args.get("pertemuan")  # optional

    q = (db.session.query(KehadiranMurid, Murid)
         .join(Murid, Murid.id_murid == KehadiranMurid.id_murid)
         .filter(KehadiranMurid.id_jadwal == id_jadwal))

    if pertemuan:
        q = q.filter(KehadiranMurid.pertemuan == int(pertemuan))

    data = q.order_by(KehadiranMurid.pertemuan, Murid.nama_murid).all()

    result = []
    for absen, murid in data:
        result.append({
            "id_murid": murid.id_murid,
            "nis": murid.nis,
            "nama_murid": murid.nama_murid,
            "pertemuan": absen.pertemuan,
            "status": absen.status,
            "tanggal": str(absen.tanggal)
        })

    return jsonify(result), 200


# =====================================================
# ✅ REKAP ADMIN PER JADWAL (14 pertemuan)
# =====================================================
@kehadiran_bp.route("/admin/rekap-absensi/<int:id_jadwal>", methods=["GET"])
@jwt_required()
def rekap_admin(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Akses ditolak"}), 403

    data = (db.session.query(KehadiranMurid, Murid)
            .join(Murid, Murid.id_murid == KehadiranMurid.id_murid)
            .filter(KehadiranMurid.id_jadwal == id_jadwal)
            .order_by(Murid.id_murid, KehadiranMurid.pertemuan)
            .all())

    rekap = {}
    for absen, murid in data:
        if murid.id_murid not in rekap:
            rekap[murid.id_murid] = {
                "id_murid": murid.id_murid,
                "nis": murid.nis,
                "nama_murid": murid.nama_murid,
            }
            for i in range(1, 15):
                rekap[murid.id_murid][f"P{i}"] = ""

        rekap[murid.id_murid][f"P{absen.pertemuan}"] = absen.status

    return jsonify(list(rekap.values())), 200


# =====================================================
# ❌ ROUTE LAMA /absensi (SALAH) -> GANTI jadi rekap by jadwal+tanggal
# =====================================================
@kehadiran_bp.route("/absensi", methods=["GET"])
@jwt_required()
def get_absensi_by_jadwal_tanggal():
    """
    Query:
      - id_jadwal=1
      - tanggal=YYYY-MM-DD (opsional; default hari ini)
    """
    claims = get_jwt()
    role = claims.get("role")
    if role not in ["admin", "guru"]:
        return jsonify({"message": "Akses ditolak"}), 403

    id_jadwal = request.args.get("id_jadwal")
    if not id_jadwal:
        return jsonify({"message": "id_jadwal wajib"}), 400

    tanggal_str = request.args.get("tanggal")
    tgl = date.today()
    if tanggal_str:
        try:
            y, m, d = map(int, tanggal_str.split("-"))
            tgl = date(y, m, d)
        except:
            return jsonify({"message": "Format tanggal harus YYYY-MM-DD"}), 400

    data = (db.session.query(KehadiranMurid, Murid)
            .join(Murid, Murid.id_murid == KehadiranMurid.id_murid)
            .filter(KehadiranMurid.id_jadwal == int(id_jadwal),
                    KehadiranMurid.tanggal == tgl)
            .order_by(Murid.nama_murid)
            .all())

    return jsonify([
        {
            "id_kehadiran": a.id_kehadiran,
            "id_murid": m.id_murid,
            "nis": m.nis,
            "nama_murid": m.nama_murid,
            "pertemuan": a.pertemuan,
            "status": a.status,
            "tanggal": str(a.tanggal),
        } for a, m in data
    ]), 200

# =====================================================
# ✅ GURU: LIST PERTEMUAN YANG SUDAH DIINPUT PER JADWAL
# frontend: GET /api/guru/kehadiran/pertemuan/<id_jadwal>
# =====================================================
@kehadiran_bp.route("/guru/kehadiran/pertemuan/<int:id_jadwal>", methods=["GET"])
@jwt_required()
def get_pertemuan_terisi_guru(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "id_guru tidak ada di token"}), 400

    if not jadwal_milik_guru(id_jadwal, id_guru):
        return jsonify({"message": "Jadwal tidak valid"}), 403

    rows = (
        db.session.query(KehadiranMurid.pertemuan)
        .filter(KehadiranMurid.id_jadwal == id_jadwal)
        .distinct()
        .order_by(KehadiranMurid.pertemuan.asc())
        .all()
    )

    pertemuan_list = [r[0] for r in rows if r[0] is not None]

    return jsonify({
        "id_jadwal": id_jadwal,
        "pertemuan_terisi": pertemuan_list
    }), 200