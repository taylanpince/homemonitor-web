import logging

from boto import dynamodb2
from flask import Flask, render_template, request, Response
from time import time

from db import DatabaseManager, ENTRY_TYPES, Reading


AWS_REGION = "us-east-1"
TABLE_NAME = "monitor_logs"


app = Flask(__name__)


@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)
        
        db_connection = dynamodb2.connect_to_region(AWS_REGION)
        
        app.db = DatabaseManager(db_connection)


@app.route("/")
def home():
    graphs = {}

    for entry_type in dict(ENTRY_TYPES).keys():
        graphs[entry_type] = [Reading(i) for i in app.db.table.query(
            entry_type__eq=entry_type,
            limit=100,
            reverse=True
        )]

    return render_template("home.html", 
        graphs=graphs,
    )


@app.route("/entries", methods=["POST"])
def create_entry():
    """
    Store a new entry log
    """
    with app.db.table.batch_write() as batch:
        for entry_type in dict(ENTRY_TYPES).keys():
            batch.put_item(data={
                "entry_type": entry_type,
                "date_created": int(time()),
                "reading": request.json.get(entry_type)
            })

    return Response(status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
