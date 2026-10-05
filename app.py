import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from flask_socketio import (
    SocketIO,
    join_room
)

from werkzeug.utils import secure_filename

from config import Config

from models import (
    db,
    User,
    Complaint,
    Department,
    Remark
)
from automatic_complaint_router import route_new_complaint


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)
app.config.from_object(Config)


# =========================================================
# DATABASE
# =========================================================

db.init_app(app)


# =========================================================
# LOGIN MANAGER
# =========================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

login_manager.login_message = "Please login to continue."


@login_manager.user_loader
def load_user(user_id):

    try:
        return db.session.get(User, int(user_id))

    except (ValueError, TypeError):
        return None


# =========================================================
# SOCKET IO
# =========================================================

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)


# =========================================================
# UPLOAD FOLDER
# =========================================================

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)


# =========================================================
# ALLOWED IMAGE EXTENSIONS
# =========================================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    # Already logged in
    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard")
        )


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()


        email = request.form.get(
            "email",
            ""
        ).strip().lower()


        password = request.form.get(
            "password",
            ""
        )


        # -------------------------
        # VALIDATION
        # -------------------------

        if not name or not email or not password:

            flash(
                "Please fill all fields.",
                "danger"
            )

            return redirect(
                url_for("register")
            )


        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(
                url_for("register")
            )


        # -------------------------
        # CHECK EXISTING USER
        # -------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()


        if existing_user:

            flash(
                "Email already registered.",
                "warning"
            )

            return redirect(
                url_for("register")
            )


        # -------------------------
        # CREATE CITIZEN
        # -------------------------

        user = User(
            name=name,
            email=email,
            role="citizen"
        )

        user.set_password(password)


        db.session.add(user)

        db.session.commit()


        flash(
            "Registration successful! Please login.",
            "success"
        )


        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard")
        )


    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()


        password = request.form.get(
            "password",
            ""
        )


        user = User.query.filter_by(
            email=email
        ).first()


        # -------------------------
        # CHECK LOGIN
        # -------------------------

        if user and user.check_password(password):

            login_user(user)


            flash(
                "Login successful!",
                "success"
            )


            return redirect(
                url_for("dashboard")
            )


        flash(
            "Invalid email or password.",
            "danger"
        )


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()


    flash(
        "You have been logged out.",
        "success"
    )


    return redirect(
        url_for("index")
    )


# =========================================================
# MAIN DASHBOARD REDIRECT
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    # ADMIN
    if current_user.role == "admin":

        return redirect(
            url_for("admin_dashboard")
        )


    # OFFICER
    if current_user.role == "officer":

        return redirect(
            url_for("officer_dashboard")
        )


    # CITIZEN
    return redirect(
        url_for("citizen_dashboard")
    )


# =========================================================
# CITIZEN DASHBOARD
# =========================================================

@app.route("/citizen/dashboard")
@login_required
def citizen_dashboard():

    if current_user.role != "citizen":

        return redirect(
            url_for("dashboard")
        )


    complaints = Complaint.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Complaint.created_at.desc()
    ).all()


    # -------------------------
    # STATISTICS
    # -------------------------

    total = len(complaints)


    pending = sum(
        c.status == "Pending"
        for c in complaints
    )


    progress = sum(
        c.status == "In Progress"
        for c in complaints
    )


    resolved = sum(
        c.status in ["Resolved", "Closed"]
        for c in complaints
    )


    return render_template(
        "citizen_dashboard.html",

        complaints=complaints,

        total=total,

        pending=pending,

        progress=progress,

        resolved=resolved
    )


# =========================================================
# CREATE COMPLAINT
# =========================================================

