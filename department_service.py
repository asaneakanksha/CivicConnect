
"""
CivicConnect - Department Service

Purpose:
    Provides database-level services for municipal departments.

    This file connects the existing models with the
    department workflow.

IMPORTANT:
    This is a NEW file.
    Existing project files are not modified.
"""

from datetime import datetime

from models import (
    db,
    Complaint,
    Department,
    User,
    Remark
)

from department_issue_router import route_issue


# ============================================================
# GET ALL DEPARTMENTS
# ============================================================

def get_all_departments():
    """
    Return all municipal departments.
    """

    return (
        Department.query
        .order_by(Department.name.asc())
        .all()
    )


# ============================================================
# GET DEPARTMENT BY ID
# ============================================================

def get_department_by_id(department_id):
    """
    Find a department using its ID.
    """

    if not department_id:
        return None

    return Department.query.get(department_id)


# ============================================================
# GET OFFICERS
# ============================================================

def get_all_officers():
    """
    Return all users whose role is officer.
    """

    return (
        User.query
        .filter_by(role="officer")
        .order_by(User.name.asc())
        .all()
    )


# ============================================================
# GET COMPLAINT
# ============================================================

def get_complaint_by_id(complaint_id):
    """
    Find a complaint using its ID.
    """

    if not complaint_id:
        return None

    return Complaint.query.get(complaint_id)


# ============================================================
# AUTO ROUTE COMPLAINT
# ============================================================

def suggest_department_for_complaint(complaint):
    """
    Automatically suggest a department based on
    complaint issue type.

    Example:
        Pothole -> Road & Public Works
        Garbage Overflow -> Solid Waste Management
    """

    if complaint is None:
        return {
            "success": False,
            "department": None,
            "message": "Complaint not found."
        }

    result = route_issue(
        complaint.issue_type
    )

    return result


# ============================================================
# ASSIGN DEPARTMENT
# ============================================================

def assign_department(
    complaint_id,
    department_id
):
    """
    Assign an existing department to a complaint.

    The complaint status becomes Assigned.
    """

    complaint = get_complaint_by_id(
        complaint_id
    )

    if complaint is None:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    department = get_department_by_id(
        department_id
    )

    if department is None:
        return {
            "success": False,
            "message": "Department not found."
        }

    complaint.department_id = department.id
    complaint.status = "Assigned"
    complaint.updated_at = datetime.utcnow()

    db.session.commit()

    return {
        "success": True,
        "complaint": complaint,
        "department": department,
        "message": (
            f"Complaint #{complaint.id} assigned to "
            f"{department.name}."
        )
    }


# ============================================================
# ASSIGN OFFICER
# ============================================================

def assign_officer(
    complaint_id,
    officer_id
):
    """
    Assign an officer to a complaint.
    """

    complaint = get_complaint_by_id(
        complaint_id
    )

    if complaint is None:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    officer = (
        User.query
        .filter_by(
            id=officer_id,
            role="officer"
        )
        .first()
    )

    if officer is None:
        return {
            "success": False,
            "message": "Officer not found."
        }

    if complaint.department_id is None:
        return {
            "success": False,
            "message": (
                "Assign a department before "
                "assigning an officer."
            )
        }

    complaint.assigned_officer_id = officer.id

    if complaint.status == "Pending":
        complaint.status = "Assigned"

    complaint.updated_at = datetime.utcnow()

    db.session.commit()

    return {
        "success": True,
        "complaint": complaint,
        "officer": officer,
        "message": (
            f"Complaint #{complaint.id} assigned to "
            f"officer {officer.name}."
        )
    }


# ============================================================
# START WORK
# ============================================================

def start_work(
    complaint_id,
    officer_id
):
    """
    Officer starts working on the complaint.
    """

    complaint = get_complaint_by_id(
        complaint_id
    )

    if complaint is None:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    if complaint.assigned_officer_id != officer_id:
        return {
            "success": False,
            "message": (
                "This complaint is not assigned "
                "to this officer."
            )
        }

    if complaint.status != "Assigned":
        return {
            "success": False,
            "message": (
                "Only an Assigned complaint "
                "can be started."
            )
        }

    complaint.status = "In Progress"
    complaint.updated_at = datetime.utcnow()

    db.session.commit()

    return {
        "success": True,
        "complaint": complaint,
        "message": (
            f"Work started on complaint "
            f"#{complaint.id}."
        )
    }


# ============================================================
# RESOLVE COMPLAINT
# ============================================================

