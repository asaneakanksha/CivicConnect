from app import app
from models import db, Complaint, User, Department
from department_notification_store import add_notification


ACTIVE_STATUSES = ["Pending", "Assigned", "In Progress"]


def get_all_officers():
    """
    Get all users whose role is officer.
    """
    return User.query.filter_by(role="officer").order_by(User.id.asc()).all()


def get_officer_by_id(officer_id):
    """
    Get one officer by ID.
    """
    return User.query.filter_by(
        id=officer_id,
        role="officer"
    ).first()


def get_complaint_by_id(complaint_id):
    """
    Get complaint by ID.
    """
    return Complaint.query.get(complaint_id)


def get_department_by_id(department_id):
    """
    Get department by ID.
    """
    return Department.query.get(department_id)


def get_officer_workload(officer_id):
    """
    Count active complaints currently assigned to an officer.
    """
    return Complaint.query.filter(
        Complaint.assigned_officer_id == officer_id,
        Complaint.status.in_(["Assigned", "In Progress"])
    ).count()


def choose_officer():
    """
    Automatically select an officer.

    Since the current User model does not have department_id,
    this version selects an officer from all officer accounts
    using the lowest active workload.
    """
    officers = get_all_officers()

    if not officers:
        return None

    officers.sort(key=lambda officer: get_officer_workload(officer.id))

    return officers[0]


def assign_officer_to_complaint(complaint_id, officer_id=None):
    """
    Assign a specific officer to a complaint.

    If officer_id is not provided, the officer with the
    lowest active workload is selected automatically.
    """

    complaint = get_complaint_by_id(complaint_id)

    if not complaint:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    if not complaint.department_id:
        return {
            "success": False,
            "message": "Complaint has no department assigned yet."
        }

    if complaint.status in ["Resolved", "Closed"]:
        return {
            "success": False,
            "message": "Complaint is already " + complaint.status + "."
        }

    # Already assigned
    if complaint.assigned_officer_id:
        officer = get_officer_by_id(complaint.assigned_officer_id)

        return {
            "success": True,
            "message": "Complaint is already assigned to an officer.",
            "complaint_id": complaint.id,
            "officer_id": complaint.assigned_officer_id,
            "officer_name": officer.name if officer else "Unknown",
            "status": complaint.status
        }

    # Select specific officer
    if officer_id is not None:
        officer = get_officer_by_id(officer_id)

        if not officer:
            return {
                "success": False,
                "message": "Invalid officer ID or user is not an officer."
            }

    # Automatically select officer
    else:
        officer = choose_officer()

        if not officer:
            return {
                "success": False,
                "message": "No officer account exists. Create an officer account first."
            }

    department = get_department_by_id(complaint.department_id)

    # Assign officer
    complaint.assigned_officer_id = officer.id

    if complaint.status == "Pending":
        complaint.status = "Assigned"

    db.session.commit()

    # Create persistent notification
    try:
        add_notification(
            notification_type="officer_assignment",
            title="New Complaint Assigned",
            message=(
                "Complaint #" + str(complaint.id)
                + " has been assigned to you."
            ),
            complaint_id=complaint.id,
            department_id=complaint.department_id,
            officer_id=officer.id
        )
    except Exception as notification_error:
        print("Notification warning:", notification_error)

    return {
        "success": True,
        "message": "Complaint assigned to officer successfully.",
        "complaint_id": complaint.id,
        "officer_id": officer.id,
        "officer_name": officer.name,
        "department_name": department.name if department else "Unknown",
        "status": complaint.status
    }


def assign_all_unassigned_complaints():
    """
    Automatically assign every complaint that has a department
    but does not yet have an officer.
    """

    complaints = Complaint.query.filter(
        Complaint.department_id.isnot(None),
        Complaint.assigned_officer_id.is_(None),
        Complaint.status.in_(ACTIVE_STATUSES)
    ).order_by(Complaint.id.asc()).all()

    results = []

    for complaint in complaints:
        result = assign_officer_to_complaint(complaint.id)
        results.append(result)

    return results


def show_officer_assignments():
    """
    Display actual complaint-officer assignments from MySQL.
    """

    complaints = Complaint.query.order_by(
        Complaint.id.desc()
    ).all()

    print()
    print("========================================")
    print("    CIVICCONNECT OFFICER ASSIGNMENTS")
    print("========================================")

    if not complaints:
        print("No complaints found.")
        return

    for complaint in complaints:

        department_name = "Not Assigned"
        officer_name = "Not Assigned"

        if complaint.department:
            department_name = complaint.department.name

        if complaint.assigned_officer:
            officer_name = complaint.assigned_officer.name

        print()
        print("Complaint ID :", complaint.id)
        print("Issue Type   :", complaint.issue_type)
        print("Department   :", department_name)
        print("Officer      :", officer_name)
        print("Status       :", complaint.status)
        print("----------------------------------------")


def run_officer_assignment():

    print()
    print("========================================")
    print(" CivicConnect Officer Assignment System")
    print("========================================")

    officers = get_all_officers()

    print()
    print("Available Officers:")

    if not officers:
        print("NO OFFICERS FOUND.")
        print()
        print("Create at least one user with role = officer.")
        return

    for officer in officers:
        print(
            "ID:",
            officer.id,
            "| Name:",
            officer.name,
            "| Active Complaints:",
            get_officer_workload(officer.id)
        )

    print()
    print("Assigning unassigned complaints...")

    results = assign_all_unassigned_complaints()

    if not results:
        print()
        print("No unassigned complaints found.")

    else:
        for result in results:

            print()

            if result["success"]:
                print("SUCCESS")
                print("Complaint :", result.get("complaint_id"))
                print("Officer   :", result.get("officer_name"))
                print("Department:", result.get("department_name"))
                print("Status    :", result.get("status"))

            else:
                print("FAILED")
                print(result.get("message"))

    show_officer_assignments()


if __name__ == "__main__":

    with app.app_context():
        run_officer_assignment()
