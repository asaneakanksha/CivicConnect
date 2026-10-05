from getpass import getpass

from app import app
from models import db, User


def create_officer():

    print()
    print("========================================")
    print("     CIVICCONNECT OFFICER CREATION")
    print("========================================")
    print()

    name = input("Officer Name: ").strip()
    email = input("Officer Email: ").strip()
    password = getpass("Officer Password: ")

    if not name:
        print("Officer name is required.")
        return

    if not email:
        print("Officer email is required.")
        return

    if not password:
        print("Officer password is required.")
        return

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        print()
        print("An account with this email already exists.")
        print("Name :", existing_user.name)
        print("Role :", existing_user.role)
        return

    officer = User(
        name=name,
        email=email,
        role="officer"
    )

    officer.set_password(password)

    db.session.add(officer)
    db.session.commit()

    print()
    print("========================================")
    print("       OFFICER CREATED SUCCESSFULLY")
    print("========================================")
    print()
    print("Officer ID :", officer.id)
    print("Name       :", officer.name)
    print("Email      :", officer.email)
    print("Role       :", officer.role)
    print()
    print("You can now login at:")
    print("http://127.0.0.1:5001/officer/login")
    print()


if __name__ == "__main__":

    with app.app_context():
        create_officer()
