
from flask import request, redirect, url_for, flash, render_template_string
from flask_login import login_required, current_user
from app import app, socketio
from models import db, Complaint, Department, User, Remark
from department_service import (
    start_work,
    resolve_complaint,
    close_complaint
)
from department_notification_store import add_notification


# =========================================================
# DEPARTMENT PORTAL
# =========================================================

@app.route("/department/portal")
@login_required
def department_portal():

    # Only officers and admins can access department portal
    if current_user.role not in ["officer", "admin"]:
        flash("Only department staff can access this portal.", "danger")
        return redirect(url_for("dashboard"))

    departments = Department.query.order_by(Department.name).all()

    # -----------------------------------------------------
    # OFFICER VIEW
    # -----------------------------------------------------
    if current_user.role == "officer":

        complaints = (
            Complaint.query
            .filter_by(assigned_officer_id=current_user.id)
            .order_by(Complaint.created_at.desc())
            .all()
        )

        selected_department = None

    # -----------------------------------------------------
    # ADMIN VIEW
    # -----------------------------------------------------
    else:

        department_id = request.args.get("department_id", type=int)

        selected_department = None

        if department_id:
            selected_department = Department.query.get(department_id)

            complaints = (
                Complaint.query
                .filter_by(department_id=department_id)
                .order_by(Complaint.created_at.desc())
                .all()
            )
        else:
            complaints = []

    return render_template_string(
        PORTAL_HTML,
        complaints=complaints,
        departments=departments,
        selected_department=selected_department,
        current_user=current_user
    )


# =========================================================
# START WORK
# =========================================================

@app.route(
    "/department/complaint/<int:complaint_id>/start",
    methods=["POST"]
)
@login_required
def department_start_work(complaint_id):

    if current_user.role not in ["officer", "admin"]:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    complaint = Complaint.query.get_or_404(complaint_id)

    # Officer can work only on their assigned complaint
    if current_user.role == "officer":

        if complaint.assigned_officer_id != current_user.id:
            flash("This complaint is not assigned to you.", "danger")
            return redirect(url_for("department_portal"))

        officer_id = current_user.id

    else:
        officer_id = complaint.assigned_officer_id

        if officer_id is None:
            flash("Assign an officer before starting the work.", "warning")
            return redirect(url_for(
                "department_portal",
                department_id=complaint.department_id
            ))

    try:

        start_work(
            complaint_id=complaint_id,
            officer_id=officer_id
        )

        add_notification(
            notification_type="work_started",
            title="Complaint Work Started",
            message=f"Work has started on complaint #{complaint.id}.",
            complaint_id=complaint.id,
            department_id=complaint.department_id,
            officer_id=complaint.assigned_officer_id
        )

        socketio.emit(
            "complaint_updated",
            {
                "complaint_id": complaint.id,
                "status": "In Progress"
            }
        )

        flash(
            f"Complaint #{complaint.id} is now In Progress.",
            "success"
        )

    except Exception as e:

        flash(str(e), "danger")

    if current_user.role == "admin":
        return redirect(url_for(
            "department_portal",
            department_id=complaint.department_id
        ))

    return redirect(url_for("department_portal"))


# =========================================================
# RESOLVE COMPLAINT
# =========================================================

@app.route(
    "/department/complaint/<int:complaint_id>/resolve",
    methods=["POST"]
)
@login_required
def department_resolve_complaint(complaint_id):

    if current_user.role not in ["officer", "admin"]:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    complaint = Complaint.query.get_or_404(complaint_id)

    # Officer security check
    if current_user.role == "officer":

        if complaint.assigned_officer_id != current_user.id:
            flash("This complaint is not assigned to you.", "danger")
            return redirect(url_for("department_portal"))

        officer_id = current_user.id

    else:
        officer_id = complaint.assigned_officer_id

        if officer_id is None:
            flash("No officer is assigned to this complaint.", "warning")
            return redirect(url_for(
                "department_portal",
                department_id=complaint.department_id
            ))

    resolution_text = request.form.get(
        "resolution",
        ""
    ).strip()

    if not resolution_text:

        flash(
            "Please enter resolution details.",
            "warning"
        )

        return redirect(request.referrer or url_for(
            "department_portal"
        ))

    try:

        resolve_complaint(
            complaint_id=complaint_id,
            officer_id=officer_id,
            resolution_text=resolution_text
        )

        add_notification(
            notification_type="resolved",
            title="Complaint Resolved",
            message=f"Complaint #{complaint.id} has been resolved.",
            complaint_id=complaint.id,
            department_id=complaint.department_id,
            officer_id=complaint.assigned_officer_id
        )

        socketio.emit(
            "complaint_updated",
            {
                "complaint_id": complaint.id,
                "status": "Resolved"
            }
        )

        flash(
            f"Complaint #{complaint.id} has been resolved.",
            "success"
        )

    except Exception as e:

        flash(str(e), "danger")

    if current_user.role == "admin":
        return redirect(url_for(
            "department_portal",
            department_id=complaint.department_id
        ))

    return redirect(url_for("department_portal"))


