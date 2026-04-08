from flask import Blueprint, request, jsonify
from app import db
from app.models.kelas import Kelas
from app.models.tingkat import Tingkat
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.jadwal import Jadwal

admin_kelas_bp = Blueprint("admin_kelas", __name__)



# === ROUTE: GET LIST KELAS ===
@admin_kelas_bp.route("/kelas", methods=["GET"])
def list_kelas():

    kelas_list = Kelas.query.all()

    result = []

    for k in kelas_list:

        jadwal_list = Jadwal.query.filter_by(
            id_kelas=k.id_kelas
        ).all()

        jadwal_data = []

        for j in jadwal_list:
            jadwal_data.append({
                "hari": j.hari,
                "mulai": j.jam_mulai.strftime('%H:%M'),
                "selesai": j.jam_selesai.strftime('%H:%M'),
                
            })

        result.append({
            "id_kelas": k.id_kelas,
            "nama_kelas": k.nama_kelas,
            "tahun_ajaran": k.tahun_ajaran,

            "tingkat": {
                "id_tingkat": k.tingkat.id_tingkat,
                "pangkat": k.tingkat.pangkat
            },

            # ✅ ARRAY
            "jadwal": jadwal_data
        })

    return jsonify(result), 200

# === ROUTE: TAMBAH KELAS ===
@admin_kelas_bp.route("/kelas", methods=["POST"])
def tambah_kelas():
    data = request.json
    nama_kelas = data.get("nama_kelas")
    tahun_ajaran = data.get("tahun_ajaran")
    id_tingkat = data.get("id_tingkat")

    

    if not nama_kelas or not tahun_ajaran or not id_tingkat:
        return jsonify({"message": "Data tidak lengkap"}), 400

    # cek tingkat
    tingkat = Tingkat.query.get(id_tingkat)
    if not tingkat:
        return jsonify({"message": "Tingkat tidak ditemukan"}), 404

    # tambah kelas
    kelas = Kelas(
        nama_kelas=nama_kelas,
        tahun_ajaran=tahun_ajaran,
        id_tingkat=id_tingkat
    )
    db.session.add(kelas)
    db.session.commit()

    return jsonify({"message": "Kelas berhasil ditambahkan"}), 201

@admin_kelas_bp.route("/kelas/<int:id_kelas>/guru", methods=["POST"])
def tambah_guru_kelas(id_kelas):

    data = request.json

    if not data or "id_guru" not in data:
        return jsonify({"message": "id_guru wajib"}), 400

    from app.models.guru import Guru

    kelas = Kelas.query.get_or_404(id_kelas)
    guru = Guru.query.get_or_404(data["id_guru"])

    if guru in kelas.guru:
        return jsonify({"message": "Guru sudah ada"}), 400

    kelas.guru.append(guru)
    db.session.commit()

    return jsonify({"message": "Guru ditambahkan"}), 201

@admin_kelas_bp.route("/kelas/<int:id_kelas>/guru", methods=["GET"])
def list_guru_kelas(id_kelas):
    kelas = Kelas.query.get_or_404(id_kelas)

    return jsonify([{
        "id_guru": g.id_guru,
        "nama_guru": g.nama_guru
    } for g in kelas.guru.all()])

@admin_kelas_bp.route("/kelas/<int:id_kelas>/murid", methods=["POST"])
def tambah_murid_kelas(id_kelas):

    data = request.json

    if not data or "id_murid" not in data:
        return jsonify({"message": "id_murid wajib"}), 400

    from app.models.murid import Murid

    kelas = Kelas.query.get_or_404(id_kelas)
    murid = Murid.query.get_or_404(data["id_murid"])

    if murid.id_kelas == id_kelas:
        return jsonify({"message": "Murid sudah di kelas ini"}), 400

    if murid.id_tingkat != kelas.id_tingkat:
        return jsonify({"message": "Tingkat tidak sesuai"}), 400

    murid.id_kelas = id_kelas
    db.session.commit()

    return jsonify({"message": "Murid ditambahkan"}), 201

@admin_kelas_bp.route("/kelas/<int:id_kelas>/murid", methods=["GET"])
def list_murid_kelas(id_kelas):

    from app.models.murid import Murid

    murid = Murid.query.filter_by(id_kelas=id_kelas).all()

    return jsonify([
        {
            "id_murid": m.id_murid,
            "nama_murid": m.nama_murid
        } for m in murid
    ]), 200

