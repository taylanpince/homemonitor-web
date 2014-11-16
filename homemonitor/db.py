from boto.dynamodb2.fields import HashKey, RangeKey, AllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import NUMBER


TABLE_NAME = "monitor_logs"

ENTRY_TYPE_PRESSURE = "pressure"
ENTRY_TYPE_UV = "uv"
ENTRY_TYPE_TEMPERATURE = "temperature"

ENTRY_TYPES = (
    (ENTRY_TYPE_TEMPERATURE, "Temperature"),
    (ENTRY_TYPE_UV, "UV"),
    (ENTRY_TYPE_PRESSURE, "Pressure"),
)


class DatabaseManager(object):
    """
    Database manager layer for DynamoDB
    """
    def __init__(self, connection, debug=False):
        super(DatabaseManager, self).__init__()

        self.connection = connection

        tables_list = self.connection.list_tables()

        if TABLE_NAME in tables_list.get("TableNames"):
            self.table = Table(table_name=TABLE_NAME, connection=self.connection)
        else:
            self.table = Table.create(TABLE_NAME, [
                HashKey("entry_type"), 
                RangeKey("date_created", data_type=NUMBER)
            ], indexes=[
                AllIndex("DateJoinedIndex", parts=[
                    HashKey("entry_type"), 
                    RangeKey("date_created", data_type=NUMBER)
                ])
            ], connection=self.connection)
