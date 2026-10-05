
"""
CivicConnect - Municipal Department Seeder

This file adds common real-world municipal departments
to the existing CivicConnect database.

IMPORTANT:
- Do NOT modify existing project files.
- Run this file manually from the CivicConnect project folder.
- Existing departments will not be duplicated.
"""

from app import app
from models import db, Department


# ============================================================
# REAL-WORLD MUNICIPAL DEPARTMENTS
# ============================================================

MUNICIPAL_DEPARTMENTS = [
    "Road & Public Works",
    "Solid Waste Management",
    "Water Supply",
    "Drainage & Sewerage",
    "Electrical & Street Lighting",
    "Parks & Garden",
    "Town Planning",
    "Public Health"
]


# ============================================================
# ADD DEPARTMENTS
# ============================================================

def seed_departments():

    added = 0
    already_exists = 0

    with app.app_context():

        for department_name in MUNICIPAL_DEPARTMENTS:

            existing_department = Department.query.filter_by(
                name=department_name
            ).first()

            if existing_department:
                already_exists += 1
                print(f"[EXISTS] {department_name}")
            else:
                new_department = Department(
                    name=department_name
                )

                db.session.add(new_department)
                added += 1

                print(f"[ADDED]  {department_name}")

        db.session.commit()

    print("\n======================================")
    print(" MUNICIPAL DEPARTMENT SETUP COMPLETE")
    print("======================================")
    print(f"Departments added   : {added}")
    print(f"Already existed     : {already_exists}")
    print(f"Total departments   : {added + already_exists}")
    print("======================================\n")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    seed_departments()

