from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.penilaian import PenilaianGuru

penilaian_bp = Blueprint('penilaian', __name__)

# ➕ Penilaian guru oleh murid
@penilaian_bp.route('/penilaian', methods=['POST'])
def tambah_penilaian():
    data = request.json
    nilai = PenilaianGuru(
        id_guru=data.get('id_guru'),
        id_murid=data.get('id_murid'),
        skor=data.get('skor'),
        komentar=data.get('komentar')
    )
    db.session.add(nilai)
    db.session.commit()
    return jsonify({"message": "Penilaian berhasil dikirim"})

# 📄 Lihat penilaian per guru
@penilaian_bp.route('/penilaian/guru/<int:id_guru>', methods=['GET'])
def get_penilaian_guru(id_guru):
    data = PenilaianGuru.query.filter_by(id_guru=id_guru).all()
    return jsonify([
        {
            "skor": p.skor,
            "komentar": p.komentar
        } for p in data
    ])
