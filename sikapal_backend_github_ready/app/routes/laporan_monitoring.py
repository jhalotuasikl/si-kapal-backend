# app/routes/monitoring.py
from flask import Blueprint, request, jsonify
from datetime import datetime, date
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models.monitoring import LaporanMonitoring
from app.models.mengajar import LaporanMengajar
from app.models.jadwal import Jadwal
from app.models.jadwal_guru import JadwalGuru
from app.models.kelas import Kelas
from app.models.mata_pelajaran import MataPelajaran
from app.models.guru import Guru

monitoring_bp = Blueprint("monitoring", __name__)

def jadwal_milik_guru(id_jadwal: int, id_guru: int) -> bool:
    return db.session.query(JadwalGuru).filter_by(
        id_jadwal=id_jadwal,
        id_guru=id_guru
    ).first() is not None

def hari_indonesia_lower():
    # jadwal kamu banyak yang pakai lowercase (senin/selasa/...)
    map_hari = {
        "Monday": "senin",
        "Tuesday": "selasa",
        "Wednesday": "rabu",
        "Thursday": "kamis",
        "Friday": "jumat",
        "Saturday": "sabtu",
        "Sunday": "minggu",
    }
    return map_hari[datetime.now().strftime("%A")]


# =====================================================
# ✅ JADWAL HARI INI (GURU LOGIN) - via jadwal_guru
# =====================================================
@monitoring_bp.route("/guru/jadwal-hari-ini", methods=["GET"])
@jwt_required()
def jadwal_hari_ini():
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "id_guru tidak ada di token"}), 400

    hari = hari_indonesia_lower()

    data = (
        db.session.query(Jadwal, Kelas, MataPelajaran)
        .join(JadwalGuru, Jadwal.id_jadwal == JadwalGuru.id_jadwal)
        .join(Kelas, Jadwal.id_kelas == Kelas.id_kelas)
        .join(MataPelajaran, Jadwal.id_mapel == MataPelajaran.id_mapel)
        .filter(JadwalGuru.id_guru == id_guru, Jadwal.hari == hari)
        .order_by(Jadwal.jam_mulai.asc())
        .all()
    )

    return jsonify([
        {
            "id_jadwal": j.id_jadwal,
            "kelas": k.nama_kelas,
            "mapel": m.nama_mapel,
            "mulai": j.jam_mulai.strftime("%H:%M"),
            "selesai": j.jam_selesai.strftime("%H:%M"),
            "hari": j.hari,
        } for j, k, m in data
    ]), 200


# =====================================================
# ✅ ABSEN MASUK - validasi jadwal milik guru
# =====================================================
@monitoring_bp.route("/guru/absen-masuk", methods=["POST"])
@jwt_required()
def absen_masuk():
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    data = request.json or {}
    id_jadwal = data.get("id_jadwal")
    if not id_jadwal:
        return jsonify({"message": "id_jadwal wajib"}), 400

    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "id_guru tidak ada di token"}), 400

    if not jadwal_milik_guru(int(id_jadwal), int(id_guru)):
        return jsonify({"message": "Jadwal tidak valid"}), 403

    today = date.today()

    cek = LaporanMonitoring.query.filter_by(
        id_jadwal=id_jadwal,
        tanggal=today
    ).first()

    if cek:
        return jsonify({
            "message": "Sudah absen",
            "id_monitor": cek.id_monitor
        }), 409

    monitor = LaporanMonitoring(
        id_jadwal=id_jadwal,
        tanggal=today,
        jam_masuk=datetime.now().time(),
        status="Hadir"
    )

    db.session.add(monitor)
    db.session.commit()

    return jsonify({
        "message": "Absen masuk berhasil",
        "id_monitor": monitor.id_monitor
    }), 201


# =====================================================
# ✅ ABSEN KELUAR - validasi pemilik via jadwal_guru
# =====================================================
@monitoring_bp.route("/guru/absen-keluar", methods=["POST"])
@jwt_required()
def absen_keluar():
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    data = request.json or {}
    id_monitor = data.get("id_monitor")
    if not id_monitor:
        return jsonify({"message": "id_monitor wajib"}), 400

    id_guru = claims.get("id_guru")
    monitor = LaporanMonitoring.query.get_or_404(id_monitor)

    if not jadwal_milik_guru(monitor.id_jadwal, id_guru):
        return jsonify({"message": "Bukan data anda"}), 403

    if monitor.jam_keluar:
        return jsonify({"message": "Sudah absen keluar"}), 409

    monitor.jam_keluar = datetime.now().time()
    monitor.status = "Selesai"
    db.session.commit()

    return jsonify({"message": "Absen keluar berhasil"}), 200


