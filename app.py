import subprocess

import spacy

from vocabulizer import db, create_app
from vocabulizer.settings import PORT

app = create_app()

if __name__ == "__main__":
    bashCommand = "python -m spacy download en_core_web_lg"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    nlp = spacy.load("en_core_web_sm")
    db.create_all(app=create_app())
    app.run(debug=True, port=PORT)

