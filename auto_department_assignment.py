from app import app
from models import db, Complaint, Department
from department_data import get_department_for_issue
from department_notification_store import add_notification


KEYWORD_DEPARTMENT_MAP = {
    "Road & Public Works": [
        "pothole",
        "damaged road",
        "road repair",
        "broken road",
        "footpath",
        "open manhole",
        "divider",
        "road"
    ],
    "Solid Waste Management": [
        "garbage",
        "waste",
        "dumping",
        "garbage overflow",
        "waste disposal"
    ],
    "Water Supply": [
        "water leakage",
        "water supply",
        "pipeline",
        "pipe leakage",
        "low water pressure",
        "water contamination"
    ],
    "Drainage & Sewerage": [
        "drainage",
        "sewage",
        "waterlogging",
        "blocked drain",
        "sewer",
        "drain blockage"
    ],
    "Electrical & Street Lighting": [
        "streetlight",
        "street light",
        "electrical pole",
        "electrical wiring",
        "public lighting"
    ],
    "Parks & Garden": [
        "park",
        "tree",
        "fallen tree",
        "garden",
        "green area"
    ],
    "Town Planning": [
        "illegal construction",
        "unauthorized construction",
        "building violation",
        "encroachment"
    ],
    "Public Health": [
        "sanitation",
        "mosquito",
        "unhygienic",
        "health hazard",
        "public health"
    ]
}


def find_department_for_issue(issue_type):
    if not issue_type:
        return None

    issue = issue_type.strip()

    department_name = get_department_for_issue(issue)

    if department_name:
        return department_name

    issue_lower = issue.lower()

    for department, keywords in KEYWORD_DEPARTMENT_MAP.items():
        for keyword in keywords:
            if keyword.lower() in issue_lower:
                return department

    return None


def get_department_object(department_name):
    if not department_name:
        return None

    return Department.query.filter_by(
        name=department_name
    ).first()


def preview_assignment(complaint_id):
    complaint = Complaint.query.get(complaint_id)

    if not complaint:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    department_name = find_department_for_issue(
        complaint.issue_type
    )

    if not department_name:
        return {
            "success": False,
            "message": (
                "No department mapping found for issue: "
                + str(complaint.issue_type)
            )
        }

    department = get_department_object(department_name)

    if not department:
        return {
            "success": False,
            "message": (
                "Department does not exist in database: "
                + department_name
            )
        }

    return {
        "success": True,
        "complaint_id": complaint.id,
        "issue_type": complaint.issue_type,
        "department_id": department.id,
        "department_name": department.name,
        "current_status": complaint.status
    }


def auto_assign_complaint(complaint_id):
    complaint = Complaint.query.get(complaint_id)

    if not complaint:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    if complaint.status in ["Resolved", "Closed"]:
        return {
            "success": False,
            "message": "Complaint is already "
                       + complaint.status
                       + "."
        }

    if complaint.department_id:
        department = Department.query.get(
            complaint.department_id
        )

        return {
            "success": True,
            "message": "Complaint is already assigned.",
            "complaint_id": complaint.id,
            "department_name": (
                department.name
                if department
                else "Unknown"
            ),
            "status": complaint.status
        }

    department_name = find_department_for_issue(
        complaint.issue_type
    )

    if not department_name:
        return {
            "success": False,
            "message": (
                "No department found for issue type: "
                + str(complaint.issue_type)
            )
        }

    department = get_department_object(
        department_name
    )

    if not department:
        return {
            "success": False,
            "message": (
                "Department is missing from database: "
                + department_name
                + ". Run department_seed.py first."
            )
        }

    complaint.department_id = department.id

    if complaint.status == "Pending":
        complaint.status = "Assigned"

    db.session.commit()

    try:
        add_notification(
            notification_type="new_complaint",
            title="New Complaint Assigned",
            message=(
                "Complaint #"
                + str(complaint.id)
                + " has been assigned to "
                + department.name
                + "."
            ),
            complaint_id=complaint.id,
            department_id=department.id
        )
    except Exception as notification_error:
        print(
            "Notification warning:",
            notification_error
        )

    return {
        "success": True,
        "message": "Complaint automatically assigned.",
        "complaint_id": complaint.id,
        "department_id": department.id,
        "department_name": department.name,
        "status": complaint.status
    }


def auto_assign_pending_complaints():
    complaints = Complaint.query.filter(
        Complaint.department_id.is_(None),
        Complaint.status == "Pending"
    ).all()

    results = []

    for complaint in complaints:
        result = auto_assign_complaint(
            complaint.id
        )
        results.append(result)

    return results


def show_assignments():
    complaints = Complaint.query.order_by(
        Complaint.id.desc()
    ).all()

    print()
    print("========================================")
    print("       CIVICCONNECT DEPARTMENT MAP")
    print("========================================")

    if not complaints:
        print("No complaints found.")
        return

    for complaint in complaints:
        department_name = "Not Assigned"

        if complaint.department:
            department_name = complaint.department.name

        print()
        print("Complaint ID :", complaint.id)
        print("Issue Type   :", complaint.issue_type)
        print("Department   :", department_name)
        print("Status       :", complaint.status)
        print("----------------------------------------")


def run_auto_assignment():
    print()
    print("========================================")
    print(" CivicConnect Auto Department Assignment")
    print("========================================")

    results = auto_assign_pending_complaints()

    if not results:
        print()
        print("No pending unassigned complaints found.")
    else:
        for result in results:
            if result["success"]:
                print()
                print("SUCCESS")
                print("Complaint:", result.get("complaint_id"))
                print("Department:", result.get("department_name"))
                print("Status:", result.get("status"))
            else:
                print()
                print("FAILED")
                print(result.get("message"))

    show_assignments()


if __name__ == "__main__":
    with app.app_context():
        run_auto_assignment()
