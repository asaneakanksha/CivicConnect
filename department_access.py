
"""
CivicConnect - Department Access Control

Purpose:
    Controls which complaints a municipal department or
    officer is allowed to view and process.

IMPORTANT:
    This is a NEW helper file.
    Existing CivicConnect files are not modified.
"""

from models import Complaint, Department, User


# ============================================================
# CHECK DEPARTMENT ACCESS
# ============================================================

def department_can_access_complaint(
    department_id,
    complaint_id
):
    """
    Check whether a department can access a complaint.
    """

    if not department_id or not complaint_id:
        return False

    complaint = Complaint.query.get(
        complaint_id
    )

    if complaint is None:
        return False

    return complaint.department_id == department_id


# ============================================================
# CHECK OFFICER ACCESS
# ============================================================

def officer_can_access_complaint(
    officer_id,
    complaint_id
):
    """
    Check whether an officer is assigned to
    a particular complaint.
    """

    if not officer_id or not complaint_id:
        return False

    officer = User.query.get(
        officer_id
    )

    if officer is None:
        return False

    if officer.role != "officer":
        return False

    complaint = Complaint.query.get(
        complaint_id
    )

    if complaint is None:
        return False

    return (
        complaint.assigned_officer_id
        == officer_id
    )


# ============================================================
# GET DEPARTMENT COMPLAINTS
# ============================================================

def get_accessible_complaints(
    department_id
):
    """
    Return only complaints assigned to the department.
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

def get_officer_accessible_complaints(
    officer_id
):
    """
    Return only complaints assigned to the officer.
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
# GET DEPARTMENT PENDING COMPLAINTS
# ============================================================

def get_department_pending_complaints(
    department_id
):
    """
    Return unresolved complaints that need department action.
    """

    if not department_id:
        return []

    return (
        Complaint.query
        .filter_by(
            department_id=department_id
        )
        .filter(
            Complaint.status.notin_(
                ["Resolved", "Closed"]
            )
        )
        .order_by(
            Complaint.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET OFFICER ACTIVE COMPLAINTS
# ============================================================

def get_officer_active_complaints(
    officer_id
):
    """
    Return active complaints assigned to an officer.
    """

    if not officer_id:
        return []

    return (
        Complaint.query
        .filter_by(
            assigned_officer_id=officer_id
        )
        .filter(
            Complaint.status.notin_(
                ["Resolved", "Closed"]
            )
        )
        .order_by(
            Complaint.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET HIGH PRIORITY DEPARTMENT COMPLAINTS
# ============================================================

def get_department_urgent_complaints(
    department_id
):
    """
    Return unresolved High-priority complaints
    for a department.
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
        .order_by(
            Complaint.created_at.desc()
        )
        .all()
    )


# ============================================================
# CHECK WHETHER COMPLAINT IS COMPLETED
# ============================================================

def complaint_is_completed(
    complaint_id
):
    """
    Check whether a complaint has been resolved or closed.
    """

    complaint = Complaint.query.get(
        complaint_id
    )

    if complaint is None:
        return False

    return complaint.status in [
        "Resolved",
        "Closed"
    ]


# ============================================================
# GET ACCESS SUMMARY
# ============================================================

def get_department_access_summary(
    department_id
):
    """
    Return a simple summary of department workload.
    """

    complaints = get_accessible_complaints(
        department_id
    )

    return {
        "total": len(complaints),

        "pending": sum(
            1 for complaint in complaints
            if complaint.status == "Pending"
        ),

        "assigned": sum(
            1 for complaint in complaints
            if complaint.status == "Assigned"
        ),

        "in_progress": sum(
            1 for complaint in complaints
            if complaint.status == "In Progress"
        ),

        "resolved": sum(
            1 for complaint in complaints
            if complaint.status == "Resolved"
        ),

        "closed": sum(
            1 for complaint in complaints
            if complaint.status == "Closed"
        ),

        "urgent": sum(
            1 for complaint in complaints
            if complaint.priority == "High"
            and complaint.status not in [
                "Resolved",
                "Closed"
            ]
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from app import app

    print("\n==========================================")
    print(" CIVICCONNECT DEPARTMENT ACCESS TEST")
    print("==========================================\n")

    with app.app_context():

        departments = (
            Department.query
            .order_by(Department.name.asc())
            .all()
        )

        if not departments:

            print(
                "No departments found."
            )

        else:

            for department in departments:

                summary = get_department_access_summary(
                    department.id
                )

                print(
                    f"Department : {department.name}"
                )

                print(
                    f"Total      : {summary['total']}"
                )

                print(
                    f"Pending    : {summary['pending']}"
                )

                print(
                    f"Assigned   : {summary['assigned']}"
                )

                print(
                    f"In Progress: {summary['in_progress']}"
                )

                print(
                    f"Resolved   : {summary['resolved']}"
                )

                print(
                    f"Closed     : {summary['closed']}"
                )

                print(
                    f"Urgent     : {summary['urgent']}"
                )

                print("------------------------------------------")

    print("\nAccess test completed.")

