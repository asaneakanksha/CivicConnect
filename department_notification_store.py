
"""
CivicConnect - Department Notification Store

Purpose:
    Stores department notifications in a local JSON file.

Why JSON?
    The current CivicConnect database does not have a
    notification table.

IMPORTANT:
    This is a NEW file.
    Existing project files and database tables are not modified.
"""

import json
import os
from datetime import datetime


# ============================================================
# STORAGE LOCATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

NOTIFICATION_FILE = os.path.join(
    BASE_DIR,
    "department_notifications.json"
)


# ============================================================
# LOAD NOTIFICATIONS
# ============================================================

def load_notifications():
    """
    Load all saved notifications from JSON.
    """

    if not os.path.exists(NOTIFICATION_FILE):
        return []

    try:

        with open(
            NOTIFICATION_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError
    ):
        return []


# ============================================================
# SAVE NOTIFICATIONS
# ============================================================

def save_notifications(notifications):
    """
    Save notifications to JSON.
    """

    try:

        with open(
            NOTIFICATION_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                notifications,
                file,
                indent=4,
                ensure_ascii=False,
                default=str
            )

        return True

    except OSError:
        return False


# ============================================================
# CREATE NOTIFICATION
# ============================================================

def add_notification(
    notification_type,
    title,
    message,
    complaint_id,
    department_id=None,
    officer_id=None
):
    """
    Create and permanently save a notification.
    """

    notifications = load_notifications()

    notification = {
        "id": len(notifications) + 1,
        "type": notification_type,
        "title": title,
        "message": message,
        "complaint_id": complaint_id,
        "department_id": department_id,
        "officer_id": officer_id,
        "created_at": datetime.utcnow().isoformat(),
        "read": False
    }

    notifications.append(notification)

    saved = save_notifications(
        notifications
    )

    if not saved:
        return {
            "success": False,
            "notification": None,
            "message": (
                "Unable to save notification."
            )
        }

    return {
        "success": True,
        "notification": notification,
        "message": (
            "Notification saved successfully."
        )
    }


# ============================================================
# GET ALL NOTIFICATIONS
# ============================================================

def get_all_notifications():
    """
    Return every notification.
    """

    return load_notifications()


# ============================================================
# GET DEPARTMENT NOTIFICATIONS
# ============================================================

def get_department_notifications(
    department_id
):
    """
    Return notifications belonging to
    one department.
    """

    if not department_id:
        return []

    notifications = load_notifications()

    return [
        notification
        for notification in notifications
        if notification.get(
            "department_id"
        ) == department_id
    ]


# ============================================================
# GET OFFICER NOTIFICATIONS
# ============================================================

def get_officer_notifications(
    officer_id
):
    """
    Return notifications belonging to
    one officer.
    """

    if not officer_id:
        return []

    notifications = load_notifications()

    return [
        notification
        for notification in notifications
        if notification.get(
            "officer_id"
        ) == officer_id
    ]


# ============================================================
# GET UNREAD DEPARTMENT NOTIFICATIONS
# ============================================================

def get_unread_department_notifications(
    department_id
):
    """
    Return unread notifications for a department.
    """

    notifications = get_department_notifications(
        department_id
    )

    return [
        notification
        for notification in notifications
        if not notification.get(
            "read",
            False
        )
    ]


# ============================================================
# GET UNREAD OFFICER NOTIFICATIONS
# ============================================================

def get_unread_officer_notifications(
    officer_id
):
    """
    Return unread notifications for an officer.
    """

    notifications = get_officer_notifications(
        officer_id
    )

    return [
        notification
        for notification in notifications
        if not notification.get(
            "read",
            False
        )
    ]


# ============================================================
# MARK NOTIFICATION AS READ
# ============================================================

def mark_as_read(notification_id):
    """
    Mark one notification as read.
    """

    notifications = load_notifications()

    found = False

    for notification in notifications:

        if notification.get(
            "id"
        ) == notification_id:

            notification["read"] = True
            found = True
            break

    if not found:
        return {
            "success": False,
            "message": (
                "Notification not found."
            )
        }

    if not save_notifications(
        notifications
    ):
        return {
            "success": False,
            "message": (
                "Unable to update notification."
            )
        }

    return {
        "success": True,
        "message": (
            "Notification marked as read."
        )
    }


# ============================================================
# MARK ALL DEPARTMENT NOTIFICATIONS READ
# ============================================================

def mark_department_notifications_read(
    department_id
):
    """
    Mark all notifications of a department as read.
    """

    if not department_id:
        return {
            "success": False,
            "message": "Department ID is required."
        }

    notifications = load_notifications()

    count = 0

    for notification in notifications:

        if (
            notification.get(
                "department_id"
            ) == department_id
            and not notification.get(
                "read",
                False
            )
        ):

            notification["read"] = True
            count += 1

    save_notifications(
        notifications
    )

    return {
        "success": True,
        "count": count,
        "message": (
            f"{count} notification(s) "
            "marked as read."
        )
    }


# ============================================================
# DELETE OLD NOTIFICATION
# ============================================================

def delete_notification(
    notification_id
):
    """
    Delete one notification.
    """

    notifications = load_notifications()

    updated_notifications = [
        notification
        for notification in notifications
        if notification.get(
            "id"
        ) != notification_id
    ]

    if len(updated_notifications) == len(
        notifications
    ):
        return {
            "success": False,
            "message": (
                "Notification not found."
            )
        }

    save_notifications(
        updated_notifications
    )

    return {
        "success": True,
        "message": (
            "Notification deleted."
        )
    }


# ============================================================
# NOTIFICATION COUNT
# ============================================================

def get_notification_counts(
    department_id
):
    """
    Return total and unread notification counts.
    """

    notifications = get_department_notifications(
        department_id
    )

    unread = [
        notification
        for notification in notifications
        if not notification.get(
            "read",
            False
        )
    ]

    return {
        "total": len(notifications),
        "unread": len(unread),
        "read": (
            len(notifications)
            - len(unread)
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n==========================================")
    print(" CIVICCONNECT NOTIFICATION STORE TEST")
    print("==========================================\n")

    result = add_notification(
        notification_type="new_complaint",
        title="New Complaint",
        message=(
            "New Pothole complaint #101 "
            "has been assigned to your department."
        ),
        complaint_id=101,
        department_id=1
    )

    print(
        "Save Status:",
        result["success"]
    )

    print(
        "Message:",
        result["message"]
    )

    notifications = get_department_notifications(
        1
    )

    print(
        "\nDepartment notifications:",
        len(notifications)
    )

    unread = get_unread_department_notifications(
        1
    )

    print(
        "Unread notifications:",
        len(unread)
    )

    counts = get_notification_counts(
        1
    )

    print("\nCounts:")
    print(
        "Total :",
        counts["total"]
    )
    print(
        "Unread:",
        counts["unread"]
    )
    print(
        "Read  :",
        counts["read"]
    )

    print("\n==========================================")
    print(" TEST COMPLETED")
    print("==========================================\n")

    print(
        "Notification file:",
        NOTIFICATION_FILE
    )
