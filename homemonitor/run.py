import os

from boto.dynamodb2.layer1 import DynamoDBConnection

from application import app
from db import DatabaseManager


db_connection = DynamoDBConnection(
    aws_access_key_id="dummy_key",
    aws_secret_access_key="dummy_secret",
    host=os.environ["DYNAMODB_PORT_8000_TCP_ADDR"],
    port=8000,
    is_secure=False
)

app.db = DatabaseManager(db_connection)
app.run(debug=True, host="0.0.0.0", port=5000)
