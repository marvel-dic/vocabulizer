from vocabulizer import db, create_app
from vocabulizer.settings import PORT

app = create_app()

if __name__ == "__main__":
    db.create_all(app=create_app())
    app.run(debug=True, port=PORT)

