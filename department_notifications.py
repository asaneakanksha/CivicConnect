
"""
CivicConnect - Department Notifications

Purpose:
    Creates notification information for municipal
    departments and officers.

Workflow events:
    - New complaint assigned
    - Officer assigned
    - Work started
    - Complaint resolved
    - Complaint closed
    - High priority complaint

IMPORTANT:
    This is a NEW helper file.
    Existing CivicConnect files are not modified.
"""

from datetime import datetime


# ============================================================
# NOTIFICATION TYPES
# ============================================================

NOTIFICATION_TYPES = {
    "new_complaint": "New Complaint",
    "assignment": "Complaint Assignment",
    "work_started": "Work Started",
    "resolved": "Complaint Resolved",
    "closed": "Complaint Closed",
    "high_priority": "High Priority Complaint"
}


# ============================================================
# CREATE NOTIFICATION
# ============================================================

def create_notification(
    notification_type,
    complaint_id,
    message,
    department_id=None,
    officer_id=None
):
    """
    Create a notification dictionary.

    This does not write anything to the database yet.
    """

    if notification_type not in NOTIFICATION_TYPES:
        return {
            "success": False,
            "message": "Invalid notification type."
        }

    if not complaint_id:
        return {
            "success": False,
            "message": "Complaint ID is required."
        }

    if not message or not message.strip():
        return {
            "success": False,
            "message": "Notification message is required."
        }

    return {
        "success": True,
        "notification": {
            "type": notification_type,
            "title": NOTIFICATION_TYPES[
                notification_type
            ],
            "complaint_id": complaint_id,
            "department_id": department_id,
            "officer_id": officer_id,
            "message": message.strip(),
            "created_at": datetime.utcnow(),
            "read": False
        }
    }


# ============================================================
# NEW COMPLAINT NOTIFICATION
# ============================================================

def notify_new_complaint(
    complaint_id,
    department_id,
    issue_type
):
    """
    Notify a department that a new complaint
    has been assigned to it.
    """

    return create_notification(
        notification_type="new_complaint",
        complaint_id=complaint_id,
        department_id=department_id,
        message=(
            f"New {issue_type} complaint "
            f"#{complaint_id} has been assigned "
            "to your department."
        )
    )


# ============================================================
# OFFICER ASSIGNMENT NOTIFICATION
# ============================================================

def notify_officer_assignment(
    complaint_id,
    department_id,
    officer_id
):
    """
    Notify an officer that a complaint has been
    assigned to them.
    """

    return create_notification(
        notification_type="assignment",
        complaint_id=complaint_id,
        department_id=department_id,
        officer_id=officer_id,
        message=(
            f"Complaint #{complaint_id} "
            "has been assigned to you."
        )
    )


# ============================================================
# WORK STARTED NOTIFICATION
# ============================================================

def notify_work_started(
    complaint_id,
    department_id,
    officer_id
):
    """
    Notify that department work has started.
    """

    return create_notification(
        notification_type="work_started",
        complaint_id=complaint_id,
        department_id=department_id,
        officer_id=officer_id,
        message=(
            f"Work has started on complaint "
            f"#{complaint_id}."
        )
    )


# ============================================================
# RESOLVED NOTIFICATION
# ============================================================

def notify_resolved(
    complaint_id,
    department_id,
    officer_id,
    resolution_remark
):
    """
    Notify that a complaint has been resolved.
    """

    return create_notification(
        notification_type="resolved",
        complaint_id=complaint_id,
        department_id=department_id,
        officer_id=officer_id,
        message=(
            f"Complaint #{complaint_id} "
            "has been marked as Resolved. "
            f"Resolution: {resolution_remark}"
        )
    )


# ============================================================
# CLOSED NOTIFICATION
# ============================================================