@app.route(
    "/complaint/create",
    methods=["GET", "POST"]
)
@login_required
def create_complaint():

    if current_user.role != "citizen":

        return redirect(
            url_for("dashboard")
        )


    departments = Department.query.order_by(
        Department.name.asc()
    ).all()


    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()


        issue_type = request.form.get(
            "issue_type",
            ""
        ).strip()


        description = request.form.get(
            "description",
            ""
        ).strip()


        location = request.form.get(
            "location",
            ""
        ).strip()


        priority = request.form.get(
            "priority",
            "Medium"
        ).strip()


        department_id = request.form.get(
            "department_id"
        )


        image = request.files.get(
            "image"
        )


        # -------------------------
        # REQUIRED FIELD CHECK
        # -------------------------

        if (
            not title
            or
            not issue_type
            or
            not description
            or
            not location
        ):

            flash(
                "Please fill all required complaint fields.",
                "danger"
            )

            return redirect(
                url_for("create_complaint")
            )


        # -------------------------
        # PRIORITY CHECK
        # -------------------------

        if priority not in [
            "Low",
            "Medium",
            "High"
        ]:

            priority = "Medium"


        # -------------------------
        # IMAGE UPLOAD
        # -------------------------

        filename = None


        if image and image.filename:

            if not allowed_file(image.filename):

                flash(
                    "Invalid image format. Use PNG, JPG, JPEG or WEBP.",
                    "danger"
                )

                return redirect(
                    url_for("create_complaint")
                )


            original_name = secure_filename(
                image.filename
            )


            # Prevent filename collision
            filename = original_name

            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )


            counter = 1


            while os.path.exists(file_path):

                name, extension = os.path.splitext(
                    original_name
                )


                filename = (
                    f"{name}_{counter}{extension}"
                )


                file_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )


                counter += 1


            image.save(file_path)


        # -------------------------
        # DEPARTMENT
        # -------------------------

        selected_department = None


        if department_id:

            try:

                selected_department = int(
                    department_id
                )

            except (ValueError, TypeError):

                selected_department = None


        # -------------------------
        # CREATE COMPLAINT
        # -------------------------

        complaint = Complaint(

            title=title,

            issue_type=issue_type,

            description=description,

            location=location,

            priority=priority,

            image=filename,

            user_id=current_user.id,

            department_id=selected_department

        )


        db.session.add(complaint)
        db.session.commit()

        # -----------------------------------------
        # AUTOMATIC DEPARTMENT + OFFICER ROUTING
        # -----------------------------------------

        routing_result = route_new_complaint(complaint)

        # -----------------------------------------
        # REAL-TIME EVENT
        # -----------------------------------------

        socketio.emit(
            "new_complaint",
            {
                "complaint_id": complaint.id,
                "title": complaint.title,
                "status": complaint.status,
                "priority": complaint.priority,
                "department": routing_result.get("department_name"),
                "officer": routing_result.get("officer_name")
            }
        )

        # -----------------------------------------
        # SUCCESS / WARNING MESSAGE
        # -----------------------------------------

        if routing_result.get("success"):

            department_name = routing_result.get(
                "department_name"
            )

            officer_name = routing_result.get(
                "officer_name"
            )

            if officer_name:

                flash(
                    f"Complaint submitted successfully! "
                    f"Automatically assigned to "
                    f"{department_name} department and "
                    f"officer {officer_name}.",
                    "success"
                )

            else:

                flash(
                    f"Complaint submitted successfully! "
                    f"Automatically routed to "
                    f"{department_name}. "
                    f"No officer is currently available, "
                    f"so the complaint is Pending.",
                    "warning"
                )

        else:

            flash(
                "Complaint submitted successfully, "
                "but automatic routing could not be completed: "
                f"{routing_result.get('message', 'Unknown error')}",
                "warning"
            )

        return redirect(
            url_for(
                "complaint_details",
                complaint_id=complaint.id
            )
        )

    return render_template(
        "create_complaint.html",
        departments=departments
    )


# =========================================================
# COMPLAINT DETAILS
# =========================================================