# =========================================================
# CLOSE COMPLAINT
# =========================================================

@app.route(
    "/department/complaint/<int:complaint_id>/close",
    methods=["POST"]
)
@login_required
def department_close_complaint(complaint_id):

    if current_user.role not in ["officer", "admin"]:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    complaint = Complaint.query.get_or_404(complaint_id)

    # Officer security check
    if current_user.role == "officer":

        if complaint.assigned_officer_id != current_user.id:
            flash("This complaint is not assigned to you.", "danger")
            return redirect(url_for("department_portal"))

    try:

        close_complaint(
            complaint_id=complaint_id
        )

        add_notification(
            notification_type="closed",
            title="Complaint Closed",
            message=f"Complaint #{complaint.id} has been closed.",
            complaint_id=complaint.id,
            department_id=complaint.department_id,
            officer_id=complaint.assigned_officer_id
        )

        socketio.emit(
            "complaint_updated",
            {
                "complaint_id": complaint.id,
                "status": "Closed"
            }
        )

        flash(
            f"Complaint #{complaint.id} has been closed.",
            "success"
        )

    except Exception as e:

        flash(str(e), "danger")

    if current_user.role == "admin":
        return redirect(url_for(
            "department_portal",
            department_id=complaint.department_id
        ))

    return redirect(url_for("department_portal"))


# =========================================================
# PORTAL HTML
# =========================================================

PORTAL_HTML = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Department Portal - CivicConnect</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f5f3ff;
            color: #222;
        }

        .header {
            background: linear-gradient(
                135deg,
                #4b1d95,
                #7c3aed
            );

            color: white;
            padding: 20px 30px;

            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            margin: 0;
            font-size: 25px;
        }

        .header p {
            margin: 5px 0 0;
            opacity: 0.9;
        }

        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 22px;
            margin-bottom: 20px;
            box-shadow: 0 5px 18px rgba(0,0,0,0.08);
        }

        .stats {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(180px, 1fr));

            gap: 15px;
            margin-bottom: 25px;
        }

        .stat {
            background: white;
            padding: 20px;
            border-radius: 14px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.07);
        }

        .stat h3 {
            margin: 0;
            color: #6d28d9;
            font-size: 28px;
        }

        .stat p {
            margin: 7px 0 0;
            color: #666;
        }

        .complaint {
            border: 1px solid #e5e7eb;
            border-radius: 13px;
            padding: 18px;
            margin-bottom: 15px;
        }

        .complaint-header {
            display: flex;
            justify-content: space-between;
            gap: 15px;
            flex-wrap: wrap;
        }

        .complaint h3 {
            margin: 0;
            color: #4b1d95;
        }

        .badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
            background: #ede9fe;
            color: #5b21b6;
        }

        .info {
            margin-top: 12px;
            color: #555;
            line-height: 1.6;
        }

        textarea {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            border: 1px solid #ddd;
            border-radius: 10px;
            resize: vertical;
        }

        button {
            border: none;
            border-radius: 9px;
            padding: 10px 16px;
            cursor: pointer;
            margin-top: 10px;
            font-weight: bold;
        }

        .start {
            background: #f59e0b;
            color: white;
        }

        .resolve {
            background: #16a34a;
            color: white;
        }

        .close {
            background: #2563eb;
            color: white;
        }

        select {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #ddd;
            margin-top: 10px;
        }

        .flash {
            padding: 13px;
            border-radius: 10px;
            margin-bottom: 15px;
            background: #ede9fe;
            color: #4b1d95;
        }

        .empty {
            text-align: center;
            padding: 40px;
            color: #777;
        }

        @media(max-width:600px) {

            .header {
                padding: 18px;
            }

            .container {
                padding: 0 12px;
            }

        }

    </style>

</head>


