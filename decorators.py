from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models.user import User

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        user    = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated

def owner_or_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id  = get_jwt_identity()
        user     = User.query.get(user_id)
        task_id  = kwargs.get('task_id')

        if not user:
            return jsonify({"error": "User not found"}), 404

        # admin can do anything
        if user.role == 'admin':
            return f(*args, **kwargs)

        # regular user can only touch their own tasks
        from models.task import Task
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        if task.user_id != int(user_id):
            return jsonify({"error": "You can only modify your own tasks"}), 403

        return f(*args, **kwargs)
    return decorated