from vocabulizer import db, create_app
from vocabulizer.settings import PORT
from vocabulizer.jobs import jobs_scheduler

app = create_app()

if __name__ == "__main__":
    # db.create_all(app=create_app())
    jobs_scheduler.run()
    app.run(port=PORT)

