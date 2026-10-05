
"""
CivicConnect - Department Dashboard Data

Purpose:
    Provides helper functions for reading department-wise
    complaint information from the existing database.

IMPORTANT:
    This is a NEW helper file.
    No existing project file is modified.
"""

from models import (
    Complaint,
    Department,
    User
)


# ============================================================
# GET DEPARTMENT
# ============================================================

def get_department(department_id):
    """
    Get a department using its database ID.
    """

    if not department_id:
        return None

    return Department.query.get(department_id)


# ============================================================
# GET DEPARTMENT COMPLAINTS
# ============================================================

def get_department_complaints(department_id):
    """
    Return all complaints assigned to a department.
    """

    if not department_id:
        return []

    return (
        Complaint.query
        .filter_by(department_id=department_id)
        .order_by(Complaint.created_at.desc())
        .all()
    )


# ============================================================
# GET DEPARTMENT OFFICERS
# ============================================================

def get_department_officers():
    """
    Return all users having officer role.

    Department-specific officer mapping is not stored
    in the current User model, so this function returns
    available officers from the existing database.
    """

    return (
        User.query
        .filter_by(role="officer")
        .order_by(User.name.asc())
        .all()
    )


# ============================================================
# DEPARTMENT STATISTICS
# ============================================================

def get_department_statistics(department_id):
    """
    Calculate complaint statistics for a department.
    """

    complaints = get_department_complaints(department_id)

    total = len(complaints)

    pending = sum(
        1 for complaint in complaints
        if complaint.status == "Pending"
    )

    assigned = sum(
        1 for complaint in complaints
        if complaint.status == "Assigned"
    )

    in_progress = sum(
        1 for complaint in complaints
        if complaint.status == "In Progress"
    )

    resolved = sum(
        1 for complaint in complaints
        if complaint.status == "Resolved"
    )

    closed = sum(
        1 for complaint in complaints
        if complaint.status == "Closed"
    )

    high_priority = sum(
        1 for complaint in complaints
        if complaint.priority == "High"
        and complaint.status not in ["Resolved", "Closed"]
    )

    return {
        "total": total,
        "pending": pending,
        "assigned": assigned,
        "in_progress": in_progress,
        "resolved": resolved,
        "closed": closed,
        "high_priority": high_priority
    }


# ============================================================
# DEPARTMENT SUMMARY
# ============================================================

def get_department_summary(department_id):
    """
    Return department information along with statistics.
    """

    department = get_department(department_id)

    if not department:
        return None

    statistics = get_department_statistics(
        department_id
    )

    return {
        "department": department,
        "statistics": statistics
    }


# ============================================================
# UNASSIGNED COMPLAINTS
# ============================================================

def get_unassigned_complaints():
    """
    Find complaints that do not have a department assigned.
    """

    return (
        Complaint.query
        .filter(
            Complaint.department_id.is_(None)
        )
        .order_by(Complaint.created_at.desc())
        .all()
    )


# ============================================================
# HIGH PRIORITY COMPLAINTS
# ============================================================

def get_high_priority_complaints(department_id):
    """
    Return unresolved high-priority complaints
    for a particular department.
    """

    if not department_id:
        return []

    return (
        Complaint.query
        .filter_by(
            department_id=department_id,
            priority="High"
        )
        .filter(
            Complaint.status.notin_(
                ["Resolved", "Closed"]
            )
        )
        .order_by(Complaint.created_at.desc())
        .all()
    )


# ============================================================
# RECENT COMPLAINTS
# ============================================================

def get_recent_department_complaints(
    department_id,
    limit=10
):
    """
    Return recent complaints for a department.
    """

    if not department_id:
        return []

    return (
        Complaint.query
        .filter_by(department_id=department_id)
        .order_by(Complaint.created_at.desc())
        .limit(limit)
        .all()
    )


# ============================================================
# TEST DATABASE CONNECTION
# ============================================================

if __name__ == "__main__":

    from app import app

    print("\n==========================================")
    print(" CIVICCONNECT DEPARTMENT DATA TEST")
    print("==========================================\n")

    with app.app_context():

        departments = (
            Department.query
            .order_by(Department.name.asc())
            .all()
        )

        if not departments:
            print("No departments found in database.")

        else:

            for department in departments:

                stats = get_department_statistics(
                    department.id
                )

                print(
                    f"Department : {department.name}"
                )

                print(
                    f"Total      : {stats['total']}"
                )

                print(
                    f"Pending    : {stats['pending']}"
                )

                print(
                    f"Assigned   : {stats['assigned']}"
                )

                print(
                    f"In Progress: {stats['in_progress']}"
                )

                print(
                    f"Resolved   : {stats['resolved']}"
                )

                print(
                    f"Closed     : {stats['closed']}"
                )

                print(
                    f"High Priority: "
                    f"{stats['high_priority']}"
                )

                print("------------------------------------------")

    print("\nDepartment data test completed.")