<body>


<div class="header">

    <div>

        <h1>CivicConnect Department Portal</h1>

        <p>
            Logged in as:
            {{ current_user.name }}
            ({{ current_user.role }})
        </p>

    </div>

</div>


<div class="container">


    {% with messages = get_flashed_messages() %}

        {% for message in messages %}

            <div class="flash">
                {{ message }}
            </div>

        {% endfor %}

    {% endwith %}


    {% if current_user.role == "admin" %}

        <div class="card">

            <h2>Select Municipal Department</h2>

            <form method="GET"
                  action="{{ url_for('department_portal') }}">

                <select name="department_id"
                        onchange="this.form.submit()">

                    <option value="">
                        Select Department
                    </option>

                    {% for department in departments %}

                        <option value="{{ department.id }}"
                            {% if selected_department
                               and selected_department.id == department.id %}
                               selected
                            {% endif %}>

                            {{ department.name }}

                        </option>

                    {% endfor %}

                </select>

            </form>

        </div>

    {% endif %}


    {% if selected_department %}

        <div class="card">

            <h2>
                {{ selected_department.name }}
            </h2>

            <p>
                Department complaint management
            </p>

        </div>

    {% endif %}


    <div class="stats">

        <div class="stat">

            <h3>
                {{ complaints|length }}
            </h3>

            <p>Total Complaints</p>

        </div>


        <div class="stat">

            <h3>
                {{ complaints|selectattr("status", "equalto", "Pending")|list|length }}
            </h3>

            <p>Pending</p>

        </div>


        <div class="stat">

            <h3>
                {{ complaints|selectattr("status", "equalto", "In Progress")|list|length }}
            </h3>

            <p>In Progress</p>

        </div>


        <div class="stat">

            <h3>
                {{ complaints|selectattr("status", "equalto", "Resolved")|list|length }}
            </h3>

            <p>Resolved</p>

        </div>


        <div class="stat">

            <h3>
                {{ complaints|selectattr("status", "equalto", "Closed")|list|length }}
            </h3>

            <p>Closed</p>

        </div>

    </div>


    <div class="card">

        <h2>Department Complaints</h2>


        {% if complaints %}


            {% for complaint in complaints %}

                <div class="complaint">

                    <div class="complaint-header">

                        <h3>
                            #{{ complaint.id }}
                            - {{ complaint.title }}
                        </h3>

                        <span class="badge">
                            {{ complaint.status }}
                        </span>

                    </div>


                    <div class="info">

                        <strong>Issue:</strong>
                        {{ complaint.issue_type }}
                        <br>

                        <strong>Location:</strong>
                        {{ complaint.location }}
                        <br>

                        <strong>Priority:</strong>
                        {{ complaint.priority }}
                        <br>

                        <strong>Description:</strong>
                        {{ complaint.description }}

                    </div>


                    {% if complaint.status == "Assigned" %}

                        <form method="POST"
                              action="{{ url_for(
                                  'department_start_work',
                                  complaint_id=complaint.id
                              ) }}">

                            <button class="start">
                                Start Work
                            </button>

                        </form>

                    {% endif %}


                    {% if complaint.status == "In Progress" %}

                        <form method="POST"
                              action="{{ url_for(
                                  'department_resolve_complaint',
                                  complaint_id=complaint.id
                              ) }}">

                            <textarea
                                name="resolution"
                                rows="3"
                                placeholder="Enter resolution details..."
                                required></textarea>

                            <button class="resolve">
                                Mark as Resolved
                            </button>

                        </form>

                    {% endif %}


                    {% if complaint.status == "Resolved" %}

                        <form method="POST"
                              action="{{ url_for(
                                  'department_close_complaint',
                                  complaint_id=complaint.id
                              ) }}">

                            <button class="close">
                                Close Complaint
                            </button>

                        </form>

                    {% endif %}


                </div>

            {% endfor %}


        {% else %}

            <div class="empty">

                <h3>No complaints found</h3>

                <p>
                    Complaints assigned to this department
                    or officer will appear here.
                </p>

            </div>

        {% endif %}


    </div>


</div>


</body>

</html>
"""


# =========================================================
# RUN SEPARATELY
# =========================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print(" CivicConnect Department Portal")
    print("==========================================")
    print()
    print("Open:")
    print("http://127.0.0.1:5000/department/portal")
    print()

    socketio.run(
        app,
        debug=False,
        use_reloader=False
    )