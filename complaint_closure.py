
from app import app
from models import db, Complaint
from department_notification_store import add_notification


def close_complaint(complaint_id):

    with app.app_context():

        # Use the current SQLAlchemy method
        complaint = db.session.get(
            Complaint,
            complaint_id
        )

        if complaint is None:
            return {
                "success": False,
                "message": "Complaint not found."
            }

        # Already closed
        if complaint.status == "Closed":
            return {
                "success": True,
                "message": (
                    f"Complaint #{complaint_id} is already closed."
                ),
                "complaint_id": complaint.id,
                "status": "Closed"
            }

        # Only Resolved complaints can be closed
        if complaint.status != "Resolved":
            return {
                "success": False,
                "message": (
                    f"Complaint #{complaint_id} cannot be closed. "
                    f"Current status: {complaint.status}"
                )
            }

        # Change status
        complaint.status = "Closed"

        # Save to MySQL
        db.session.commit()

        # Add notification using the existing
        # CivicConnect notification structure
        add_notification(
            notification_type="closed",
            title="Complaint Closed",
            message=(
                f"Complaint #{complaint.id} has been closed."
            ),
            complaint_id=complaint.id,
            department_id=complaint.department_id,
            officer_id=complaint.assigned_officer_id
        )

        return {
            "success": True,
            "message": (
                f"Complaint #{complaint_id} closed successfully."
            ),
            "complaint_id": complaint.id,
            "status": complaint.status
        }


if __name__ == "__main__":

    print()
    print("=" * 45)
    print(" CivicConnect Complaint Closure")
    print("=" * 45)

    try:

        complaint_id = int(
            input("Enter Complaint ID to close: ")
        )

        result = close_complaint(
            complaint_id
        )

        print()

        if result["success"]:

            print("SUCCESS")
            print(result["message"])
            print("Status:", result["status"])

        else:

            print("FAILED")
            print(result["message"])

    except ValueError:

        print()
        print("Please enter a valid complaint ID.")

    print("=" * 45)
