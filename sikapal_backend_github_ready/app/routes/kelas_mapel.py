from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime

from app.extensions import db
from app.models.kelas import Kelas
from app.models.mata_pelajaran import MataPelajaran
from app.models.jadwal import Jadwal
from app.models.kelas_mapel import kelas_mapel  # ini Table association kamu

kelas_mapel_bp = Blueprint("kelas_mapel", __name__)

@kelas_mapel_bp.route("/kelas/mapel/jadwal", methods=["POST"])
@jwt_required()
def add_mapel_with_jadwal():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"msg": "Hanya admin"}), 403

    data = request.json or {}

    id_kelas    = data.get("id_kelas")
    nama_mapel  = (data.get("nama_mapel") or "").strip()
    hari        = (data.get("hari") or "").strip()
    jam_mulai   = (data.get("jam_mulai") or "").strip()
    jam_selesai = (data.get("jam_selesai") or "").strip()

    if not all([id_kelas, nama_mapel, hari, jam_mulai, jam_selesai]):
        return jsonify({"msg": "Data tidak lengkap"}), 400

    # parse jam
    try:
        jm = datetime.strptime(jam_mulai, "%H:%M").time()
        js = datetime.strptime(jam_selesai, "%H:%M").time()
    except:
        return jsonify({"msg": "Format jam harus HH:MM"}), 400

    if jm >= js:
        return jsonify({"msg": "Jam mulai harus < jam selesai"}), 400

    # ambil kelas + tingkat
    kelas = Kelas.query.get_or_404(id_kelas)
    id_tingkat = kelas.id_tingkat

    # =========================
    # 1) CEK / INSERT MAPEL
    # =========================
    mapel = MataPelajaran.query.filter_by(
        nama_mapel=nama_mapel,
        id_tingkat=id_tingkat
    ).first()

    if not mapel:
        mapel = MataPelajaran(
            nama_mapel=nama_mapel,
            id_tingkat=id_tingkat
        )
        db.session.add(mapel)
        db.session.flush()  # <-- supaya mapel.id_mapel langsung ada tanpa commit dulu

    id_mapel = mapel.id_mapel

    # =========================
    # 2) CEK RELASI kelas_mapel
    # =========================
    # cek apakah sudah ada relasi
    exists = db.session.execute(
        db.select(kelas_mapel.c.id_kelas)
        .where(
            kelas_mapel.c.id_kelas == id_kelas,
            kelas_mapel.c.id_mapel == id_mapel
        )
        .limit(1)
    ).first()

    if not exists:
        db.session.execute(
            kelas_mapel.insert().values(id_kelas=id_kelas, id_mapel=id_mapel)
        )

    # =========================
    # 3) INSERT JADWAL
    # =========================
    # OPTIONAL: cegah jadwal dobel exact sama
    dupe = Jadwal.query.filter_by(
        id_kelas=id_kelas,
        id_mapel=id_mapel,
        hari=hari
    ).filter(
        Jadwal.jam_mulai == jm,
        Jadwal.jam_selesai == js
    ).first()

    if dupe:
        db.session.rollback()
        return jsonify({"msg": "Jadwal sudah ada (duplikat)"}), 409

    jadwal = Jadwal(
        id_kelas=id_kelas,
        id_mapel=id_mapel,
        hari=hari,
        jam_mulai=jm,
        jam_selesai=js,
    )
    db.session.add(jadwal)
    db.session.commit()

    return jsonify({
        "msg": "Mapel & Jadwal berhasil ditambahkan",
        "id_mapel": id_mapel,
        "id_jadwal": jadwal.id_jadwal
    }), 201