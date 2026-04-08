from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from app import db
from app.models.kelas import Kelas
from app.models.jadwal import Jadwal
from app.models.jadwal_guru import JadwalGuru
from app.models.murid import Murid
from app.models.kehadiran_murid import KehadiranMurid

guru_bp = Blueprint("guru", __name__)

@guru_bp.route("/guru/kelas", methods=["GET"])
@jwt_required()
def get_kelas_guru_login():
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Khusus guru"}), 403

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "id_guru tidak ada di token"}), 400

    kelas_list = (
        db.session.query(Kelas)
        .join(Jadwal, Jadwal.id_kelas == Kelas.id_kelas)
        .join(JadwalGuru, JadwalGuru.id_jadwal == Jadwal.id_jadwal)
        .filter(JadwalGuru.id_guru == id_guru)
        .distinct()
        .all()
    )

    return jsonify([
        {
            "id_kelas": k.id_kelas,
            "nama_kelas": k.nama_kelas,
            "tahun_ajaran": k.tahun_ajaran,
            "id_tingkat": k.id_tingkat,
        }
        for k in kelas_list
    ]), 200

@guru_bp.route("/guru/rekap-absensi/<int:id_jadwal>", methods=["GET"])
@jwt_required()
def guru_rekap_absensi_by_jadwal(id_jadwal):
    claims = get_jwt()

    if claims.get("role") != "guru":
        return jsonify({"message": "Khusus guru"}), 403

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "id_guru tidak ada di token"}), 400

    # cek jadwal benar milik guru login
    jadwal_guru = JadwalGuru.query.filter_by(
        id_jadwal=id_jadwal,
        id_guru=id_guru
    ).first()

    if not jadwal_guru:
        return jsonify({"message": "Jadwal tidak ditemukan / bukan milik guru"}), 404

    jadwal = Jadwal.query.get(id_jadwal)
    if not jadwal:
        return jsonify({"message": "Jadwal tidak ditemukan"}), 404

    # ambil murid dalam jadwal
    # kalau pakai relasi jadwal_murid, ambil dari situ
    # kalau tidak, fallback dari kelas
    murid_list = Murid.query.filter_by(id_kelas=jadwal.id_kelas).all()

    # ambil kehadiran berdasarkan id_jadwal
    rows = KehadiranMurid.query.filter_by(id_jadwal=id_jadwal).all()

    idx = {}
    for r in rows:
        idx[(r.id_murid, r.pertemuan)] = r.status

    result = []
    for m in murid_list:
        item = {
            "id_murid": m.id_murid,
            "nis": getattr(m, "nis", None),
            "nama_murid": m.nama_murid,
        }
        for p in range(1, 15):
            item[f"P{p}"] = idx.get((m.id_murid, p), "")
        result.append(item)

    return jsonify(result), 200
@guru_bp.route("/admin/rekap-absensi/<int:id_jadwal>", methods=["GET"])
def admin_rekap_absensi_by_jadwal(id_jadwal):
    jadwal = Jadwal.query.get(id_jadwal)
    if not jadwal:
        return jsonify({"message": "Jadwal tidak ditemukan"}), 404

    murid_list = Murid.query.filter_by(id_kelas=jadwal.id_kelas).all()
    rows = KehadiranMurid.query.filter_by(id_jadwal=id_jadwal).all()

    idx = {}
    for r in rows:
        idx[(r.id_murid, r.pertemuan)] = r.status

    result = []
    for m in murid_list:
        item = {
            "id_murid": m.id_murid,
            "nis": getattr(m, "nis", None),
            "nama_murid": m.nama_murid,
        }
        for p in range(1, 15):
            item[f"P{p}"] = idx.get((m.id_murid, p), "")
        result.append(item)

    return jsonify(result), 200
@guru_bp.route("/admin/absensi", methods=["POST"])
def simpan_laporan_absensi_admin():
    data = request.json

    if not data:
        return jsonify({"message": "Data kosong"}), 400

    id_jadwal = data.get("id_jadwal")
    rekap = data.get("rekap", [])

    if not id_jadwal or not rekap:
        return jsonify({"message": "id_jadwal dan rekap wajib"}), 400

    jadwal = Jadwal.query.get(id_jadwal)
    if not jadwal:
        return jsonify({"message": "Jadwal tidak ditemukan"}), 404

    # kalau hanya ingin validasi dan tidak simpan terpisah, bisa cukup return sukses
    # karena data sebenarnya sudah ada di tabel kehadiran_murid
    return jsonify({
        "message": "Laporan absensi berhasil diterima admin",
        "id_jadwal": id_jadwal
    }), 200