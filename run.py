from app import create_app

app = create_app()

if __name__ == "__main__":
    from app.db import create_db

    with app.app_context():
        create_db()
    app.run(debug=True)
