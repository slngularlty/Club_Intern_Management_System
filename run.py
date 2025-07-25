import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.models.db import create_initial_admin

app = create_app()

with app.app_context():
    initial_admin_username = os.environ.get('ADMIN_USERNAME')
    initial_admin_password = os.environ.get('ADMIN_PASSWORD')

    if initial_admin_username and initial_admin_password:
        create_initial_admin(initial_admin_username, initial_admin_password)
    else:
        print("WARNING: ADMIN_USERNAME or ADMIN_PASSWORD not set in .env. Initial admin not created automatically.")
        print("If this is a new setup and no admins exist, you'll need to create one manually or via shell.")

if __name__ == '__main__':
    app.run(debug=True)