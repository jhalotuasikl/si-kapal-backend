from flask import Blueprint, request, jsonify
from app.models.murid import Murid
from app.models.kelas import Kelas
from app.models.jadwal import Jadwal
from app.models.mata_pelajaran import MataPelajaran
from app.models.kehadiran_murid import KehadiranMurid

murid_bp = Blueprint("murid", __name__)

@murid_bp.route("/murid/mapel", methods=["GET"])
def get_mapel_murid():
    id_murid = request.args.get("id_murid", type=int)
    if not id_murid:
        return jsonify({"message": "id_murid wajib"}), 400

    murid = Murid.query.get(id_murid)
    if not murid:
        return jsonify({"message": "Murid tidak ditemukan"}), 404

    # asumsi murid punya id_kelas
    id_kelas = getattr(murid, "id_kelas", None)
    if not id_kelas:
        return jsonify([]), 200

    rows = (
        Jadwal.query
        .join(Kelas, Kelas.id_kelas == Jadwal.id_kelas)
        .join(MataPelajaran, MataPelajaran.id_mapel == Jadwal.id_mapel)
        .filter(Jadwal.id_kelas == id_kelas)
        .order_by(Jadwal.hari.asc(), Jadwal.jam_mulai.asc())
        .all()
    )

    result = []
    for j in rows:
        result.append({
            "id_jadwal": j.id_jadwal,
            "id_kelas": j.id_kelas,
            "nama_kelas": j.kelas.nama_kelas if hasattr(j, "kelas") and j.kelas else None,
            "id_mapel": j.id_mapel,
            "nama_mapel": j.mapel.nama_mapel if hasattr(j, "mapel") and j.mapel else None,
            "hari": j.hari,
            "jam_mulai": j.jam_mulai.strftime("%H:%M") if j.jam_mulai else None,
            "jam_selesai": j.jam_selesai.strftime("%H:%M") if j.jam_selesai else None,
        })

    return jsonify(result), 200


@murid_bp.route("/murid/absen", methods=["GET"])
def get_absen_mapel_murid():
    id_murid = request.args.get("id_murid", type=int)
    id_jadwal = request.args.get("id_jadwal", type=int)

    if not id_murid or not id_jadwal:
        return jsonify({"message": "id_murid dan id_jadwal wajib"}), 400

    rows = (KehadiranMurid.query
            .filter_by(id_murid=id_murid, id_jadwal=id_jadwal)
            .order_by(KehadiranMurid.pertemuan.asc())
            .all())

    result = []
    for r in rows:
        result.append({
            "id_kehadiran": getattr(r, "id_kehadiran", None),
            "pertemuan": r.pertemuan,
            "status": r.status,
            # kalau ada tanggal:
            # "tanggal": r.tanggal.strftime("%Y-%m-%d") if r.tanggal else None,
        })

    return jsonify(result), 200