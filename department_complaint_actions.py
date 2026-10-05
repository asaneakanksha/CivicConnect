
"""
CivicConnect - Department Complaint Actions

Purpose:
    Provides the business logic for municipal departments
    to process complaints.

Workflow:

    Assigned
        ↓
    In Progress
        ↓
    Resolved
        ↓
    Closed

IMPORTANT:
    This is a NEW helper file.
    Existing CivicConnect files are not modified.
"""

from datetime import datetime


# ============================================================
# VALID STATUS FLOW
# ============================================================

STATUS_FLOW = [
    "Pending",
    "Assigned",
    "In Progress",
    "Resolved",
    "Closed"
]


# ============================================================
# CHECK STATUS
# ============================================================

def is_valid_status(status):
    """
    Check whether a status is valid in CivicConnect.
    """

    return status in STATUS_FLOW


# ============================================================
# ACCEPT COMPLAINT
# ============================================================

def accept_complaint(complaint):
    """
    Department accepts an assigned complaint.

    Assigned -> In Progress
    """

    if complaint is None:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    if complaint.status != "Assigned":
        return {
            "success": False,
            "message": (
                "Only an Assigned complaint "
                "can be accepted."
            )
        }

    complaint.status = "In Progress"
    complaint.updated_at = datetime.utcnow()

    return {
        "success": True,
        "status": "In Progress",
        "message": (
            f"Complaint #{complaint.id} "
            "has been accepted by the department."
        )
    }


# ============================================================
# START WORK
# ============================================================

def start_work(complaint):
    """
    Start work on a complaint.

    This function also supports an Assigned complaint
    directly moving to In Progress.
    """

    if complaint is None:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    if complaint.status not in ["Assigned", "In Progress"]:
        return {
            "success": False,
            "message": (
                "Complaint must be Assigned "
                "before work can start."
            )
        }

    complaint.status = "In Progress"
    complaint.updated_at = datetime.utcnow()

    return {
        "success": True,
        "status": "In Progress",
        "message": (
            f"Work has started on complaint "
            f"#{complaint.id}."
        )
    }


# ============================================================
# RESOLVE COMPLAINT
# ============================================================

def resolve_complaint(complaint, resolution_remark):
    """
    Mark a complaint as Resolved.

    A resolution remark is mandatory.
    """

    if complaint is None:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    if complaint.status != "In Progress":
        return {
            "success": False,
            "message": (
                "Complaint must be In Progress "
                "before it can be resolved."
            )
        }

    if not resolution_remark:
        return {
            "success": False,
            "message": (
                "Resolution remark is required."
            )
        }

    resolution_remark = resolution_remark.strip()

    if not resolution_remark:
        return {
            "success": False,
            "message": (
                "Resolution remark cannot be empty."
            )
        }

    complaint.status = "Resolved"
    complaint.updated_at = datetime.utcnow()

    return {
        "success": True,
        "status": "Resolved",
        "resolution_remark": resolution_remark,
        "resolved_at": datetime.utcnow(),
        "message": (
            f"Complaint #{complaint.id} "
            "has been marked as Resolved."
        )
    }


# ============================================================
# CLOSE COMPLAINT
# ============================================================

def close_complaint(complaint):
    """
    Close a complaint after resolution.

    Resolved -> Closed
    """

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
                "can be Closed."
            )
        }

    complaint.status = "Closed"
    complaint.updated_at = datetime.utcnow()

    return {
        "success": True,
        "status": "Closed",
        "closed_at": datetime.utcnow(),
        "message": (
            f"Complaint #{complaint.id} "
            "has been Closed."
        )
    }


# ============================================================
# REOPEN COMPLAINT
# ============================================================

def reopen_complaint(complaint, reason):
    """
    Reopen a resolved/closed complaint when additional
    work is required.

    Closed/Resolved -> In Progress
    """

    if complaint is None:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    if complaint.status not in ["Resolved", "Closed"]:
        return {
            "success": False,
            "message": (
                "Only a Resolved or Closed complaint "
                "can be reopened."
            )
        }

    if not reason or not reason.strip():
        return {
            "success": False,
            "message": (
                "Reopen reason is required."
            )
        }

    complaint.status = "In Progress"
    complaint.updated_at = datetime.utcnow()

    return {
        "success": True,
        "status": "In Progress",
        "reason": reason.strip(),
        "reopened_at": datetime.utcnow(),
        "message": (
            f"Complaint #{complaint.id} "
            "has been reopened."
        )
    }


# ============================================================
# GET NEXT ACTION
# ============================================================

def get_next_action(status):
    """
    Tell the department what action is available
    for the current complaint status.
    """

    actions = {
        "Pending": "Assign Department",
        "Assigned": "Accept Complaint",
        "In Progress": "Resolve Complaint",
        "Resolved": "Close Complaint",
        "Closed": "No Action"
    }

    return actions.get(
        status,
        "Unknown Status"
    )


# ============================================================
# GET STATUS INFORMATION
# ============================================================

def get_status_information(status):
    """
    Return useful information about the complaint status.
    """

    information = {
        "Pending": {
            "label": "Pending",
            "next_action": "Assign Department",
            "completed": False
        },

        "Assigned": {
            "label": "Assigned",
            "next_action": "Accept Complaint",
            "completed": False
        },

        "In Progress": {
            "label": "In Progress",
            "next_action": "Resolve Complaint",
            "completed": False
        },

        "Resolved": {
            "label": "Resolved",
            "next_action": "Close Complaint",
            "completed": True
        },

        "Closed": {
            "label": "Closed",
            "next_action": "No Action",
            "completed": True
        }
    }

    return information.get(
        status,
        {
            "label": "Unknown",
            "next_action": "No Action",
            "completed": False
        }
    )


# ============================================================
# COMPLETE COMPLAINT CHECK
# ============================================================

def is_completed(complaint):
    """
    Check whether a complaint has been completed.
    """

    if complaint is None:
        return False

    return complaint.status in [
        "Resolved",
        "Closed"
    ]


# ============================================================
# TEST WITH A FAKE COMPLAINT
# ============================================================

class TestComplaint:
    """
    Small test object so this file can be tested
    without changing the real database.
    """

    def __init__(self, complaint_id):
        self.id = complaint_id
        self.status = "Assigned"
        self.updated_at = None


# ============================================================
# RUN TEST
# ============================================================

if __name__ == "__main__":

    print("\n==========================================")
    print(" CIVICCONNECT COMPLAINT ACTION TEST")
    print("==========================================\n")

    complaint = TestComplaint(101)

    print("Initial Status :", complaint.status)

    # Accept
    result = accept_complaint(complaint)

    print("\n1. ACCEPT")
    print("Status  :", result["status"])
    print("Message :", result["message"])

    # Start work
    result = start_work(complaint)

    print("\n2. START WORK")
    print("Status  :", result["status"])
    print("Message :", result["message"])

    # Resolve
    result = resolve_complaint(
        complaint,
        "Pothole repaired successfully by "
        "Road & Public Works department."
    )

    print("\n3. RESOLVE")
    print("Status  :", result["status"])
    print("Message :", result["message"])

    # Close
    result = close_complaint(complaint)

    print("\n4. CLOSE")
    print("Status  :", result["status"])
    print("Message :", result["message"])

    # Final check
    print("\n==========================================")
    print(" FINAL STATUS")
    print("==========================================")

    print("Complaint ID :", complaint.id)
    print("Status       :", complaint.status)
    print("Completed    :", is_completed(complaint))
    print("Next Action  :", get_next_action(complaint.status))

    print("\n==========================================")
    print(" TEST COMPLETED")
    print("==========================================\n")
