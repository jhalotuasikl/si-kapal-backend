from flask import Blueprint, request, jsonify
from app import db

from app.models.murid import Murid
from app.models.user import User
from app.models.role import Role
from app.models.kelas import Kelas
from app.models.mata_pelajaran import MataPelajaran
from app.models.murid_tingkat import MuridTingkat
from app.models.kelas_mapel import kelas_mapel
from app.models.tingkat import Tingkat
from app.models.jadwal import Jadwal
from app.models.jadwal_murid import jadwal_murid
from werkzeug.security import generate_password_hash
from app.utils.jadwal_helper import sinkron_jadwal_murid

import csv, io, random, string


admin_murid_bp = Blueprint("admin_murid", __name__)


# ======================
# GENERATOR AKUN
# ======================
def generate_username(nama):
    base = nama.lower().replace(" ", "")
    return f"{base}{random.randint(100,999)}"


def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# =====================================================
# TAMBAH MURID
# =====================================================
from app.utils.jadwal_helper import sinkron_jadwal_murid

@admin_murid_bp.route("/murid", methods=["POST"])
def tambah_murid_manual():
    data = request.json
    print("DATA MASUK:", data)

    if (
        not data.get("nis") or
        not data.get("nama_murid") or
        not data.get("id_kelas") or
        not data.get("id_tingkat") or
        not data.get("id_mapel")
    ):
        return jsonify({"message": "Data tidak lengkap"}), 400

    tingkat = Tingkat.query.get(data["id_tingkat"])
    if not tingkat:
        return jsonify({"message": "Tingkat tidak ditemukan"}), 404

    kelas = Kelas.query.filter_by(id_kelas=data["id_kelas"]).first()
    if not kelas:
        return jsonify({"message": "Kelas tidak ditemukan"}), 404

    if Murid.query.filter_by(nis=data["nis"]).first():
        return jsonify({"message": "NIS sudah terdaftar"}), 400

    role = Role.query.filter_by(nama_role="murid").first()
    if not role:
        return jsonify({"message": "Role murid tidak ada"}), 500

    username = str(data["nis"]).strip()

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username/NIS sudah digunakan"}), 400

    password_asli = generate_password()
    password_hash = generate_password_hash(password_asli)

    try:
        user = User(
            username=username,
            password=password_hash,
            id_role=role.id_role
        )
        db.session.add(user)
        db.session.flush()

        murid = Murid(
            nis=data["nis"],
            nama_murid=data["nama_murid"],
            id_kelas=kelas.id_kelas,
            id_user=user.id_user
        )
        db.session.add(murid)
        db.session.flush()

        mt = MuridTingkat(
            id_murid=murid.id_murid,
            id_tingkat=data["id_tingkat"],
            id_kelas=kelas.id_kelas,
            tahun_ajaran=data.get("tahun_ajaran", "2025/2026"),
            status="aktif"
        )
        db.session.add(mt)

        daftar_id_mapel = data["id_mapel"]

        for idm in daftar_id_mapel:
            mapel = MataPelajaran.query.get(idm)
            if not mapel:
                db.session.rollback()
                return jsonify({
                    "message": f"Mapel ID {idm} tidak ditemukan"
                }), 404

            murid.mapel.append(mapel)

        # helper sinkron jadwal_murid
        sinkron_jadwal_murid(
            id_murid=murid.id_murid,
            id_kelas=kelas.id_kelas,
            daftar_id_mapel=daftar_id_mapel
        )

        db.session.commit()

        return jsonify({
            "message": "Murid berhasil ditambahkan",
            "username": username,
            "password": password_asli
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Gagal menambahkan murid",
            "error": str(e)
        }), 500


