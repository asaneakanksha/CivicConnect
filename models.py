from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


db = SQLAlchemy()


# =====================================================
# USER
# =====================================================

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="citizen"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def set_password(self, password):

        self.password = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password,
            password
        )


# =====================================================
# DEPARTMENT
# =====================================================

class Department(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )


# =====================================================
# COMPLAINT
# =====================================================

class Complaint(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    issue_type = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    location = db.Column(
        db.String(255),
        nullable=False
    )

    image = db.Column(
        db.String(255)
    )

    status = db.Column(
        db.String(30),
        default="Pending"
    )

    priority = db.Column(
        db.String(20),
        default="Medium"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("department.id")
    )

    assigned_officer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    citizen = db.relationship(
        "User",
        foreign_keys=[user_id]
    )

    department = db.relationship(
        "Department"
    )

    assigned_officer = db.relationship(
        "User",
        foreign_keys=[assigned_officer_id]
    )


# =====================================================
# REMARK
# =====================================================

class Remark(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey("complaint.id"),
        nullable=False
    )

    officer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    remark = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    officer = db.relationship(
        "User"
    )

    complaint = db.relationship(
        "Complaint"
    )