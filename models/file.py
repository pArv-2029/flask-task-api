from models.task import db
from datetime import datetime

class TaskFile(db.Model):
    __tablename__ = 'task_files'

    id          = db.Column(db.Integer, primary_key=True)
    task_id     = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    filename    = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_type   = db.Column(db.String(50), nullable=False)
    file_size   = db.Column(db.Integer, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":            self.id,
            "task_id":       self.task_id,
            "filename":      self.filename,
            "original_name": self.original_name,
            "file_type":     self.file_type,
            "file_size":     self.file_size,
            "url":           f"/uploads/{self.filename}",
            "uploaded_at":   self.uploaded_at.isoformat()
        }