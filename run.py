from app import create_app
from app.db import create_db

app = create_app()

with app.app_context():
    create_db()


if __name__ == "__main__":
    app.run(debug=True)
