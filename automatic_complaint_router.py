
from models import db, Complaint, Department, User
from department_notification_store import add_notification


# =========================================================
# ISSUE → DEPARTMENT KEYWORDS
# =========================================================

KEYWORD_DEPARTMENT_MAP = {

    "Road & Public Works": [
        "pothole",
        "road damage",
        "damaged road",
        "broken road",
        "road repair",
        "footpath",
        "open manhole",
        "damaged divider"
    ],

    "Solid Waste Management": [
        "garbage",
        "garbage overflow",
        "waste",
        "waste disposal",
        "illegal dumping",
        "dumping",
        "garbage collection"
    ],

    "Water Supply": [
        "water leakage",
        "water leak",
        "water supply",
        "broken pipeline",
        "pipeline",
        "low water pressure",
        "water contamination"
    ],

    "Drainage & Sewerage": [
        "drainage",
        "drain blockage",
        "blocked drain",
        "sewage",
        "sewer",
        "waterlogging",
        "sewer leakage"
    ],

    "Electrical & Street Lighting": [
        "streetlight",
        "street light",
        "streetlight not working",
        "broken streetlight",
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


# =========================================================
# FIND DEPARTMENT
# =========================================================

def find_department(issue_type):

    if not issue_type:
        return None

    issue = issue_type.lower().strip()

    # First try exact department issue names
    for department_name, keywords in KEYWORD_DEPARTMENT_MAP.items():

        for keyword in keywords:

            if keyword in issue:
                return department_name

    return None


# =========================================================
# GET DEPARTMENT OBJECT
# =========================================================

def get_department(department_name):

    if not department_name:
        return None

    return Department.query.filter_by(
        name=department_name
    ).first()


# =========================================================
# FIND AVAILABLE OFFICER
# =========================================================

def choose_officer():

    officers = User.query.filter_by(
        role="officer"
    ).all()

    if not officers:
        return None

    best_officer = None
    lowest_workload = None

    for officer in officers:

        workload = Complaint.query.filter(
            Complaint.assigned_officer_id == officer.id,
            Complaint.status.in_([
                "Assigned",
                "In Progress"
            ])
        ).count()

        if (
            best_officer is None
            or workload < lowest_workload
        ):
            best_officer = officer
            lowest_workload = workload

    return best_officer


# =========================================================
# AUTOMATIC ROUTING
# =========================================================

def route_new_complaint(complaint):

    if complaint is None:
        return {
            "success": False,
            "message": "Complaint not found."
        }

    # -----------------------------------------------------
    # 1. FIND DEPARTMENT
    # -----------------------------------------------------

    department_name = find_department(
        complaint.issue_type
    )

    if department_name is None:

        return {
            "success": False,
            "message": (
                "Could not automatically identify "
                "the responsible department."
            )
        }

    department = get_department(
        department_name
    )

    if department is None:

        return {
            "success": False,
            "message": (
                f"Department '{department_name}' "
                "does not exist in database."
            )
        }

    # -----------------------------------------------------
    # 2. ASSIGN DEPARTMENT
    # -----------------------------------------------------

    complaint.department_id = department.id

    # -----------------------------------------------------
    # 3. FIND OFFICER
    # -----------------------------------------------------

    officer = choose_officer()

    if officer is not None:

        complaint.assigned_officer_id = officer.id
        complaint.status = "Assigned"

    else:

        complaint.status = "Pending"

    # -----------------------------------------------------
    # 4. SAVE
    # -----------------------------------------------------

    db.session.commit()

    # -----------------------------------------------------
    # 5. NOTIFICATION
    # -----------------------------------------------------

    add_notification(
        notification_type="assigned",
        title="New Complaint Assigned",
        message=(
            f"Complaint #{complaint.id} has been assigned "
            f"to {department.name}."
        ),
        complaint_id=complaint.id,
        department_id=department.id,
        officer_id=(
            officer.id
            if officer
            else None
        )
    )

    return {
        "success": True,
        "complaint_id": complaint.id,
        "department_id": department.id,
        "department_name": department.name,
        "officer_id": (
            officer.id
            if officer
            else None
        ),
        "officer_name": (
            officer.name
            if officer
            else None
        ),
        "status": complaint.status
    }
