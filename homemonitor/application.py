import logging

from boto import dynamodb2
from flask import Flask, render_template, request, Response
from math import ceil
from time import time

from db import DatabaseManager, ENTRY_TYPES, Reading, AWS_REGION


app = Flask(__name__)


TIME_FILTER_1_HOUR = 1

TIME_FILTER_OPTIONS = (
    (TIME_FILTER_1_HOUR, "1 hour ago"),
    (6, "6 hours ago"),
    (12, "12 hours ago"),
    (24, "Yesterday"),
    (48, "2 days ago"),
    (72, "3 days ago"),
    (120, "5 days ago"),
)


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
    try:
        time_since = int(request.args.get("time-since", TIME_FILTER_1_HOUR))
    except ValueError:
        time_since = TIME_FILTER_1_HOUR

    if not time_since in dict(TIME_FILTER_OPTIONS).keys():
        time_since = TIME_FILTER_1_HOUR

    time_start = int(time()) - (time_since * 60 * 60)

    graphs = []

    for entry_type, title in dict(ENTRY_TYPES).items():
        raw_entries = [Reading(i) for i in app.db.table.query_2(
            entry_type__eq=entry_type,
            date_created__gte=time_start,
            index="DateJoinedIndex",
            reverse=True
        ) if Reading(i).is_valid()]

        raw_entries.reverse()

        entries = []
        counter = 0
        average = 0.0
        loop = ceil(len(raw_entries) / 10)

        for reading in raw_entries:
            average += float(reading.reading)
            counter += 1

            if counter >= loop:
                entries.append(Reading({
                    "entry_type": entry_type,
                    "date_created": reading.timestamp,
                    "reading": round(average / counter, 1),
                }))

                counter = 0
                average = 0

        if counter > 0:
            entries.append(Reading({
                "entry_type": entry_type,
                "date_created": reading.timestamp,
                "reading": round(average / counter, 1),
            }))

        graphs.append({
            "entries": entries,
            "key": entry_type,
            "title": title,
        })

    return render_template("home.html", 
        graphs=graphs,
        time_options=dict(TIME_FILTER_OPTIONS),
        time_since=time_since,
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
