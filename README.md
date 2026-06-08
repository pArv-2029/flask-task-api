# 🚀 Flask Task API

![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=for-the-badge&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?style=for-the-badge)
![JWT](https://img.shields.io/badge/JWT-Authentication-green?style=for-the-badge)
![REST API](https://img.shields.io/badge/REST-API-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

A RESTful Task Management API built using **Flask**, **PostgreSQL**, **SQLAlchemy**, and **JWT Authentication**.

This project was developed as a learning project to understand backend development fundamentals including authentication, database integration, REST APIs, file handling, and Git workflows.

---

## ✨ Features

### 🔐 Authentication

- User Registration
- User Login
- JWT Access Tokens
- Refresh Tokens
- Protected Routes
- Secure Logout
- Token Blacklisting

### 📝 Task Management

- Create Tasks
- Get All Tasks
- Get Single Task
- Update Tasks
- Delete Tasks
- Search Tasks
- Filter Tasks

### 📂 File Management

- Upload Files
- View Uploaded Files
- Delete Uploaded Files
- Serve Uploaded Files

### ❤️ Health Monitoring

- API Health Check Endpoint

---

# 🏗️ Architecture

```text
                ┌─────────────┐
                │   Client    │
                │ Postman/API │
                └──────┬──────┘
                       │
                       ▼
             ┌──────────────────┐
             │    Flask API     │
             └────────┬─────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼

   Auth Module   Task Module   File Module

                      │
                      ▼

             PostgreSQL Database
```

---

# 📌 API Endpoints

## 🔐 Authentication

| Method | Endpoint | Description |
|---------|-----------|------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Login and receive JWT tokens |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout user |

---

## 📝 Tasks

| Method | Endpoint |
|---------|----------|
| GET | `/tasks` |
| GET | `/tasks/<id>` |
| POST | `/tasks` |
| PUT | `/tasks/<id>` |
| DELETE | `/tasks/<id>` |

---

## 📂 Files

| Method | Endpoint |
|---------|----------|
| POST | `/tasks/<id>/upload` |
| GET | `/tasks/<id>/files` |
| DELETE | `/tasks/<id>/files/<id>` |
| GET | `/uploads/<filename>` |

---

## ❤️ Health

| Method | Endpoint |
|---------|----------|
| GET | `/health` |

---

# 🛠️ Tech Stack

| Category | Technology |
|-----------|-----------|
| Language | Python |
| Framework | Flask |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT |
| Testing | Postman |
| Version Control | Git |
| Repository Hosting | GitHub |

---

# 📁 Project Structure

```text
flask-task-api
│
├── app.py
├── auth.py
├── files.py
├── config.py
├── requirements.txt
│
├── models
│   ├── __init__.py
│   ├── user.py
│   ├── task.py
│   ├── token.py
│   └── file.py
│
├── uploads/
│
└── README.md
```

---

# 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/pArv-2029/flask-task-api.git

cd flask-task-api
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure PostgreSQL

Update the database configuration in `config.py`.

### Run Application

```bash
python app.py
```

---

# 🧪 Testing

The API can be tested using:

- Postman
- Thunder Client
- Insomnia
- cURL

---

# 🎯 Learning Outcomes

Through this project I learned:

- REST API Design
- Flask Application Structure
- JWT Authentication
- PostgreSQL Integration
- SQLAlchemy ORM
- File Upload Handling
- API Testing
- Git & GitHub Workflow

---

# 🔮 Future Enhancements

- [ ] Swagger / OpenAPI Documentation
- [ ] Docker Support
- [ ] Unit Testing
- [ ] CI/CD Pipeline
- [ ] Role Based Access Control (RBAC)
- [ ] Pagination
- [ ] Cloud Deployment

---

# 📊 Current Capabilities

| Module | Status |
|---------|---------|
| Authentication | ✅ Complete |
| JWT Security | ✅ Complete |
| CRUD Operations | ✅ Complete |
| File Uploads | ✅ Complete |
| PostgreSQL Integration | ✅ Complete |
| Health Monitoring | ✅ Complete |

---

# 👨‍💻 Author

### Parv

Engineering Student • Backend Development Learner

Built to learn Flask, PostgreSQL, JWT Authentication, REST APIs, and GitHub workflows.

---

⭐ If you found this project interesting, consider starring the repository.