# =====================================================
# IMPORT CSV
# =====================================================
@admin_murid_bp.route("/murid/import", methods=["POST"])
def import_murid_csv():

    if "file" not in request.files:
        return jsonify({"message": "File CSV tidak ditemukan"}), 400

    file = request.files["file"]

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"message": "File harus CSV"}), 400

    raw = file.stream.read().decode("utf-8-sig")
    stream = io.StringIO(raw)

    lines = raw.splitlines()
    first_line = lines[0] if lines else ""

    if ";" in first_line:
        delimiter = ";"
    elif "\t" in first_line:
        delimiter = "\t"
    else:
        delimiter = ","

    reader = csv.DictReader(stream, delimiter=delimiter)

    print("CSV DELIMITER:", delimiter)
    print("CSV HEADER:", reader.fieldnames)

    role = Role.query.filter_by(nama_role="murid").first()
    if not role:
        return jsonify({"message": "Role murid tidak ada"}), 500

    berhasil = 0
    gagal = []
    akun = []

    for i, row in enumerate(reader, start=2):
        try:
            if not row.get("nis") or not row.get("nama_murid") or not row.get("id_kelas"):
                gagal.append({
                    "baris": i,
                    "row": row,
                    "error": "Kolom wajib kosong"
                })
                continue

            nis = str(row["nis"]).strip()
            nama = str(row["nama_murid"]).strip()

            if Murid.query.filter_by(nis=nis).first():
                gagal.append({
                    "baris": i,
                    "row": row,
                    "error": "NIS sudah ada"
                })
                continue

            try:
                id_kelas = int(str(row["id_kelas"]).strip())
            except:
                gagal.append({
                    "baris": i,
                    "row": row,
                    "error": "ID kelas bukan angka"
                })
                continue

            kelas = Kelas.query.get(id_kelas)
            if not kelas:
                gagal.append({
                    "baris": i,
                    "row": row,
                    "error": "Kelas tidak ditemukan"
                })
                continue

            username = nis

            if User.query.filter_by(username=username).first():
                gagal.append({
                    "baris": i,
                    "row": row,
                    "error": "Username/NIS sudah digunakan"
                })
                continue
            password_asli = generate_password()
            password_hash = generate_password_hash(password_asli)

            user = User(
                username=username,
                password=password_hash,   # ✅ hash
                id_role=role.id_role
            )
            db.session.add(user)
            db.session.flush()

            murid = Murid(
                nis=nis,
                nama_murid=nama,
                id_kelas=kelas.id_kelas,
                id_user=user.id_user
            )
            db.session.add(murid)
            db.session.flush()

            mt = MuridTingkat(
                id_murid=murid.id_murid,
                id_tingkat=kelas.id_tingkat,
                id_kelas=kelas.id_kelas,
                tahun_ajaran=getattr(kelas, "tahun_ajaran", "2025/2026"),
                status="aktif"
            )
            db.session.add(mt)

            for mapel in kelas.mapel:
                murid.mapel.append(mapel)

            berhasil += 1
            akun.append({
                "baris": i,
                "nis": nis,
                "nama_murid": nama,
                "id_kelas": kelas.id_kelas,
                "username": username,
                "password": password_asli
            })

        except Exception as e:
            db.session.rollback()
            gagal.append({
                "baris": i,
                "row": row,
                "error": str(e)
            })

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Gagal commit import",
            "error": str(e)
        }), 500

    return jsonify({
        "message": "Import selesai",
        "berhasil": berhasil,
        "gagal": len(gagal),
        "akun": akun,
        "detail_gagal": gagal
    }), 201


# =====================================================
# UPDATE
# =====================================================
@admin_murid_bp.route("/murid/<int:id_murid>", methods=["PUT"])
def update_murid(id_murid):

    data = request.json

    if not data:
        return jsonify({"message": "Data kosong"}), 400

    murid = Murid.query.get_or_404(id_murid)

    if "nis" in data:
        if Murid.query.filter(
            Murid.nis == data["nis"],
            Murid.id_murid != id_murid
        ).first():
            return jsonify({"message": "NIS sudah digunakan"}), 400

        murid.nis = data["nis"]

    murid.nama_murid = data.get("nama_murid", murid.nama_murid)

    if "id_kelas" in data:
        kelas = Kelas.query.get(data["id_kelas"])
        if not kelas:
            return jsonify({"message": "Kelas tidak ditemukan"}), 404

        murid.id_kelas = kelas.id_kelas

        # update tingkat aktif di murid_tingkat
        mt = MuridTingkat.query.filter_by(
            id_murid=murid.id_murid,
            status="aktif"
        ).first()

        if mt:
            mt.id_kelas = kelas.id_kelas
            mt.id_tingkat = kelas.id_tingkat
        else:
            mt = MuridTingkat(
                id_murid=murid.id_murid,
                id_tingkat=kelas.id_tingkat,
                id_kelas=kelas.id_kelas,
                tahun_ajaran=getattr(kelas, "tahun_ajaran", "2025/2026"),
                status="aktif"
            )
            db.session.add(mt)

        # reset mapel ikut kelas baru
        murid.mapel.clear()
        for mapel in kelas.mapel:
            murid.mapel.append(mapel)

    if "id_mapel" in data:
        murid.mapel.clear()

        for idm in data["id_mapel"]:
            mapel = MataPelajaran.query.get(idm)

            if not mapel:
                return jsonify({
                    "message": f"Mapel ID {idm} tidak ditemukan"
                }), 404

            murid.mapel.append(mapel)

    db.session.commit()

    return jsonify({"message": "Murid diperbarui"}), 200


