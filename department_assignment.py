
"""
CivicConnect - Department Assignment System

Purpose:
    Handles assignment of a complaint to a municipal department
    and optionally to a responsible officer.

IMPORTANT:
    This is a NEW helper file.
    Existing CivicConnect files are not modified.
"""

from datetime import datetime

from department_issue_router import route_issue


# ============================================================
# ASSIGN COMPLAINT TO DEPARTMENT
# ============================================================

def assign_to_department(complaint_id, issue_type):
    """
    Automatically identify the correct department
    for a complaint.

    Example:
        Pothole -> Road & Public Works
    """

    if not complaint_id:
        return {
            "success": False,
            "complaint_id": complaint_id,
            "department": None,
            "status": "Pending",
            "message": "Complaint ID is required."
        }

    result = route_issue(issue_type)

    if not result["success"]:
        return {
            "success": False,
            "complaint_id": complaint_id,
            "department": None,
            "status": "Pending",
            "message": result["message"]
        }

    return {
        "success": True,
        "complaint_id": complaint_id,
        "issue_type": issue_type,
        "department": result["department"],
        "officer_id": None,
        "status": "Assigned",
        "assigned_at": datetime.now(),
        "message": (
            f"Complaint #{complaint_id} assigned to "
            f"{result['department']}."
        )
    }


# ============================================================
# ASSIGN OFFICER
# ============================================================

def assign_officer(assignment, officer_id):
    """
    Assign a municipal officer to an already assigned complaint.
    """

    if not assignment:
        return {
            "success": False,
            "message": "Assignment information is missing."
        }

    if not officer_id:
        return {
            "success": False,
            "message": "Officer ID is required."
        }

    assignment["officer_id"] = officer_id

    if assignment.get("status") == "Pending":
        assignment["status"] = "Assigned"

    assignment["assigned_at"] = (
        assignment.get("assigned_at")
        or datetime.now()
    )

    assignment["message"] = (
        f"Complaint #{assignment.get('complaint_id')} "
        f"assigned to officer #{officer_id}."
    )

    return {
        "success": True,
        **assignment
    }


# ============================================================
# START WORK
# ============================================================

def start_department_work(assignment):
    """
    Department officer starts working on the complaint.
    """

    if not assignment:
        return {
            "success": False,
            "message": "Assignment information is missing."
        }

    if not assignment.get("department"):
        return {
            "success": False,
            "message": "No department has been assigned."
        }

    if not assignment.get("officer_id"):
        return {
            "success": False,
            "message": "No officer has been assigned."
        }

    assignment["status"] = "In Progress"
    assignment["work_started_at"] = datetime.now()

    assignment["message"] = (
        f"Department {assignment['department']} "
        f"has started working on complaint "
        f"#{assignment['complaint_id']}."
    )

    return {
        "success": True,
        **assignment
    }


# ============================================================
# RESOLVE COMPLAINT
# ============================================================

def resolve_department_complaint(assignment, resolution_remark):
    """
    Department marks the complaint as resolved.
    """

    if not assignment:
        return {
            "success": False,
            "message": "Assignment information is missing."
        }

    if assignment.get("status") != "In Progress":
        return {
            "success": False,
            "message": (
                "Complaint must be In Progress "
                "before it can be resolved."
            )
        }

    if not resolution_remark or not resolution_remark.strip():
        return {
            "success": False,
            "message": "Resolution remark is required."
        }

    assignment["status"] = "Resolved"
    assignment["resolved_at"] = datetime.now()
    assignment["resolution_remark"] = resolution_remark.strip()

    assignment["message"] = (
        f"Complaint #{assignment['complaint_id']} "
        f"has been marked as Resolved."
    )

    return {
        "success": True,
        **assignment
    }


# ============================================================
# CLOSE COMPLAINT
# ============================================================

def close_department_complaint(assignment):
    """
    Close a complaint after it has been resolved.
    """

    if not assignment:
        return {
            "success": False,
            "message": "Assignment information is missing."
        }

    if assignment.get("status") != "Resolved":
        return {
            "success": False,
            "message": (
                "Only a Resolved complaint "
                "can be Closed."
            )
        }

    assignment["status"] = "Closed"
    assignment["closed_at"] = datetime.now()

    assignment["message"] = (
        f"Complaint #{assignment['complaint_id']} "
        f"has been Closed."
    )

    return {
        "success": True,
        **assignment
    }


# ============================================================
# COMPLETE WORKFLOW
# ============================================================

def run_assignment_workflow(
    complaint_id,
    issue_type,
    officer_id,
    resolution_remark
):
    """
    Demonstrates the complete department workflow.

    Pending
       ↓
    Assigned
       ↓
    In Progress
       ↓
    Resolved
       ↓
    Closed
    """

    assignment_result = assign_to_department(
        complaint_id,
        issue_type
    )

    if not assignment_result["success"]:
        return assignment_result

    assignment = assignment_result

    officer_result = assign_officer(
        assignment,
        officer_id
    )

    if not officer_result["success"]:
        return officer_result

    assignment = officer_result

    work_result = start_department_work(
        assignment
    )

    if not work_result["success"]:
        return work_result

    assignment = work_result

    resolve_result = resolve_department_complaint(
        assignment,
        resolution_remark
    )

    if not resolve_result["success"]:
        return resolve_result

    assignment = resolve_result

    close_result = close_department_complaint(
        assignment
    )

    return close_result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n==========================================")
    print(" CIVICCONNECT DEPARTMENT ASSIGNMENT TEST")
    print("==========================================\n")

    result = run_assignment_workflow(
        complaint_id=101,
        issue_type="Pothole",
        officer_id=5,
        resolution_remark=(
            "Pothole repair completed by the "
            "Road & Public Works team."
        )
    )

    print("Complaint ID :", result.get("complaint_id"))
    print("Issue        :", result.get("issue_type"))
    print("Department   :", result.get("department"))
    print("Officer ID   :", result.get("officer_id"))
    print("Status       :", result.get("status"))
    print("Message      :", result.get("message"))

    print("\n==========================================")
    print(" WORKFLOW TEST COMPLETED")
    print("==========================================")

