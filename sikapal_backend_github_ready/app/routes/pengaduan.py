from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from datetime import datetime

from app.extensions import db
from app.models.pengaduan import Pengaduan
from app.models.murid import Murid

pengaduan_bp = Blueprint("pengaduan", __name__)


# =========================================================
# MURID: KIRIM PENGADUAN
# POST /api/pengaduan
# =========================================================
@pengaduan_bp.route("/pengaduan", methods=["POST"])
@jwt_required()
def create_pengaduan():
    claims = get_jwt()
    identity = get_jwt_identity()

    if claims.get("role") != "murid":
        return jsonify({"message": "Hanya murid yang dapat membuat pengaduan"}), 403

    data = request.get_json()

    mode_pelaporan = data.get("mode_pelaporan")
    kategori_pengaduan = data.get("kategori_pengaduan")
    isi_pengaduan = data.get("isi_pengaduan")

    if not mode_pelaporan:
        return jsonify({"message": "mode_pelaporan wajib diisi"}), 400

    if not kategori_pengaduan:
        return jsonify({"message": "kategori_pengaduan wajib diisi"}), 400

    if not isi_pengaduan or not str(isi_pengaduan).strip():
        return jsonify({"message": "isi_pengaduan wajib diisi"}), 400

    mode_valid = ["terbuka", "rahasia", "anonim"]
    kategori_valid = ["akademik", "absensi", "nilai", "bullying", "fasilitas", "lainnya"]

    if mode_pelaporan not in mode_valid:
        return jsonify({"message": "mode_pelaporan tidak valid"}), 400

    if kategori_pengaduan not in kategori_valid:
        return jsonify({"message": "kategori_pengaduan tidak valid"}), 400

    # ambil id_murid dari token
    id_murid = claims.get("id_murid")

    # fallback kalau token belum simpan id_murid
    if not id_murid:
        murid = Murid.query.filter_by(id_user=identity).first()
        if not murid:
            return jsonify({"message": "Data murid tidak ditemukan"}), 404
        id_murid = murid.id_murid

    pengaduan = Pengaduan(
        id_murid=id_murid,
        mode_pelaporan=mode_pelaporan,
        kategori_pengaduan=kategori_pengaduan,
        isi_pengaduan=isi_pengaduan.strip(),
        status="menunggu"
    )

    db.session.add(pengaduan)
    db.session.commit()

    return jsonify({
        "message": "Pengaduan berhasil dikirim",
        "data": pengaduan.to_dict()
    }), 201


# =========================================================
# MURID: LIHAT PENGADUAN SENDIRI
# GET /api/pengaduan/saya
# =========================================================
@pengaduan_bp.route("/pengaduan/saya", methods=["GET"])
@jwt_required()
def get_pengaduan_saya():
    claims = get_jwt()
    identity = get_jwt_identity()

    if claims.get("role") != "murid":
        return jsonify({"message": "Hanya murid yang dapat melihat pengaduannya"}), 403

    id_murid = claims.get("id_murid")

    if not id_murid:
        murid = Murid.query.filter_by(id_user=identity).first()
        if not murid:
            return jsonify({"message": "Data murid tidak ditemukan"}), 404
        id_murid = murid.id_murid

    data = Pengaduan.query.filter_by(id_murid=id_murid)\
        .order_by(Pengaduan.id_pengaduan.desc())\
        .all()

    return jsonify([item.to_dict() for item in data]), 200


# =========================================================
# ADMIN: LIHAT SEMUA PENGADUAN
# GET /api/admin/pengaduan
# optional:
# ?status=menunggu
# ?kategori=absensi
# =========================================================
@pengaduan_bp.route("/admin/pengaduan", methods=["GET"])
@jwt_required()
def get_semua_pengaduan():
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"message": "Hanya admin"}), 403

    status = request.args.get("status")
    kategori = request.args.get("kategori")

    q = Pengaduan.query

    if status:
        q = q.filter(Pengaduan.status == status)

    if kategori:
        q = q.filter(Pengaduan.kategori_pengaduan == kategori)

    data = q.order_by(Pengaduan.id_pengaduan.desc()).all()

    hasil = []
    for item in data:
        row = item.to_dict()

        # kalau anonim, sembunyikan identitas
        if item.mode_pelaporan == "anonim":
            row["nama_murid"] = "Anonim"
            row["nis"] = None
            row["id_murid"] = None
            row["id_kelas"] = None
            row["nama_kelas"] = None

        hasil.append(row)

    return jsonify(hasil), 200


# =========================================================
# ADMIN: DETAIL PENGADUAN
# GET /api/admin/pengaduan/<id_pengaduan>
# =========================================================
@pengaduan_bp.route("/admin/pengaduan/<int:id_pengaduan>", methods=["GET"])
@jwt_required()
def detail_pengaduan(id_pengaduan):
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"message": "Hanya admin"}), 403

    item = Pengaduan.query.get(id_pengaduan)
    if not item:
        return jsonify({"message": "Pengaduan tidak ditemukan"}), 404

    row = item.to_dict()

    if item.mode_pelaporan == "anonim":
        row["nama_murid"] = "Anonim"
        row["nis"] = None
        row["id_murid"] = None
        row["id_kelas"] = None
        row["nama_kelas"] = None

    return jsonify(row), 200


# =========================================================
# ADMIN: UPDATE STATUS / CATATAN
# PUT /api/admin/pengaduan/<id_pengaduan>
# =========================================================
@pengaduan_bp.route("/admin/pengaduan/<int:id_pengaduan>", methods=["PUT"])
@jwt_required()
def update_pengaduan(id_pengaduan):
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"message": "Hanya admin"}), 403

    item = Pengaduan.query.get(id_pengaduan)
    if not item:
        return jsonify({"message": "Pengaduan tidak ditemukan"}), 404

    data = request.get_json()

    status_baru = data.get("status")
    catatan_admin = data.get("catatan_admin")

    status_valid = ["menunggu", "diproses", "selesai", "ditolak"]

    if status_baru and status_baru not in status_valid:
        return jsonify({"message": "status tidak valid"}), 400

    if status_baru:
        item.status = status_baru

    if catatan_admin is not None:
        item.catatan_admin = catatan_admin.strip() if str(catatan_admin).strip() else None

    item.tanggal_ditindaklanjuti = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "message": "Pengaduan berhasil diperbarui",
        "data": item.to_dict()
    }), 200