# =========================
# GET KELAS BY TINGKAT
# =========================
@admin_kelas_bp.route("/tingkat/<int:id_tingkat>/kelas", methods=["GET"])
@jwt_required()
def get_kelas_by_tingkat(id_tingkat):

    from app.models.kelas import Kelas

    kelas_list = Kelas.query.filter_by(id_tingkat=id_tingkat).all()

    result = []

    for k in kelas_list:
        result.append({
            "id_kelas": k.id_kelas,
            "nama_kelas": k.nama_kelas,
            "tahun_ajaran": k.tahun_ajaran,
            "id_tingkat": k.id_tingkat,
        })

    return jsonify(result), 200

# =========================
# GET KELAS BY GURU
# =========================
@admin_kelas_bp.route("/guru/<int:id_guru>/kelas", methods=["GET"])
@jwt_required()
def get_kelas_by_guru(id_guru):

    from app.models.guru import Guru

    guru = Guru.query.get_or_404(id_guru)

    result = []

    for k in guru.kelas:
        result.append({
            "id_kelas": k.id_kelas,
            "nama_kelas": k.nama_kelas,
            "tahun_ajaran": k.tahun_ajaran,
            "id_tingkat": k.id_tingkat,
        })

    return jsonify(result), 200
@admin_kelas_bp.route("/kelas/<int:id_kelas>", methods=["GET"])
def get_kelas(id_kelas):

    k = Kelas.query.get_or_404(id_kelas)

    return jsonify({
        "id_kelas": k.id_kelas,
        "nama_kelas": k.nama_kelas,
        "tahun_ajaran": k.tahun_ajaran,
        "id_tingkat": k.id_tingkat
    }), 200

@admin_kelas_bp.route("/kelas/<int:id_kelas>", methods=["PUT"])
def update_kelas(id_kelas):

    data = request.json

    if not data:
        return jsonify({"message": "Data kosong"}), 400

    kelas = Kelas.query.get_or_404(id_kelas)

    if "id_tingkat" in data:
        tingkat = Tingkat.query.get(data["id_tingkat"])
        if not tingkat:
            return jsonify({"message": "Tingkat tidak valid"}), 400

    kelas.nama_kelas = data.get("nama_kelas", kelas.nama_kelas)
    kelas.tahun_ajaran = data.get("tahun_ajaran", kelas.tahun_ajaran)
    kelas.id_tingkat = data.get("id_tingkat", kelas.id_tingkat)

    db.session.commit()

    return jsonify({"message": "Kelas berhasil diperbarui"}), 200

@admin_kelas_bp.route("/kelas/<int:id_kelas>", methods=["DELETE"])
def hapus_kelas(id_kelas):

    kelas = Kelas.query.get_or_404(id_kelas)

    db.session.delete(kelas)
    db.session.commit()

    return jsonify({"message": "Kelas berhasil dihapus"}), 200

@admin_kelas_bp.route("/guru/kelas", methods=["GET"])
@jwt_required()
def get_kelas_guru_login():
    claims = get_jwt()
    id_guru = claims.get("id_guru")
    if not id_guru:
        return jsonify({"message": "id_guru tidak ada di token"}), 400

    from app.models.guru import Guru
    guru = Guru.query.get_or_404(id_guru)

    result = []
    for k in guru.kelas:
        result.append({
            "id_kelas": k.id_kelas,
            "nama_kelas": k.nama_kelas,
            "tahun_ajaran": k.tahun_ajaran,
            "id_tingkat": k.id_tingkat,
        })

    return jsonify(result), 200


@admin_kelas_bp.route("/kelas/<int:id_kelas>/murid/<int:id_murid>", methods=["DELETE"])
def hapus_murid_dari_kelas(id_kelas, id_murid):
    from app.models.murid import Murid
    murid = Murid.query.get_or_404(id_murid)
    if murid.id_kelas != id_kelas:
        return jsonify({"message": "Murid tidak di kelas ini"}), 400
    murid.id_kelas = None
    db.session.commit()
    return jsonify({"message": "Murid dihapus dari kelas"}), 200

@admin_kelas_bp.route("/kelas/<int:id_kelas>/guru/<int:id_guru>", methods=["DELETE"])
def hapus_guru_dari_kelas(id_kelas, id_guru):
    from app.models.guru import Guru
    kelas = Kelas.query.get_or_404(id_kelas)
    guru = Guru.query.get_or_404(id_guru)
    if guru not in kelas.guru:
        return jsonify({"message": "Guru tidak ada di kelas ini"}), 400
    kelas.guru.remove(guru)
    db.session.commit()
    return jsonify({"message": "Guru dihapus dari kelas"}), 200

from flask import Blueprint, jsonify
from app.models.kelas import Kelas
from app.extensions import db

kelas_bp = Blueprint("kelas", __name__)

@kelas_bp.route("/kelas", methods=["GET"])
def list_kelas():
    data = db.session.query(Kelas).all()
    result = [{"id_kelas": k.id_kelas, "nama_kelas": k.nama_kelas} for k in data]
    return jsonify(result), 200