from app import app

from auto_department_assignment import auto_assign_complaint
from department_officer_assignment import assign_officer_to_complaint


def route_complaint(complaint_id):
    """
    Complete routing process:

    Complaint
        ↓
    Department
        ↓
    Officer
    """

    print()
    print("========================================")
    print("       CIVICCONNECT COMPLAINT ROUTING")
    print("========================================")
    print()

    # ------------------------------------------------
    # STEP 1: Assign Department
    # ------------------------------------------------

    department_result = auto_assign_complaint(
        complaint_id
    )

    print("Department Assignment:")
    print(department_result)

    if not department_result.get("success"):
        return {
            "success": False,
            "stage": "department",
            "message": department_result.get(
                "message",
                "Department assignment failed."
            )
        }

    # ------------------------------------------------
    # STEP 2: Assign Officer
    # ------------------------------------------------

    officer_result = assign_officer_to_complaint(
        complaint_id
    )

    print()
    print("Officer Assignment:")
    print(officer_result)

    if not officer_result.get("success"):
        return {
            "success": False,
            "stage": "officer",
            "message": officer_result.get(
                "message",
                "Officer assignment failed."
            )
        }

    # ------------------------------------------------
    # SUCCESS
    # ------------------------------------------------

    print()
    print("========================================")
    print("       ROUTING COMPLETED")
    print("========================================")
    print()

    print(
        "Complaint:",
        complaint_id
    )

    print(
        "Department:",
        department_result.get(
            "department_name"
        )
    )

    print(
        "Officer:",
        officer_result.get(
            "officer_name"
        )
    )

    print(
        "Status:",
        officer_result.get(
            "status"
        )
    )

    print()

    return {
        "success": True,
        "complaint_id": complaint_id,
        "department_name": department_result.get(
            "department_name"
        ),
        "officer_name": officer_result.get(
            "officer_name"
        ),
        "status": officer_result.get(
            "status"
        )
    }


def route_all_pending_complaints():

    from models import Complaint

    complaints = Complaint.query.filter(
        Complaint.status == "Pending"
    ).all()

    results = []

    for complaint in complaints:

        result = route_complaint(
            complaint.id
        )

        results.append(result)

    return results


if __name__ == "__main__":

    with app.app_context():

        print()
        print("CivicConnect Automatic Complaint Routing")
        print()

        route_all_pending_complaints()
