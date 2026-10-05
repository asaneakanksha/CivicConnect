from flask import request, redirect, url_for, session
from werkzeug.security import check_password_hash

from app import app
from models import db, User, Complaint
from department_service import start_work, resolve_complaint


# ============================================================
# OFFICER LOGIN
# ============================================================

@app.route("/officer/login", methods=["GET", "POST"])
def officer_login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        officer = User.query.filter_by(
            email=email,
            role="officer"
        ).first()

        if not officer:
            return """
            <h3>Invalid officer account.</h3>
            <a href="/officer/login">Try Again</a>
            """

        if not officer.check_password(password):
            return """
            <h3>Invalid password.</h3>
            <a href="/officer/login">Try Again</a>
            """

        session["officer_id"] = officer.id

        return redirect(url_for("officer_portal"))

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CivicConnect Officer Login</title>

        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #4f46e5, #7c3aed);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .login-box {
                width: 380px;
                background: white;
                padding: 35px;
                border-radius: 18px;
                box-shadow: 0 15px 40px rgba(0,0,0,0.25);
            }

            h1 {
                margin-bottom: 5px;
                color: #312e81;
            }

            p {
                color: #666;
                margin-bottom: 25px;
            }

            label {
                display: block;
                margin-top: 15px;
                margin-bottom: 6px;
                font-weight: bold;
            }

            input {
                width: 100%;
                padding: 12px;
                box-sizing: border-box;
                border: 1px solid #ddd;
                border-radius: 8px;
            }

            button {
                width: 100%;
                margin-top: 25px;
                padding: 13px;
                border: none;
                border-radius: 8px;
                background: #4f46e5;
                color: white;
                font-size: 16px;
                cursor: pointer;
            }

            button:hover {
                background: #3730a3;
            }
        </style>
    </head>

    <body>

        <div class="login-box">

            <h1>🏛️ CivicConnect</h1>
            <p>Officer Login</p>

            <form method="POST">

                <label>Email</label>
                <input
                    type="email"
                    name="email"
                    placeholder="Officer email"
                    required
                >

                <label>Password</label>
                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    required
                >

                <button type="submit">
                    Login as Officer
                </button>

            </form>

        </div>

    </body>
    </html>
    """


# ============================================================
# OFFICER PORTAL
# ============================================================

@app.route("/officer/portal")
def officer_portal():

    officer_id = session.get("officer_id")

    if not officer_id:
        return redirect(url_for("officer_login"))

    officer = User.query.filter_by(
        id=officer_id,
        role="officer"
    ).first()

    if not officer:
        session.pop("officer_id", None)
        return redirect(url_for("officer_login"))

    complaints = Complaint.query.filter_by(
        assigned_officer_id=officer.id
    ).order_by(
        Complaint.created_at.desc()
    ).all()

    pending = [
        c for c in complaints
        if c.status == "Assigned"
    ]

    in_progress = [
        c for c in complaints
        if c.status == "In Progress"
    ]

    resolved = [
        c for c in complaints
        if c.status == "Resolved"
    ]

    rows = ""

    for complaint in complaints:

        department_name = (
            complaint.department.name
            if complaint.department
            else "Not Assigned"
        )

        action = ""

        if complaint.status == "Assigned":

            action = f"""
            <form method="POST"
                  action="/officer/complaint/{complaint.id}/start">

                <button class="start-btn">
                    Accept & Start Work
                </button>

            </form>
            """

        elif complaint.status == "In Progress":

            action = f"""
            <form method="POST"
                  action="/officer/complaint/{complaint.id}/resolve">

                <textarea
                    name="resolution"
                    placeholder="Enter resolution details..."
                    required
                ></textarea>

                <button class="resolve-btn">
                    Mark Resolved
                </button>

            </form>
            """

        elif complaint.status == "Resolved":

            action = """
            <span class="resolved">
                ✓ Resolved
            </span>
            """

        elif complaint.status == "Closed":

            action = """
            <span class="closed">
                ✓ Closed
            </span>
            """

        else:

            action = f"""
            <span class="pending">
                {complaint.status}
            </span>
            """

        rows += f"""

        <div class="complaint">

            <div class="top">

                <div>
                    <h2>Complaint #{complaint.id}</h2>

                    <span class="issue">
                        {complaint.issue_type}
                    </span>
                </div>

                <span class="status">
                    {complaint.status}
                </span>

            </div>

            <p>
                <strong>Title:</strong>
                {complaint.title}
            </p>

            <p>
                <strong>Description:</strong>
                {complaint.description}
            </p>

            <p>
                <strong>Location:</strong>
                📍 {complaint.location}
            </p>

            <p>
                <strong>Department:</strong>
                {department_name}
            </p>

            <div class="action">
                {action}
            </div>

        </div>

        """

    if not rows:
        rows = """
        <div class="empty">
            <h2>No complaints assigned</h2>
            <p>
                New complaints assigned to you will appear here.
            </p>
        </div>
        """

    return f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>Officer Dashboard - CivicConnect</title>

        <style>

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f4f6fb;
                color: #222;
            }}

            .navbar {{
                background: linear-gradient(
                    135deg,
                    #312e81,
                    #4f46e5
                );

                color: white;
                padding: 18px 35px;

                display: flex;
                justify-content: space-between;
                align-items: center;
            }}

            .brand {{
                font-size: 23px;
                font-weight: bold;
            }}

            .officer {{
                text-align: right;
            }}

            .logout {{
                display: inline-block;
                margin-top: 6px;
                color: white;
                text-decoration: none;
                background: rgba(255,255,255,0.18);
                padding: 7px 12px;
                border-radius: 7px;
            }}

            .container {{
                max-width: 1200px;
                margin: 30px auto;
                padding: 0 20px;
            }}

            .welcome {{
                margin-bottom: 25px;
            }}

            .welcome h1 {{
                margin-bottom: 5px;
                color: #312e81;
            }}

            .cards {{
                display: grid;
                grid-template-columns:
                    repeat(4, 1fr);

                gap: 18px;
                margin-bottom: 30px;
            }}

            .card {{
                background: white;
                padding: 22px;
                border-radius: 15px;
                box-shadow:
                    0 5px 18px rgba(0,0,0,0.08);
            }}

            .card h3 {{
                margin: 0;
                color: #666;
                font-size: 14px;
            }}

            .number {{
                font-size: 32px;
                font-weight: bold;
                color: #312e81;
                margin-top: 8px;
            }}

            .complaint {{
                background: white;
                padding: 25px;
                margin-bottom: 20px;
                border-radius: 15px;

                box-shadow:
                    0 5px 18px rgba(0,0,0,0.08);
            }}

            .top {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
            }}

            .top h2 {{
                margin-top: 0;
            }}

            .issue {{
                display: inline-block;
                background: #ede9fe;
                color: #5b21b6;
                padding: 6px 10px;
                border-radius: 20px;
                font-size: 13px;
            }}

            .status {{
                background: #fef3c7;
                color: #92400e;
                padding: 7px 12px;
                border-radius: 20px;
                font-weight: bold;
            }}

            .action {{
                margin-top: 20px;
            }}

            button {{
                border: none;
                padding: 11px 18px;
                border-radius: 8px;
                color: white;
                cursor: pointer;
                font-weight: bold;
            }}

            .start-btn {{
                background: #2563eb;
            }}

            .resolve-btn {{
                background: #16a34a;
                margin-top: 10px;
            }}

            textarea {{
                width: 100%;
                min-height: 90px;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                resize: vertical;
            }}

            .resolved {{
                color: #15803d;
                font-weight: bold;
            }}

            .closed {{
                color: #475569;
                font-weight: bold;
            }}

            .pending {{
                color: #b45309;
                font-weight: bold;
            }}

            .empty {{
                background: white;
                text-align: center;
                padding: 60px 20px;
                border-radius: 15px;
            }}

            @media(max-width: 800px) {{
                .cards {{
                    grid-template-columns: repeat(2, 1fr);
                }}
            }}

        </style>

    </head>

    <body>

        <div class="navbar">

            <div class="brand">
                🏛️ CivicConnect
            </div>

            <div class="officer">

                👮 {officer.name}

                <br>

                <a
                    class="logout"
                    href="/officer/logout"
                >
                    Logout
                </a>

            </div>

        </div>


        <div class="container">

            <div class="welcome">

                <h1>
                    Officer Dashboard
                </h1>

                <p>
                    Manage complaints assigned to you.
                </p>

            </div>


            <div class="cards">

                <div class="card">

                    <h3>Total Assigned</h3>

                    <div class="number">
                        {len(complaints)}
                    </div>

                </div>


                <div class="card">

                    <h3>Assigned</h3>

                    <div class="number">
                        {len(pending)}
                    </div>

                </div>


                <div class="card">

                    <h3>In Progress</h3>

                    <div class="number">
                        {len(in_progress)}
                    </div>

                </div>


                <div class="card">

                    <h3>Resolved</h3>

                    <div class="number">
                        {len(resolved)}
                    </div>

                </div>

            </div>


            <h2>
                My Complaints
            </h2>

            {rows}

        </div>

    </body>

    </html>

    """


