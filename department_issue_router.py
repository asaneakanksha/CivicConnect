
"""
CivicConnect - Department Issue Router

Purpose:
    Automatically identify the correct municipal department
    based on the complaint issue type.

IMPORTANT:
    This is a NEW helper file.
    Existing CivicConnect files are not modified.
"""

from department_data import (
    MUNICIPAL_DEPARTMENTS,
    get_department_for_issue
)


# ============================================================
# ISSUE ROUTING
# ============================================================

def route_issue(issue_type):
    """
    Find the correct municipal department for an issue.

    Example:
        Pothole -> Road & Public Works
        Garbage Overflow -> Solid Waste Management
        Water Leakage -> Water Supply
    """

    if not issue_type:
        return {
            "success": False,
            "issue_type": "",
            "department": None,
            "message": "Issue type is required."
        }

    issue_type = issue_type.strip()

    department = get_department_for_issue(issue_type)

    if department:
        return {
            "success": True,
            "issue_type": issue_type,
            "department": department,
            "message": f"Issue routed to {department}."
        }

    return {
        "success": False,
        "issue_type": issue_type,
        "department": None,
        "message": "No department found for this issue."
    }


# ============================================================
# SHOW ALL ROUTING OPTIONS
# ============================================================

def get_all_issue_routes():
    """
    Returns every issue and its corresponding department.
    """

    routes = []

    for department_name, department_info in MUNICIPAL_DEPARTMENTS.items():

        issues = department_info.get("issues", [])

        for issue in issues:

            routes.append({
                "issue_type": issue,
                "department": department_name
            })

    return routes


# ============================================================
# FIND ISSUES FOR A DEPARTMENT
# ============================================================

def get_issues_for_department(department_name):
    """
    Returns all supported complaint types
    belonging to a particular department.
    """

    if not department_name:
        return []

    department = MUNICIPAL_DEPARTMENTS.get(department_name)

    if not department:
        return []

    return department.get("issues", [])


# ============================================================
# CHECK DEPARTMENT RESPONSIBILITY
# ============================================================

def is_department_responsible(department_name, issue_type):
    """
    Check whether a department is responsible
    for a particular issue.
    """

    if not department_name or not issue_type:
        return False

    department = MUNICIPAL_DEPARTMENTS.get(department_name)

    if not department:
        return False

    issues = department.get("issues", [])

    return any(
        issue.lower() == issue_type.strip().lower()
        for issue in issues
    )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    print("\n==========================================")
    print(" CIVICCONNECT ISSUE ROUTING TEST")
    print("==========================================\n")

    test_issues = [
        "Pothole",
        "Garbage Overflow",
        "Water Leakage",
        "Streetlight Not Working",
        "Drainage Blockage",
        "Illegal Construction",
        "Park Maintenance",
        "Mosquito Problem"
    ]

    for issue in test_issues:

        result = route_issue(issue)

        print(f"Issue      : {result['issue_type']}")
        print(f"Department : {result['department']}")
        print(f"Message    : {result['message']}")
        print("------------------------------------------")

    print("\nRouting test completed.")