def resolve_complaint(
    complaint_id,
    officer_id,
    resolution_text
):
    """
    Officer resolves a complaint.

    A Remark is created so the citizen can see
    what was done.
    """

    complaint = get_complaint_by_id(
        complaint_id
    )

    if complaint is None:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    if complaint.assigned_officer_id != officer_id:
        return {
            "success": False,
            "message": (
                "Only the assigned officer "
                "can resolve this complaint."
            )
        }

    if complaint.status != "In Progress":
        return {
            "success": False,
            "message": (
                "Complaint must be In Progress "
                "before resolution."
            )
        }

    if not resolution_text:
        return {
            "success": False,
            "message": (
                "Resolution remark is required."
            )
        }

    resolution_text = resolution_text.strip()

    if not resolution_text:
        return {
            "success": False,
            "message": (
                "Resolution remark cannot be empty."
            )
        }

    complaint.status = "Resolved"
    complaint.updated_at = datetime.utcnow()

    remark = Remark(
        complaint_id=complaint.id,
        officer_id=officer_id,
        remark=resolution_text
    )

    db.session.add(remark)

    db.session.commit()

    return {
        "success": True,
        "complaint": complaint,
        "remark": remark,
        "message": (
            f"Complaint #{complaint.id} "
            "has been resolved."
        )
    }


# ============================================================
# CLOSE COMPLAINT
# ============================================================

def close_complaint(
    complaint_id
):
    """
    Close a resolved complaint.
    """

    complaint = get_complaint_by_id(
        complaint_id
    )

    if complaint is None:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    if complaint.status != "Resolved":
        return {
            "success": False,
            "message": (
                "Only a Resolved complaint "
                "can be closed."
            )
        }

    complaint.status = "Closed"
    complaint.updated_at = datetime.utcnow()

    db.session.commit()

    return {
        "success": True,
        "complaint": complaint,
        "message": (
            f"Complaint #{complaint.id} "
            "has been closed."
        )
    }


# ============================================================
# GET DEPARTMENT COMPLAINTS
# ============================================================

def get_complaints_for_department(
    department_id
):
    """
    Get complaints belonging to a department.
    """

    if not department_id:
        return []

    return (
        Complaint.query
        .filter_by(
            department_id=department_id
        )
        .order_by(
            Complaint.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET OFFICER COMPLAINTS
# ============================================================

def get_complaints_for_officer(
    officer_id
):
    """
    Get complaints assigned to an officer.
    """

    if not officer_id:
        return []

    return (
        Complaint.query
        .filter_by(
            assigned_officer_id=officer_id
        )
        .order_by(
            Complaint.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET DEPARTMENT STATISTICS
# ============================================================

def get_department_statistics(
    department_id
):
    """
    Calculate live statistics for a department.
    """

    complaints = get_complaints_for_department(
        department_id
    )

    return {
        "total": len(complaints),

        "pending": sum(
            1 for c in complaints
            if c.status == "Pending"
        ),

        "assigned": sum(
            1 for c in complaints
            if c.status == "Assigned"
        ),

        "in_progress": sum(
            1 for c in complaints
            if c.status == "In Progress"
        ),

        "resolved": sum(
            1 for c in complaints
            if c.status == "Resolved"
        ),

        "closed": sum(
            1 for c in complaints
            if c.status == "Closed"
        ),

        "high_priority": sum(
            1 for c in complaints
            if c.priority == "High"
            and c.status not in [
                "Resolved",
                "Closed"
            ]
        )
    }


# ============================================================
# GET COMPLAINT TIMELINE
# ============================================================

def get_complaint_timeline(
    complaint_id
):
    """
    Return complaint remarks ordered from
    oldest to newest.
    """

    return (
        Remark.query
        .filter_by(
            complaint_id=complaint_id
        )
        .order_by(
            Remark.created_at.asc()
        )
        .all()
    )


# ============================================================
# TEST DATABASE SERVICE
# ============================================================

if __name__ == "__main__":

    from app import app

    print("\n==========================================")
    print(" CIVICCONNECT DEPARTMENT SERVICE TEST")
    print("==========================================\n")

    with app.app_context():

        departments = get_all_departments()

        print(
            f"Departments found: {len(departments)}"
        )

        for department in departments:

            stats = get_department_statistics(
                department.id
            )

            print(
                f"\nDepartment: {department.name}"
            )

            print(
                f"  Total      : {stats['total']}"
            )

            print(
                f"  Pending    : {stats['pending']}"
            )

            print(
                f"  Assigned   : {stats['assigned']}"
            )

            print(
                f"  In Progress: {stats['in_progress']}"
            )

            print(
                f"  Resolved   : {stats['resolved']}"
            )

            print(
                f"  Closed     : {stats['closed']}"
            )

            print(
                f"  High Priority: "
                f"{stats['high_priority']}"
            )

        officers = get_all_officers()

        print(
            f"\nOfficers found: {len(officers)}"
        )

    print("\n==========================================")
    print(" TEST COMPLETED")
    print("==========================================\n")