@app.route(
    "/complaint/<int:complaint_id>"
)
@login_required
def complaint_details(complaint_id):

    complaint = db.get_or_404(
        Complaint,
        complaint_id
    )


    # -------------------------
    # CITIZEN ACCESS CONTROL
    # -------------------------

    if (
        current_user.role == "citizen"
        and
        complaint.user_id != current_user.id
    ):

        flash(
            "You cannot view this complaint.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )


    # -------------------------
    # REMARKS
    # -------------------------

    remarks = Remark.query.filter_by(
        complaint_id=complaint.id
    ).order_by(
        Remark.created_at.desc()
    ).all()


    # -------------------------
    # DEPARTMENTS
    # -------------------------

    departments = Department.query.order_by(
        Department.name.asc()
    ).all()


    # -------------------------
    # OFFICERS
    # -------------------------

    officers = User.query.filter_by(
        role="officer"
    ).order_by(
        User.name.asc()
    ).all()


    return render_template(
        "complaint_details.html",

        complaint=complaint,

        remarks=remarks,

        departments=departments,

        officers=officers
    )


# =========================================================
# OFFICER DASHBOARD
# =========================================================

@app.route("/officer/dashboard")
@login_required
def officer_dashboard():

    if current_user.role not in [
        "officer",
        "admin"
    ]:

        return redirect(
            url_for("dashboard")
        )


    complaints = Complaint.query.order_by(
        Complaint.created_at.desc()
    ).all()


    departments = Department.query.order_by(
        Department.name.asc()
    ).all()


    officers = User.query.filter_by(
        role="officer"
    ).order_by(
        User.name.asc()
    ).all()


    # -------------------------
    # STATISTICS
    # -------------------------

    total = len(complaints)


    pending = sum(
        c.status == "Pending"
        for c in complaints
    )


    assigned = sum(
        c.status == "Assigned"
        for c in complaints
    )


    progress = sum(
        c.status == "In Progress"
        for c in complaints
    )


    resolved = sum(
        c.status in ["Resolved", "Closed"]
        for c in complaints
    )


    urgent = sum(
        c.priority == "High"
        and
        c.status not in ["Resolved", "Closed"]
        for c in complaints
    )


    return render_template(
        "officer_dashboard.html",

        complaints=complaints,

        departments=departments,

        officers=officers,

        total=total,

        pending=pending,

        assigned=assigned,

        progress=progress,

        resolved=resolved,

        urgent=urgent
    )


# =========================================================
# UPDATE COMPLAINT - OFFICER
# =========================================================

@app.route(
    "/complaint/update/<int:complaint_id>",
    methods=["POST"]
)
@login_required
def update_complaint(complaint_id):

    if current_user.role not in [
        "officer",
        "admin"
    ]:

        return redirect(
            url_for("dashboard")
        )


    complaint = db.get_or_404(
        Complaint,
        complaint_id
    )


    status = request.form.get(
        "status"
    )


    department_id = request.form.get(
        "department_id"
    )


    officer_id = request.form.get(
        "officer_id"
    )


    remark_text = request.form.get(
        "remark",
        ""
    ).strip()


    # -------------------------
    # STATUS
    # -------------------------

    allowed_statuses = [
        "Pending",
        "Assigned",
        "In Progress",
        "Resolved",
        "Closed"
    ]


    if status in allowed_statuses:

        complaint.status = status


    # -------------------------
    # DEPARTMENT
    # -------------------------

    if department_id:

        try:

            complaint.department_id = int(
                department_id
            )

        except (ValueError, TypeError):

            pass


    # -------------------------
    # ASSIGNED OFFICER
    # -------------------------

    if officer_id:

        try:

            selected_officer_id = int(
                officer_id
            )


            selected_officer = User.query.filter_by(
                id=selected_officer_id,
                role="officer"
            ).first()


            if selected_officer:

                complaint.assigned_officer_id = (
                    selected_officer.id
                )

        except (ValueError, TypeError):

            pass


    # -------------------------
    # REMARK
    # -------------------------

    if remark_text:

        remark = Remark(

            complaint_id=complaint.id,

            officer_id=current_user.id,

            remark=remark_text

        )


        db.session.add(
            remark
        )


    db.session.commit()


    # -------------------------
    # REAL-TIME UPDATE
    # -------------------------

    socketio.emit(
        "complaint_updated",

        {
            "complaint_id": complaint.id,

            "status": complaint.status,

            "priority": complaint.priority
        },

        room=f"complaint_{complaint.id}"
    )


    flash(
        "Complaint updated successfully!",
        "success"
    )


    return redirect(
        url_for("officer_dashboard")
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":

        return redirect(
            url_for("dashboard")
        )


    # -------------------------
    # USER STATISTICS
    # -------------------------

    users = User.query.count()


    citizens = User.query.filter_by(
        role="citizen"
    ).count()


    officers = User.query.filter_by(
        role="officer"
    ).count()


    admins = User.query.filter_by(
        role="admin"
    ).count()


    # -------------------------
    # COMPLAINT STATISTICS
    # -------------------------

    complaints = Complaint.query.count()


    pending = Complaint.query.filter_by(
        status="Pending"
    ).count()


    assigned = Complaint.query.filter_by(
        status="Assigned"
    ).count()


    progress = Complaint.query.filter_by(
        status="In Progress"
    ).count()


    resolved = Complaint.query.filter(
        Complaint.status.in_(
            ["Resolved", "Closed"]
        )
    ).count()


    high_priority = Complaint.query.filter(
        Complaint.priority == "High",
        Complaint.status.notin_(
            ["Resolved", "Closed"]
        )
    ).count()


    # -------------------------
    # RECENT COMPLAINTS
    # -------------------------

    recent_complaints = Complaint.query.order_by(
        Complaint.created_at.desc()
    ).limit(5).all()


    # -------------------------
    # DEPARTMENTS
    # -------------------------

    departments = Department.query.order_by(
        Department.name.asc()
    ).all()


    return render_template(
        "admin_dashboard.html",

        users=users,

        citizens=citizens,

        officers=officers,

        admins=admins,

        complaints=complaints,

        pending=pending,

        assigned=assigned,

        progress=progress,

        resolved=resolved,

        high_priority=high_priority,

        recent_complaints=recent_complaints,

        departments=departments
    )


# =========================================================
# ADMIN - MANAGE COMPLAINTS
# =========================================================

@app.route("/admin/complaints")
@login_required
def admin_complaints():

    if current_user.role != "admin":

        return redirect(
            url_for("dashboard")
        )


    complaints = Complaint.query.order_by(
        Complaint.created_at.desc()
    ).all()


    departments = Department.query.order_by(
        Department.name.asc()
    ).all()


    officers = User.query.filter_by(
        role="officer"
    ).order_by(
        User.name.asc()
    ).all()


    return render_template(
        "admin_complaints.html",

        complaints=complaints,

        departments=departments,

        officers=officers
    )


# =========================================================
# ADMIN - UPDATE COMPLAINT
# =========================================================

@app.route(
    "/admin/complaint/<int:complaint_id>/update",
    methods=["POST"]
)
@login_required
def admin_update_complaint(complaint_id):

    if current_user.role != "admin":

        return redirect(
            url_for("dashboard")
        )


    complaint = db.get_or_404(
        Complaint,
        complaint_id
    )


    status = request.form.get(
        "status"
    )


    priority = request.form.get(
        "priority"
    )


    # -------------------------
    # UPDATE STATUS
    # -------------------------

    allowed_statuses = [
        "Pending",
        "Assigned",
        "In Progress",
        "Resolved",
        "Closed"
    ]


    if status in allowed_statuses:

        complaint.status = status


    # -------------------------
    # UPDATE PRIORITY
    # -------------------------

    allowed_priorities = [
        "Low",
        "Medium",
        "High"
    ]


    if priority in allowed_priorities:

        complaint.priority = priority


    db.session.commit()


    # -------------------------
    # REAL-TIME UPDATE
    # -------------------------

    socketio.emit(

        "complaint_updated",

        {
            "complaint_id": complaint.id,

            "status": complaint.status,

            "priority": complaint.priority
        },

        room=f"complaint_{complaint.id}"

    )


    flash(
        "Complaint updated successfully!",
        "success"
    )


    return redirect(
        url_for("admin_complaints")
    )


# =========================================================
# ADMIN - USERS
# =========================================================

@app.route("/admin/users")
@login_required
def admin_users():

    if current_user.role != "admin":

        return redirect(
            url_for("dashboard")
        )


    users_list = User.query.order_by(
        User.id.desc()
    ).all()


    return render_template(
        "admin_users.html",

        users_list=users_list
    )


# =========================================================
# ADMIN - CHANGE USER ROLE
# =========================================================

@app.route(
    "/admin/user/<int:user_id>/role",
    methods=["POST"]
)
@login_required
def admin_update_user_role(user_id):

    if current_user.role != "admin":

        return redirect(
            url_for("dashboard")
        )


    user = db.get_or_404(
        User,
        user_id
    )


    new_role = request.form.get(
        "role"
    )


    allowed_roles = [
        "citizen",
        "officer",
        "admin"
    ]


    if new_role not in allowed_roles:

        flash(
            "Invalid role.",
            "danger"
        )

        return redirect(
            url_for("admin_users")
        )


    # -------------------------
    # PROTECT CURRENT ADMIN
    # -------------------------

    if user.id == current_user.id:

        flash(
            "You cannot change your own role.",
            "warning"
        )

        return redirect(
            url_for("admin_users")
        )


    user.role = new_role


    db.session.commit()


    flash(
        "User role updated successfully!",
        "success"
    )


    return redirect(
        url_for("admin_users")
    )


# =========================================================
# ADMIN - ADD DEPARTMENT
# =========================================================

@app.route(
    "/admin/add-department",
    methods=["POST"]
)
@login_required
def add_department():

    if current_user.role != "admin":

        return redirect(
            url_for("dashboard")
        )


    name = request.form.get(
        "name",
        ""
    ).strip()


    if not name:

        flash(
            "Department name is required.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )


    # -------------------------
    # CHECK DUPLICATE
    # -------------------------

    existing = Department.query.filter_by(
        name=name
    ).first()


    if existing:

        flash(
            "Department already exists.",
            "warning"
        )

        return redirect(
            url_for("admin_dashboard")
        )


    # -------------------------
    # CREATE DEPARTMENT
    # -------------------------

    department = Department(
        name=name
    )


    db.session.add(
        department
    )


    db.session.commit()


    flash(
        "Department added successfully!",
        "success"
    )


    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# REAL-TIME SOCKET
# =========================================================

@socketio.on("join_complaint")
def join_complaint(data):

    if not data:
        return


    complaint_id = data.get(
        "complaint_id"
    )


    if complaint_id:

        join_room(
            f"complaint_{complaint_id}"
        )


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

with app.app_context():

    db.create_all()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    socketio.run(

        app,

        debug=True,

        allow_unsafe_werkzeug=True

    )