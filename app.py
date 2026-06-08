from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from models.task import db, Task
from models.user import User
from models.token import RefreshToken
from auth import auth
import logging

from models.file import TaskFile
from files import files
# -----------------------------------------------
# LOGGING SETUP
# -----------------------------------------------
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = 'uploads'
db.init_app(app)
jwt = JWTManager(app)

# register auth blueprint
app.register_blueprint(auth)
app.register_blueprint(files)

with app.app_context():
    db.create_all()
    print("✅ Tables created successfully!")

VALID_PRIORITIES = ['low', 'medium', 'high']


# -----------------------------------------------
# READ ALL — GET /tasks
# -----------------------------------------------
@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    logger.debug(f"GET /tasks called by user {user_id}")

    done_filter     = request.args.get('done',     None)
    search          = request.args.get('search',   None)
    priority_filter = request.args.get('priority', None)

    query = Task.query

    if done_filter is not None:
        if done_filter.lower() not in ['true', 'false']:
            return jsonify({"error": "done must be 'true' or 'false'"}), 400
        is_done = done_filter.lower() == 'true'
        query   = query.filter(Task.done == is_done)

    if priority_filter is not None:
        if priority_filter.lower() not in VALID_PRIORITIES:
            return jsonify({"error": f"priority must be one of {VALID_PRIORITIES}"}), 400
        query = query.filter(Task.priority == priority_filter.lower())

    if search is not None:
        if len(search.strip()) < 1:
            return jsonify({"error": "search term cannot be empty"}), 400
        query = query.filter(Task.title.ilike(f'%{search}%'))

    tasks = query.all()
    logger.info(f"User {user_id} fetched {len(tasks)} tasks")
    return jsonify({"tasks": [t.to_dict() for t in tasks], "count": len(tasks)}), 200


# -----------------------------------------------
# READ ONE — GET /tasks/<id>
# -----------------------------------------------
@app.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    logger.debug(f"GET /tasks/{task_id} called by user {user_id}")

    if task_id <= 0:
        return jsonify({"error": "ID must be a positive number"}), 400

    task = Task.query.get(task_id)
    if task is None:
        logger.warning(f"Task {task_id} not found")
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task.to_dict()), 200


# -----------------------------------------------
# CREATE — POST /tasks
# -----------------------------------------------
@app.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    try:
        logger.debug(f"POST /tasks called by user {user_id}")
        data = request.get_json()
        logger.debug(f"Request body received: {data}")

        # VALIDATION 1 — body exists
        if not data:
            logger.warning("POST /tasks — body missing")
            return jsonify({"error": "Request body is missing"}), 400

        # VALIDATION 2 — title exists
        if "title" not in data:
            logger.warning("POST /tasks — title missing")
            return jsonify({"error": "Title is required"}), 400

        # VALIDATION 3 — title is a string
        if not isinstance(data["title"], str):
            return jsonify({"error": "Title must be a string"}), 400

        # VALIDATION 4 — title not empty
        if not data["title"].strip():
            return jsonify({"error": "Title cannot be empty"}), 400

        # VALIDATION 5 — title min length
        if len(data["title"].strip()) < 3:
            return jsonify({"error": "Title too short (min 3 chars)"}), 400

        # VALIDATION 6 — title max length
        if len(data["title"].strip()) > 100:
            return jsonify({"error": "Title too long (max 100 chars)"}), 400

        # VALIDATION 7 — title not only numbers
        if data["title"].strip().isnumeric():
            return jsonify({"error": "Title cannot be only numbers"}), 400

        # VALIDATION 8 — priority valid
        if "priority" in data and data["priority"] not in VALID_PRIORITIES:
            return jsonify({"error": "Priority must be low, medium or high"}), 400

        # VALIDATION 9 — done is boolean
        if "done" in data and not isinstance(data["done"], bool):
            return jsonify({"error": "Done must be true or false"}), 400

        # VALIDATION 10 — description is string
        if "description" in data and not isinstance(data["description"], str):
            return jsonify({"error": "Description must be a string"}), 400

        # VALIDATION 11 — description max length
        if "description" in data and len(data["description"]) > 500:
            return jsonify({"error": "Description too long (max 500 chars)"}), 400

        new_task = Task(
            title       = data["title"].strip(),
            description = data.get("description", None),
            priority    = data.get("priority", "medium"),
            done        = data.get("done", False)
        )
        db.session.add(new_task)
        db.session.commit()
        logger.info(f"Task created by user {user_id}: {new_task.to_dict()}")
        return jsonify(new_task.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in POST /tasks: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------
# UPDATE — PUT /tasks/<id>
# -----------------------------------------------
@app.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    try:
        logger.debug(f"PUT /tasks/{task_id} called by user {user_id}")

        if task_id <= 0:
            return jsonify({"error": "ID must be a positive number"}), 400

        task = Task.query.get(task_id)
        if task is None:
            logger.warning(f"PUT /tasks/{task_id} — task not found")
            return jsonify({"error": "Task not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is missing"}), 400
        if len(data) == 0:
            return jsonify({"error": "No fields provided to update"}), 400

        if "title" in data:
            if not isinstance(data["title"], str):
                return jsonify({"error": "Title must be a string"}), 400
            if not data["title"].strip():
                return jsonify({"error": "Title cannot be empty"}), 400
            if len(data["title"].strip()) < 3:
                return jsonify({"error": "Title too short (min 3 chars)"}), 400
            if len(data["title"].strip()) > 100:
                return jsonify({"error": "Title too long (max 100 chars)"}), 400
            if data["title"].strip().isnumeric():
                return jsonify({"error": "Title cannot be only numbers"}), 400
            task.title = data["title"].strip()

        if "done" in data:
            if not isinstance(data["done"], bool):
                return jsonify({"error": "Done must be true or false"}), 400
            task.done = data["done"]

        if "priority" in data:
            if data["priority"] not in VALID_PRIORITIES:
                return jsonify({"error": "Priority must be low, medium or high"}), 400
            task.priority = data["priority"]

        if "description" in data:
            if not isinstance(data["description"], str):
                return jsonify({"error": "Description must be a string"}), 400
            if len(data["description"]) > 500:
                return jsonify({"error": "Description too long (max 500 chars)"}), 400
            task.description = data["description"]

        db.session.commit()
        logger.info(f"Task {task_id} updated by user {user_id}: {task.to_dict()}")
        return jsonify(task.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in PUT /tasks/{task_id}: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------
# DELETE — DELETE /tasks/<id>
# -----------------------------------------------
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    try:
        logger.debug(f"DELETE /tasks/{task_id} called by user {user_id}")

        if task_id <= 0:
            return jsonify({"error": "ID must be a positive number"}), 400

        task = Task.query.get(task_id)
        if task is None:
            logger.warning(f"DELETE /tasks/{task_id} — task not found")
            return jsonify({"error": "Task not found"}), 404

        db.session.delete(task)
        db.session.commit()
        logger.info(f"Task {task_id} deleted by user {user_id}")
        return jsonify({"message": f"Task {task_id} deleted"}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in DELETE /tasks/{task_id}: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------
# HEALTH CHECK — no auth needed
# -----------------------------------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "uptime": "100%"}), 200


if __name__ == '__main__':
    app.run(debug=True)