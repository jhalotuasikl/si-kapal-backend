from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from app import db
from app.models.kelas import Kelas
from app.models.jadwal import Jadwal
from app.models.jadwal_guru import JadwalGuru
from app.models.murid import Murid
from app.models.kehadiran_murid import KehadiranMurid

admin_bp = Blueprint("admin", __name__)


# =====================================================
# ADMIN TERIMA ABSENSI DARI GURU (BERDASARKAN ID_JADWAL)
# =====================================================
@admin_bp.route("/admin/absensi", methods=["POST"])
@jwt_required()
def admin_terima_absensi():
    claims = get_jwt()

    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "id_guru tidak ada di token"}), 400

    data = request.get_json() or {}
    id_jadwal = data.get("id_jadwal")
    rekap = data.get("rekap", [])

    if not id_jadwal:
        return jsonify({"message": "id_jadwal wajib"}), 400

    if not isinstance(rekap, list):
        return jsonify({"message": "rekap harus berupa list"}), 400

    jadwal = Jadwal.query.get(id_jadwal)
    if not jadwal:
        return jsonify({"message": "Jadwal tidak ditemukan"}), 404

    # validasi jadwal milik guru login
    cek = JadwalGuru.query.filter_by(
        id_jadwal=id_jadwal,
        id_guru=id_guru
    ).first()

    if not cek:
        return jsonify({"message": "Jadwal bukan milik guru login"}), 403

    # NOTE:
    # karena data absensi sebenarnya sudah tersimpan di tabel KehadiranMurid,
    # route ini cukup menjadi "tanda kirim" ke admin.
    # kalau nanti kamu mau simpan log/tabel laporan admin, bisa ditambahkan di sini.

    return jsonify({
        "message": "Rekap diterima admin",
        "id_jadwal": id_jadwal,
        "jumlah": len(rekap)
    }), 201


# =====================================================
# ADMIN LIHAT REKAP ABSENSI BERDASARKAN ID_JADWAL
# =====================================================
@admin_bp.route("/admin/rekap-absensi/<int:id_jadwal>", methods=["GET"])
@jwt_required()
def get_rekap_absensi_admin_by_jadwal(id_jadwal):
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"message": "Akses ditolak"}), 403

    jadwal = Jadwal.query.get(id_jadwal)
    if not jadwal:
        return jsonify({"message": "Jadwal tidak ditemukan"}), 404

    # ambil murid di kelas jadwal
    murid_list = Murid.query.filter_by(id_kelas=jadwal.id_kelas).all()

    # ambil semua kehadiran berdasarkan id_jadwal
    rows = KehadiranMurid.query.filter_by(id_jadwal=id_jadwal).all()

    # index (id_murid, pertemuan) -> status
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