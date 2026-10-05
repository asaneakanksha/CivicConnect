from flask import redirect, url_for
from flask_login import login_required, current_user

from app import app
from models import Complaint, Remark


@app.route("/citizen/status")
@login_required
def citizen_status():

    complaints = Complaint.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Complaint.created_at.desc()
    ).all()

    complaint_cards = ""

    for complaint in complaints:

        department_name = "Not Assigned"

        if complaint.department:
            department_name = complaint.department.name

        officer_name = "Not Assigned"

        if complaint.assigned_officer:
            officer_name = complaint.assigned_officer.name

        remarks = Remark.query.filter_by(
            complaint_id=complaint.id
        ).order_by(
            Remark.created_at.desc()
        ).all()

        remark_html = ""

        for remark in remarks:

            remark_officer = "Officer"

            if remark.officer:
                remark_officer = remark.officer.name

            remark_html += f"""
            <div class="remark">

                <strong>{remark_officer}</strong>

                <p>
                    {remark.remark}
                </p>

                <small>
                    {remark.created_at}
                </small>

            </div>
            """

        if not remark_html:

            remark_html = """
            <p class="no-remark">
                No update has been added yet.
            </p>
            """

        status_class = complaint.status.lower().replace(
            " ",
            "-"
        )

        complaint_cards += f"""

        <div class="complaint-card">

            <div class="header">

                <div>

                    <h2>
                        Complaint #{complaint.id}
                    </h2>

                    <span class="issue">
                        {complaint.issue_type}
                    </span>

                </div>

                <span class="status {status_class}">
                    {complaint.status}
                </span>

            </div>


            <div class="details">

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

                <p>
                    <strong>Assigned Officer:</strong>
                    {officer_name}
                </p>

            </div>


            <div class="timeline">

                <h3>
                    Complaint Progress
                </h3>

                <div class="timeline-item">

                    <span class="dot"></span>

                    <div>
                        <strong>
                            Complaint Submitted
                        </strong>

                        <p>
                            Your complaint was successfully submitted.
                        </p>
                    </div>

                </div>


                <div class="timeline-item">

                    <span class="dot"></span>

                    <div>
                        <strong>
                            Department Assignment
                        </strong>

                        <p>
                            {department_name}
                        </p>
                    </div>

                </div>


                <div class="timeline-item">

                    <span class="dot"></span>

                    <div>
                        <strong>
                            Officer Assignment
                        </strong>

                        <p>
                            {officer_name}
                        </p>
                    </div>

                </div>


                <div class="timeline-item">

                    <span class="dot"></span>

                    <div>
                        <strong>
                            Current Status
                        </strong>

                        <p>
                            {complaint.status}
                        </p>
                    </div>

                </div>

            </div>


            <div class="updates">

                <h3>
                    Officer Updates
                </h3>

                {remark_html}

            </div>

        </div>

        """


    if not complaint_cards:

        complaint_cards = """

        <div class="empty">

            <h2>
                No Complaints Found
            </h2>

            <p>
                You have not submitted any complaints yet.
            </p>

        </div>

        """


    return f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>
            My Complaints - CivicConnect
        </title>


        <style>

            * {{
                box-sizing: border-box;
            }}


            body {{

                margin: 0;

                font-family:
                    Arial,
                    sans-serif;

                background:
                    #f4f6fb;

                color:
                    #1f2937;

            }}


            .navbar {{

                background:
                    linear-gradient(
                        135deg,
                        #312e81,
                        #4f46e5
                    );

                color:
                    white;

                padding:
                    18px 35px;

                display:
                    flex;

                justify-content:
                    space-between;

                align-items:
                    center;

            }}


            .brand {{

                font-size:
                    23px;

                font-weight:
                    bold;

            }}


            .user-info {{

                text-align:
                    right;

            }}


            .logout {{

                display:
                    inline-block;

                margin-top:
                    6px;

                color:
                    white;

                text-decoration:
                    none;

                background:
                    rgba(
                        255,
                        255,
                        255,
                        0.18
                    );

                padding:
                    7px 12px;

                border-radius:
                    7px;

            }}


            .container {{

                max-width:
                    1100px;

                margin:
                    30px auto;

                padding:
                    0 20px;

            }}


            .welcome h1 {{

                color:
                    #312e81;

                margin-bottom:
                    5px;

            }}


            .welcome p {{

                color:
                    #64748b;

                margin-bottom:
                    30px;

            }}


            .complaint-card {{

                background:
                    white;

                padding:
                    28px;

                margin-bottom:
                    25px;

                border-radius:
                    16px;

                box-shadow:
                    0 5px 20px
                    rgba(
                        0,
                        0,
                        0,
                        0.08
                    );

            }}


            .header {{

                display:
                    flex;

                justify-content:
                    space-between;

                align-items:
                    flex-start;

                gap:
                    20px;

            }}


            .header h2 {{

                margin-top:
                    0;

                margin-bottom:
                    8px;

                color:
                    #312e81;

            }}


            .issue {{

                display:
                    inline-block;

                background:
                    #ede9fe;

                color:
                    #5b21b6;

                padding:
                    6px 11px;

                border-radius:
                    20px;

                font-size:
                    13px;

            }}


            .status {{

                padding:
                    8px 14px;

                border-radius:
                    20px;

                font-weight:
                    bold;

                white-space:
                    nowrap;

            }}


            .pending {{

                background:
                    #fef3c7;

                color:
                    #92400e;

            }}


            .assigned {{

                background:
                    #dbeafe;

                color:
                    #1d4ed8;

            }}


            .in-progress {{

                background:
                    #e0e7ff;

                color:
                    #4338ca;

            }}


            .resolved {{

                background:
                    #dcfce7;

                color:
                    #15803d;

            }}


            .closed {{

                background:
                    #e2e8f0;

                color:
                    #475569;

            }}


            .details {{

                margin-top:
                    20px;

                padding:
                    18px;

                background:
                    #f8fafc;

                border-radius:
                    10px;

            }}


            .details p {{

                margin:
                    9px 0;

            }}


            .timeline {{

                margin-top:
                    25px;

                padding:
                    20px;

                border-left:
                    3px solid #4f46e5;

            }}


            .timeline h3,
            .updates h3 {{

                color:
                    #312e81;

                margin-top:
                    0;

            }}


            .timeline-item {{

                display:
                    flex;

                gap:
                    14px;

                margin-bottom:
                    18px;

            }}


            .dot {{

                min-width:
                    12px;

                height:
                    12px;

                margin-top:
                    5px;

                border-radius:
                    50%;

                background:
                    #4f46e5;

            }}


            .timeline-item p {{

                margin:
                    5px 0 0;

                color:
                    #64748b;

            }}


            .updates {{

                margin-top:
                    25px;

            }}


            .remark {{

                background:
                    #f8fafc;

                border:
                    1px solid #e2e8f0;

                padding:
                    15px;

                margin-bottom:
                    10px;

                border-radius:
                    10px;

            }}


            .remark p {{

                margin:
                    8px 0;

            }}


            .remark small {{

                color:
                    #64748b;

            }}


            .no-remark {{

                color:
                    #64748b;

            }}


            .empty {{

                background:
                    white;

                padding:
                    60px 20px;

                text-align:
                    center;

                border-radius:
                    15px;

            }}


            @media(max-width:700px) {{

                .header {{

                    flex-direction:
                        column;

                }}

                .navbar {{

                    padding:
                        15px 20px;

                }}

            }}

        </style>

    </head>


    <body>


        <div class="navbar">

            <div class="brand">

                🏛️ CivicConnect

            </div>


            <div class="user-info">

                👤 {current_user.name}

                <br>

                <a
                    href="/logout"
                    class="logout"
                >
                    Logout
                </a>

            </div>

        </div>


        <div class="container">


            <div class="welcome">

                <h1>
                    My Complaints
                </h1>

                <p>
                    Track the progress of your reported public issues.
                </p>

            </div>


            {complaint_cards}


        </div>


    </body>

    </html>

    """


if __name__ == "__main__":

    print()
    print("========================================")
    print(" CivicConnect Citizen Status Portal")
    print("========================================")
    print()
    print("Open:")
    print("http://127.0.0.1:5001/citizen/status")
    print()

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False,
        use_reloader=False
    )
