from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models.task import db, Task
from models.file import TaskFile
import os
import uuid

files = Blueprint('files', __name__)

# -----------------------------------------------
# CONFIG
# -----------------------------------------------
UPLOAD_FOLDER   = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_FILE_SIZE   = 5 * 1024 * 1024  # 5MB in bytes

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ['png', 'jpg', 'jpeg', 'gif']:
        return 'image'
    elif ext == 'pdf':
        return 'pdf'
    return 'unknown'


# -----------------------------------------------
# UPLOAD — POST /tasks/<id>/upload
# -----------------------------------------------
@files.route('/tasks/<int:task_id>/upload', methods=['POST'])
@jwt_required()
def upload_file(task_id):
    user_id = get_jwt_identity()

    # check task exists
    task = Task.query.get(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    # check file in request
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    # check file selected
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # check file type allowed
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Use: png, jpg, jpeg, gif, pdf"}), 400

    # check file size
    file.seek(0, 2)               # move to end of file
    file_size = file.tell()       # get size in bytes
    file.seek(0)                  # reset to start

    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": "File too large (max 5MB)"}), 400

    # generate unique filename to avoid conflicts
    original_name = file.filename
    extension     = original_name.rsplit('.', 1)[1].lower()
    unique_name   = f"{uuid.uuid4().hex}.{extension}"

    # save file to uploads folder
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(save_path)

    # save record to database
    task_file = TaskFile(
        task_id       = task_id,
        filename      = unique_name,
        original_name = original_name,
        file_type     = get_file_type(original_name),
        file_size     = file_size
    )
    db.session.add(task_file)
    db.session.commit()

    return jsonify({
        "message": "File uploaded successfully",
        "file":    task_file.to_dict()
    }), 201


# -----------------------------------------------
# GET FILES — GET /tasks/<id>/files
# -----------------------------------------------
@files.route('/tasks/<int:task_id>/files', methods=['GET'])
@jwt_required()
def get_files(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    task_files = TaskFile.query.filter_by(task_id=task_id).all()
    return jsonify({
        "task_id": task_id,
        "files":   [f.to_dict() for f in task_files],
        "count":   len(task_files)
    }), 200


# -----------------------------------------------
# DELETE FILE — DELETE /tasks/<id>/files/<file_id>
# -----------------------------------------------
@files.route('/tasks/<int:task_id>/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(task_id, file_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    task_file = TaskFile.query.filter_by(
        id=file_id,
        task_id=task_id
    ).first()

    if task_file is None:
        return jsonify({"error": "File not found"}), 404

    # delete from disk
    file_path = os.path.join(UPLOAD_FOLDER, task_file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # delete from database
    db.session.delete(task_file)
    db.session.commit()

    return jsonify({"message": "File deleted successfully"}), 200


# -----------------------------------------------
# VIEW/DOWNLOAD — GET /uploads/<filename>
# -----------------------------------------------
@files.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)