
# ============================================================
# CIVICCONNECT - MUNICIPAL DEPARTMENT DATA
# ============================================================
# This is a NEW file.
# Existing app.py / models.py / dashboards are NOT changed.
# ============================================================


MUNICIPAL_DEPARTMENTS = {

    "Road & Public Works": {
        "description": "Handles roads, potholes, footpaths and damaged public infrastructure.",

        "issues": [
            "Pothole",
            "Damaged Road",
            "Broken Footpath",
            "Road Repair",
            "Open Manhole",
            "Damaged Divider"
        ]
    },


    "Solid Waste Management": {
        "description": "Handles garbage collection, waste overflow and illegal dumping.",

        "issues": [
            "Garbage Overflow",
            "Garbage Collection",
            "Illegal Dumping",
            "Waste Disposal",
            "Public Waste"
        ]
    },


    "Water Supply": {
        "description": "Handles water supply problems, leakage and pipeline issues.",

        "issues": [
            "Water Leakage",
            "Water Supply",
            "Broken Pipeline",
            "Low Water Pressure",
            "Water Contamination"
        ]
    },


    "Drainage & Sewerage": {
        "description": "Handles drainage, sewage and waterlogging complaints.",

        "issues": [
            "Drainage Blockage",
            "Sewage Problem",
            "Waterlogging",
            "Blocked Drain",
            "Sewer Leakage"
        ]
    },


    "Electrical & Street Lighting": {
        "description": "Handles streetlights, public electrical infrastructure and lighting issues.",

        "issues": [
            "Streetlight Not Working",
            "Broken Streetlight",
            "Electrical Pole",
            "Electrical Wiring",
            "Public Lighting"
        ]
    },


    "Parks & Garden": {
        "description": "Handles public parks, gardens, trees and green spaces.",

        "issues": [
            "Park Maintenance",
            "Tree Issue",
            "Fallen Tree",
            "Garden Maintenance",
            "Green Area"
        ]
    },


    "Town Planning": {
        "description": "Handles illegal construction and town planning related complaints.",

        "issues": [
            "Illegal Construction",
            "Unauthorized Construction",
            "Building Violation",
            "Encroachment"
        ]
    },


    "Public Health": {
        "description": "Handles sanitation and public-health related civic complaints.",

        "issues": [
            "Public Sanitation",
            "Mosquito Problem",
            "Unhygienic Area",
            "Public Health Hazard"
        ]
    }

}


# ============================================================
# FIND DEPARTMENT FOR AN ISSUE
# ============================================================

def get_department_for_issue(issue_type):

    if not issue_type:
        return None

    issue_type = issue_type.strip().lower()


    for department, data in MUNICIPAL_DEPARTMENTS.items():

        for issue in data["issues"]:

            if issue.lower() == issue_type:
                return department


    return None


# ============================================================
# GET ALL DEPARTMENT NAMES
# ============================================================

def get_department_names():

    return list(MUNICIPAL_DEPARTMENTS.keys())


# ============================================================
# GET ISSUES FOR A DEPARTMENT
# ============================================================

def get_department_issues(department_name):

    department = MUNICIPAL_DEPARTMENTS.get(department_name)

    if department:

        return department["issues"]

    return []


# ============================================================
# CHECK WHETHER DEPARTMENT EXISTS
# ============================================================

def department_exists(department_name):

    return department_name in MUNICIPAL_DEPARTMENTS


# ============================================================
# EXAMPLE
# ============================================================
#
# issue = "Pothole"
#
# department = get_department_for_issue(issue)
#
# print(department)
#
# Output:
# Road & Public Works
#
# ============================================================