# =====================================================
# ✅ LAPORAN MENGAJAR
# =====================================================
@monitoring_bp.route("/guru/laporan-mengajar", methods=["POST"])
@jwt_required()
def laporan_mengajar():
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    data = request.json or {}
    required = ["id_monitor", "materi", "catatan", "jumlah_hadir"]
    for r in required:
        if r not in data:
            return jsonify({"message": f"{r} wajib"}), 400

    id_guru = claims.get("id_guru")
    monitor = LaporanMonitoring.query.get_or_404(data["id_monitor"])

    if not jadwal_milik_guru(monitor.id_jadwal, id_guru):
        return jsonify({"message": "Bukan laporan anda"}), 403

    laporan = LaporanMengajar(
        id_monitor=monitor.id_monitor,
        materi=data["materi"],
        catatan=data["catatan"],
        jumlah_hadir=data["jumlah_hadir"]
    )

    db.session.add(laporan)
    db.session.commit()

    return jsonify({"message": "Laporan tersimpan"}), 201


# =====================================================
# ✅ STATUS ABSEN (UNTUK UI)
# =====================================================
@monitoring_bp.route("/guru/status-absen/<int:id_jadwal>", methods=["GET"])
@jwt_required()
def status_absen(id_jadwal):
    claims = get_jwt()
    if claims.get("role") != "guru":
        return jsonify({"message": "Akses ditolak"}), 403

    id_guru = claims.get("id_guru")
    if not jadwal_milik_guru(id_jadwal, id_guru):
        return jsonify({"message": "Jadwal tidak valid"}), 403

    today = date.today()

    data = LaporanMonitoring.query.filter_by(
        id_jadwal=id_jadwal,
        tanggal=today
    ).first()

    if not data:
        return jsonify({"status": "belum"}), 200

    if data.jam_masuk and not data.jam_keluar:
        return jsonify({"status": "masuk", "id_monitor": data.id_monitor}), 200

    return jsonify({"status": "selesai", "id_monitor": data.id_monitor}), 200


# =====================================================
# ✅ ADMIN MONITORING - join Guru via JadwalGuru
# =====================================================
@monitoring_bp.route("/admin/monitoring", methods=["GET"])
@jwt_required()
def monitoring_admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Akses ditolak"}), 403

    today = date.today()
    hari = hari_indonesia_lower()
    now_time = datetime.now().time()

    # Ambil semua jadwal guru hari ini,
    # lalu LEFT JOIN ke laporan_monitoring berdasarkan id_jadwal + tanggal hari ini
    data = (
        db.session.query(
            Jadwal,
            Kelas,
            MataPelajaran,
            Guru,
            LaporanMonitoring
        )
        .join(JadwalGuru, JadwalGuru.id_jadwal == Jadwal.id_jadwal)
        .join(Guru, Guru.id_guru == JadwalGuru.id_guru)
        .join(Kelas, Kelas.id_kelas == Jadwal.id_kelas)
        .join(MataPelajaran, MataPelajaran.id_mapel == Jadwal.id_mapel)
        .outerjoin(
            LaporanMonitoring,
            db.and_(
                LaporanMonitoring.id_jadwal == Jadwal.id_jadwal,
                LaporanMonitoring.tanggal == today
            )
        )
        .filter(Jadwal.hari == hari)
        .order_by(Jadwal.jam_mulai.asc(), Guru.nama_guru.asc())
        .all()
    )

    hasil = []

    for jadwal, kelas, mapel, guru, mon in data:
        status = "Belum Absen"
        jam_masuk = None
        jam_keluar = None
        id_monitor = None

        if mon:
            id_monitor = mon.id_monitor
            jam_masuk = str(mon.jam_masuk) if mon.jam_masuk else None
            jam_keluar = str(mon.jam_keluar) if mon.jam_keluar else None

            if mon.jam_keluar:
                status = "Selesai"
            elif mon.jam_masuk:
                status = "Hadir"
            else:
                status = mon.status or "Belum Absen"
        else:
            # jika belum ada record monitoring
            if jadwal.jam_selesai and now_time > jadwal.jam_selesai:
                status = "Tidak Hadir"
            else:
                status = "Belum Absen"

        hasil.append({
            "id": id_monitor,
            "id_monitor": id_monitor,
            "id_jadwal": jadwal.id_jadwal,
            "tanggal": str(today),
            "hari": jadwal.hari,
            "guru": guru.nama_guru if guru else None,
            "kelas": kelas.nama_kelas,
            "mapel": mapel.nama_mapel,
            "jam_jadwal_mulai": str(jadwal.jam_mulai)[:5] if jadwal.jam_mulai else None,
            "jam_jadwal_selesai": str(jadwal.jam_selesai)[:5] if jadwal.jam_selesai else None,
            "masuk": jam_masuk,
            "keluar": jam_keluar,
            "status": status,
        })

    return jsonify(hasil), 200