def notify_closed(
    complaint_id,
    department_id
):
    """
    Notify that a complaint has been closed.
    """

    return create_notification(
        notification_type="closed",
        complaint_id=complaint_id,
        department_id=department_id,
        message=(
            f"Complaint #{complaint_id} "
            "has been Closed."
        )
    )


# ============================================================
# HIGH PRIORITY NOTIFICATION
# ============================================================

def notify_high_priority(
    complaint_id,
    department_id,
    issue_type
):
    """
    Notify a department about a high-priority complaint.
    """

    return create_notification(
        notification_type="high_priority",
        complaint_id=complaint_id,
        department_id=department_id,
        message=(
            f"URGENT: High-priority {issue_type} "
            f"complaint #{complaint_id} "
            "requires department attention."
        )
    )


# ============================================================
# NOTIFICATION FOR COMPLAINT
# ============================================================

def create_complaint_notifications(
    complaint_id,
    department_id,
    issue_type,
    priority="Medium"
):
    """
    Create the appropriate notifications when
    a complaint reaches a department.
    """

    notifications = []

    new_notification = notify_new_complaint(
        complaint_id,
        department_id,
        issue_type
    )

    if new_notification["success"]:
        notifications.append(
            new_notification["notification"]
        )

    if priority == "High":

        urgent_notification = notify_high_priority(
            complaint_id,
            department_id,
            issue_type
        )

        if urgent_notification["success"]:
            notifications.append(
                urgent_notification["notification"]
            )

    return {
        "success": True,
        "count": len(notifications),
        "notifications": notifications
    }


# ============================================================
# FILTER UNREAD NOTIFICATIONS
# ============================================================

def get_unread_notifications(notifications):
    """
    Return only unread notifications.
    """

    if not notifications:
        return []

    return [
        notification
        for notification in notifications
        if not notification.get("read", False)
    ]


# ============================================================
# MARK AS READ
# ============================================================

def mark_notification_read(notification):
    """
    Mark one notification as read.
    """

    if not notification:
        return {
            "success": False,
            "message": "Notification not found."
        }

    notification["read"] = True

    return {
        "success": True,
        "notification": notification,
        "message": "Notification marked as read."
    }


# ============================================================
# MARK ALL AS READ
# ============================================================

def mark_all_notifications_read(notifications):
    """
    Mark all notifications as read.
    """

    if not notifications:
        return {
            "success": True,
            "count": 0,
            "notifications": []
        }

    for notification in notifications:
        notification["read"] = True

    return {
        "success": True,
        "count": len(notifications),
        "notifications": notifications
    }


# ============================================================
# NOTIFICATION SUMMARY
# ============================================================

def get_notification_summary(notifications):
    """
    Return notification counts.
    """

    if not notifications:
        return {
            "total": 0,
            "unread": 0,
            "read": 0
        }

    unread = len(
        get_unread_notifications(notifications)
    )

    return {
        "total": len(notifications),
        "unread": unread,
        "read": len(notifications) - unread
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n==========================================")
    print(" CIVICCONNECT NOTIFICATION TEST")
    print("==========================================\n")

    result = create_complaint_notifications(
        complaint_id=101,
        department_id=1,
        issue_type="Pothole",
        priority="High"
    )

    notifications = result["notifications"]

    print(
        f"Notifications created: "
        f"{result['count']}\n"
    )

    for notification in notifications:

        print(
            f"Type       : {notification['title']}"
        )

        print(
            f"Complaint  : "
            f"#{notification['complaint_id']}"
        )

        print(
            f"Message    : "
            f"{notification['message']}"
        )

        print(
            f"Read       : "
            f"{notification['read']}"
        )

        print("------------------------------------------")

    summary = get_notification_summary(
        notifications
    )

    print("\nNotification Summary")
    print(
        f"Total  : {summary['total']}"
    )
    print(
        f"Unread : {summary['unread']}"
    )
    print(
        f"Read   : {summary['read']}"
    )

    print("\n==========================================")
    print(" TEST COMPLETED")
    print("==========================================\n")
