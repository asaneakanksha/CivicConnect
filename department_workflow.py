
# ============================================================
# CIVICCONNECT - DEPARTMENT WORKFLOW
# ============================================================
# NEW FILE
#
# Purpose:
# 1. Find the correct municipal department for a complaint
# 2. Find an available officer from that department
# 3. Create a department assignment
# 4. Track complaint status
# 5. Keep resolution information
#
# Existing project files are NOT modified by this file.
# ============================================================


from datetime import datetime

from department_data import get_department_for_issue


# ============================================================
# STATUS FLOW
# ============================================================

STATUS_FLOW = [
    "Pending",
    "Assigned",
    "In Progress",
    "Resolved",
    "Closed"
]


# ============================================================
# VALID STATUS
# ============================================================

def is_valid_status(status):

    return status in STATUS_FLOW


# ============================================================
# GET NEXT STATUS
# ============================================================

def get_next_status(current_status):

    if current_status not in STATUS_FLOW:
        return None

    current_index = STATUS_FLOW.index(current_status)

    if current_index >= len(STATUS_FLOW) - 1:
        return None

    return STATUS_FLOW[current_index + 1]


# ============================================================
# FIND DEPARTMENT
# ============================================================

def identify_department(issue_type):

    department = get_department_for_issue(issue_type)

    if department:
        return {
            "success": True,
            "department": department
        }

    return {
        "success": False,
        "department": None,
        "message": "No department mapping found for this issue."
    }


# ============================================================
# CREATE ASSIGNMENT DATA
# ============================================================
# This prepares assignment information.
# Database saving will be connected later without changing
# the existing database structure.
# ============================================================

def create_assignment(
    complaint_id,
    department_name,
    officer_id=None
):

    assignment = {

        "complaint_id": complaint_id,

        "department": department_name,

        "officer_id": officer_id,

        "status": "Assigned",

        "assigned_at": datetime.utcnow(),

        "resolved_at": None,

        "resolution_remark": None

    }

    return assignment


# ============================================================
# START WORK
# ============================================================

def start_work(assignment):

    if not assignment:
        return False

    assignment["status"] = "In Progress"

    return True


# ============================================================
# MARK COMPLAINT RESOLVED
# ============================================================

def resolve_complaint(
    assignment,
    resolution_remark
):

    if not assignment:
        return False

    if not resolution_remark:
        return False

    assignment["status"] = "Resolved"

    assignment["resolved_at"] = datetime.utcnow()

    assignment["resolution_remark"] = resolution_remark.strip()

    return True


# ============================================================
# CLOSE COMPLAINT
# ============================================================

def close_complaint(assignment):

    if not assignment:
        return False

    if assignment["status"] != "Resolved":
        return False

    assignment["status"] = "Closed"

    return True


# ============================================================
# CHECK WHETHER COMPLAINT IS COMPLETED
# ============================================================

def is_completed(status):

    return status in ["Resolved", "Closed"]


# ============================================================
# GET WORKFLOW INFORMATION
# ============================================================

def get_workflow_status(status):

    if status not in STATUS_FLOW:
        return {
            "status": status,
            "step": 0,
            "completed": False
        }

    step = STATUS_FLOW.index(status) + 1

    return {
        "status": status,
        "step": step,
        "total_steps": len(STATUS_FLOW),
        "completed": is_completed(status)
    }


# ============================================================
# COMPLETE WORKFLOW DEMO
# ============================================================
# This function is only for testing the workflow.
# It does NOT modify the database.
# ============================================================

def demo_workflow(
    complaint_id,
    issue_type,
    officer_id
):

    # ----------------------------------------
    # Step 1: Identify department
    # ----------------------------------------

    department_result = identify_department(issue_type)

    if not department_result["success"]:
        return {
            "success": False,
            "message": department_result["message"]
        }


    department = department_result["department"]


    # ----------------------------------------
    # Step 2: Assign complaint
    # ----------------------------------------

    assignment = create_assignment(
        complaint_id=complaint_id,
        department_name=department,
        officer_id=officer_id
    )


    # ----------------------------------------
    # Step 3: Start work
    # ----------------------------------------

    start_work(assignment)


    # ----------------------------------------
    # Step 4: Resolve
    # ----------------------------------------

    resolve_complaint(
        assignment,
        "Issue inspected and corrective action completed."
    )


    # ----------------------------------------
    # Return result
    # ----------------------------------------

    return {
        "success": True,
        "assignment": assignment
    }


# ============================================================
# EXAMPLE
# ============================================================
#
# result = demo_workflow(
#     complaint_id=101,
#     issue_type="Pothole",
#     officer_id=5
# )
#
# Result flow:
#
# Pothole
#    ↓
# Road & Public Works
#    ↓
# Officer #5
#    ↓
# In Progress
#    ↓
# Resolved
#
# ============================================================

