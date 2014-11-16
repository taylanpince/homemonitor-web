from boto import dynamodb2
from flask import Flask, render_template, request, Response
from time import time

from db import DatabaseManager, ENTRY_TYPES


AWS_REGION = "us-east"
TABLE_NAME = "monitor_logs"


app = Flask(__name__)


@app.route("/")
def home():
    graphs = {}

    for entry_type in dict(ENTRY_TYPES).keys():
        graphs[entry_type] = app.db.table.query(
            entry_type__eq=entry_type,
            limit=100
        )

    return render_template("home.html", 
        graphs=graphs,
    )


@app.route("/entries", methods=["POST"])
def create_entry():
    """
    Store a new entry log
    """
    print request.json

    with app.db.table.batch_write() as batch:
        for entry_type in dict(ENTRY_TYPES).keys():
            batch.put_item(data={
                "entry_type": entry_type,
                "date_created": int(time()),
                "reading": request.json.get(entry_type)
            })

    return Response(status=200)


if __name__ == "__main__":
    db_connection = dynamodb2.connect_to_region(AWS_REGION)

    app.db = DatabaseManager(db_connection)
    app.run(host="0.0.0.0", port=80)