# =====================================================
# DELETE
# =====================================================
@admin_murid_bp.route("/murid/<int:id_murid>", methods=["DELETE"])
def hapus_murid(id_murid):

    murid = Murid.query.get_or_404(id_murid)


    murid.mapel.clear()


    user = User.query.get(murid.id_user)

    if user:
        db.session.delete(user)


    db.session.delete(murid)
    db.session.commit()


    return jsonify({"message": "Murid dihapus"}), 200


# =====================================================
# LIST BY TINGKAT (ambil dari murid_tingkat status aktif)
# =====================================================
@admin_murid_bp.route("/murid/tingkat/<int:id_tingkat>", methods=["GET"])
def list_murid_by_tingkat(id_tingkat):

    # ambil murid yang tingkat aktifnya = id_tingkat
    murids = (
        Murid.query
        .join(MuridTingkat, MuridTingkat.id_murid == Murid.id_murid)
        .filter(
            MuridTingkat.id_tingkat == id_tingkat,
            MuridTingkat.status == "aktif"
        )
        .all()
    )

    # ambil pangkat tingkat (biar gak query berulang2)
    tingkat = Tingkat.query.get(id_tingkat)
    pangkat = tingkat.pangkat if tingkat else None

    result = []

    for m in murids:
        for mapel in m.mapel:
            result.append({
                "id_murid": m.id_murid,
                "nis": m.nis,
                "nama_murid": m.nama_murid,

                "id_kelas": m.id_kelas,
                "kelas": m.kelas.nama_kelas,

                "id_tingkat": id_tingkat,   # ✅ sesuai parameter
                "pangkat": pangkat,         # ✅ langsung kirim pangkat

                "id_mapel": mapel.id_mapel,
                "nama_mapel": mapel.nama_mapel,
            })

    return jsonify(result), 200

# =====================================================
# LIST ALL
# =====================================================
from app.models.murid_tingkat import MuridTingkat
from app.models.tingkat import Tingkat


@admin_murid_bp.route("/murid", methods=["GET"])
def list_murid():

    try:

        murids = Murid.query.all()
        result = []

        for m in murids:

            # =========================
            # AMBIL TINGKAT AKTIF
            # =========================
            mt = MuridTingkat.query.filter_by(
                id_murid=m.id_murid,
                status="aktif"
            ).first()

            tingkat_id = None
            pangkat = None

            if mt:
                tingkat_id = mt.id_tingkat
                tingkat = Tingkat.query.get(mt.id_tingkat)
                if tingkat:
                    pangkat = tingkat.pangkat

            # =========================
            # LOOP MAPEL
            # =========================
            for mapel in m.mapel:

                result.append({
                    "id_murid": m.id_murid,
                    "nis": m.nis,
                    "nama_murid": m.nama_murid,

                    "id_kelas": m.id_kelas,
                    "kelas": m.kelas.nama_kelas,

                    "id_tingkat": tingkat_id,     # ✅ dari murid_tingkat
                    "pangkat": pangkat,           # ✅ langsung kirim pangkat

                    "id_mapel": mapel.id_mapel,
                    "nama_mapel": mapel.nama_mapel
                })

        return jsonify(result), 200

    except Exception as e:
        print("❌ ERROR list_murid:", e)
        return jsonify({"error": str(e)}), 500