# ============================================================
# START WORK
# ============================================================

@app.route(
    "/officer/complaint/<int:complaint_id>/start",
    methods=["POST"]
)
def officer_start_complaint(complaint_id):

    officer_id = session.get("officer_id")

    if not officer_id:
        return redirect(url_for("officer_login"))

    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.assigned_officer_id != officer_id:
        return "You are not assigned to this complaint.", 403

    result = start_work(
        complaint_id,
        officer_id
    )

    if not result.get("success"):
        return result.get("message", "Unable to start complaint.")

    return redirect(url_for("officer_portal"))


# ============================================================
# RESOLVE COMPLAINT
# ============================================================

@app.route(
    "/officer/complaint/<int:complaint_id>/resolve",
    methods=["POST"]
)
def officer_resolve_complaint(complaint_id):

    officer_id = session.get("officer_id")

    if not officer_id:
        return redirect(url_for("officer_login"))

    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.assigned_officer_id != officer_id:
        return "You are not assigned to this complaint.", 403

    resolution = request.form.get(
        "resolution",
        ""
    ).strip()

    if not resolution:
        return "Resolution details are required."

    result = resolve_complaint(
        complaint_id,
        officer_id,
        resolution
    )

    if not result.get("success"):
        return result.get("message", "Unable to resolve complaint.")

    return redirect(url_for("officer_portal"))


# ============================================================
# OFFICER LOGOUT
# ============================================================

@app.route("/officer/logout")
def officer_logout():

    session.pop("officer_id", None)

    return redirect(url_for("officer_login"))


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print()
    print("========================================")
    print(" CivicConnect Officer Portal")
    print("========================================")
    print()
    print("Officer Login:")
    print("http://127.0.0.1:5001/officer/login")
    print()

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False,
        use_reloader=False
    )
