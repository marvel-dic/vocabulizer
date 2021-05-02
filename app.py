from vocabulizer import db, create_app
from vocabulizer.settings import PORT

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=PORT)
    # db.create_all(app=create_app())
