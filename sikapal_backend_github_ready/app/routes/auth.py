from flask import Blueprint, request, jsonify

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

from app import db

from app.models.user import User
from app.models.role import Role
from app.models.murid import Murid
from app.models.guru import Guru
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():

    data = request.json

    if not data:
        return jsonify({"message": "Data tidak lengkap"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username / password kosong"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User tidak ditemukan"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"message": "Password salah"}), 401

    role = Role.query.get(user.id_role)

    if not role:
        return jsonify({"message": "Role tidak valid"}), 500

    id_murid = None
    id_guru = None

    nama_murid = None
    nis = None

    nama_guru = None
    nip = None

    if role.nama_role == "murid":
        murid = Murid.query.filter_by(id_user=user.id_user).first()

        if not murid:
            return jsonify({"message": "Data murid rusak"}), 500

        id_murid = murid.id_murid
        nama_murid = murid.nama_murid
        nis = murid.nis

    elif role.nama_role == "guru":
        guru = Guru.query.filter_by(id_user=user.id_user).first()

        if not guru:
            return jsonify({"message": "Data guru rusak"}), 500

        id_guru = guru.id_guru
        nama_guru = guru.nama_guru
        nip = guru.nip

    access_token = create_access_token(
        identity=str(user.id_user),
        additional_claims={
            "role": role.nama_role.lower(),
            "id_guru": id_guru,
            "id_murid": id_murid
        }
    )

    refresh_token = create_refresh_token(
        identity=str(user.id_user)
    )

    return jsonify({
    "access_token": access_token,
    "refresh_token": refresh_token,

    "username": user.username,
    "role": role.nama_role.lower(),

    "id_guru": id_guru,
    "id_murid": id_murid,

    "nama_murid": nama_murid,
    "nis": nis,

    "nama_guru": nama_guru,
    "nip": nip,

    "foto_profil": user.foto_profil
}), 200


# =====================================================
# REGISTER
# =====================================================
@auth_bp.route('/register', methods=['POST'])
def register():

    data = request.json

    if not data:
        return jsonify({"message": "Data kosong"}), 400


    username = data.get("username")
    password = data.get("password")
    role_name = data.get("role")


    if not username or not password or not role_name:
        return jsonify({"message": "Data wajib belum lengkap"}), 400


    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username sudah digunakan"}), 400


    role = Role.query.filter_by(nama_role=role_name).first()

    if not role:
        return jsonify({"message": "Role tidak valid"}), 400


    # VALIDASI DETAIL
    if role.nama_role == "murid" and not data.get("nis"):
        return jsonify({"message": "NIS wajib"}), 400

    if role.nama_role == "guru" and not data.get("nip"):
        return jsonify({"message": "NIP wajib"}), 400


    # HASH PASSWORD
    hashed = generate_password_hash(password)
    user = User(
        username=username,
        password=hashed,
        id_role=role.id_role
    )
    db.session.add(user)
    db.session.flush()
    if role.nama_role == "murid":
        murid = Murid(
            nis=data["nis"],
            nama_murid=username,
            id_user=user.id_user
        )
        db.session.add(murid)
    elif role.nama_role == "guru":
        guru = Guru(
            nip=data["nip"],
            nama_guru=username,
            id_user=user.id_user
        )
        db.session.add(guru)
    db.session.commit()
    return jsonify({
        "message": "Register berhasil"
    }), 201
# =====================================================
# REFRESH TOKEN
# =====================================================
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    role = Role.query.get(user.id_role)

    id_guru = None
    id_murid = None

    if role.nama_role == "guru":
        guru = Guru.query.filter_by(id_user=user.id_user).first()
        if guru:
            id_guru = guru.id_guru

    if role.nama_role == "murid":
        murid = Murid.query.filter_by(id_user=user.id_user).first()
        if murid:
            id_murid = murid.id_murid


    new_access = create_access_token(
        identity=str(user.id_user),
        additional_claims={
            "role": role.nama_role.lower(),
            "id_guru": id_guru,
            "id_murid": id_murid
        }
    )

    return jsonify({
        "access_token": new_access
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User tidak ditemukan"}), 404

    role = Role.query.get(user.id_role)

    nama = user.username
    identitas = "-"
    role_name = role.nama_role.lower() if role else ""

    if role_name == "murid":
        murid = Murid.query.filter_by(id_user=user.id_user).first()
        if murid:
            nama = murid.nama_murid
            identitas = murid.nis

    elif role_name == "guru":
        guru = Guru.query.filter_by(id_user=user.id_user).first()
        if guru:
            nama = guru.nama_guru
            identitas = guru.nip

    return jsonify({
        "id_user": user.id_user,
        "username": user.username,
        "role": role_name,
        "nama": nama,
        "identitas": identitas,
        "foto_profil": user.foto_profil
    }), 200

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User tidak ditemukan"}), 404

    data = request.json
    if not data:
        return jsonify({"message": "Data kosong"}), 400

    password_lama = data.get("password_lama")
    password_baru = data.get("password_baru")

    if not password_lama or not password_baru:
        return jsonify({"message": "Password lama dan password baru wajib diisi"}), 400

    if not check_password_hash(user.password, password_lama):
        return jsonify({"message": "Password lama salah"}), 400

    if len(password_baru) < 6:
        return jsonify({"message": "Password baru minimal 6 karakter"}), 400

    user.password = generate_password_hash(password_baru)
    db.session.commit()

    return jsonify({"message": "Password berhasil diperbarui"}), 200

@auth_bp.route('/upload-photo', methods=['PUT'])
@jwt_required()
def upload_photo():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User tidak ditemukan"}), 404

    if "photo" not in request.files:
        return jsonify({"message": "File foto tidak ditemukan"}), 400

    file = request.files["photo"]

    if file.filename == "":
        return jsonify({"message": "Nama file kosong"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "Format file harus png/jpg/jpeg/webp"}), 400

    upload_folder = os.path.join(current_app.root_path, "static", "profile_photos")
    os.makedirs(upload_folder, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    filepath = os.path.join(upload_folder, filename)

    try:
        if user.foto_profil:
            old_filename = os.path.basename(user.foto_profil)
            old_path = os.path.join(upload_folder, old_filename)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass

        file.save(filepath)

        if not os.path.exists(filepath):
            return jsonify({"message": "File gagal disimpan"}), 500

        if os.path.getsize(filepath) == 0:
            return jsonify({"message": "File kosong / rusak"}), 500

        user.foto_profil = f"/static/profile_photos/{filename}"
        db.session.commit()

        return jsonify({
            "message": "Foto profil berhasil diperbarui",
            "foto_profil": user.foto_profil
        }), 200

    except Exception as e:
        return jsonify({"message": f"Gagal upload foto: {str(e)}"}), 500