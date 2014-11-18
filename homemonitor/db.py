import datetime
import time
import pytz

from boto.dynamodb2.fields import HashKey, RangeKey, AllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import NUMBER


AWS_REGION = "us-east-1"
TABLE_NAME = "monitor_logs"
LOCAL_TIMEZONE = pytz.timezone("EST")

ENTRY_TYPE_HUMIDITY = "humidity"
ENTRY_TYPE_TEMPERATURE = "temperature"
ENTRY_TYPE_UV = "uv"
ENTRY_TYPE_LUMINANCE = "luminance"
ENTRY_TYPE_LOUDNESS = "loudness"

ENTRY_TYPES = (
    (ENTRY_TYPE_TEMPERATURE, "Temperature (Celcius)"),
    (ENTRY_TYPE_HUMIDITY, "Humidity (%)"),
    (ENTRY_TYPE_UV, "UV (mV)"),
    (ENTRY_TYPE_LOUDNESS, "Loudness (dB)"),
    (ENTRY_TYPE_LUMINANCE, "Luminance (V)"),
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


class Reading(object):
    """
    A model for handling reading entries
    """
    def __init__(self, db_reading):
        super(Reading, self).__init__()

        self.entry_type = db_reading.get("entry_type")
        self.timestamp = db_reading.get("date_created")
        self.reading = db_reading.get("reading")
        
        naive_date = datetime.datetime.fromtimestamp(self.timestamp)
        utc_date = pytz.utc.localize(naive_date)
        local_date = utc_date.astimezone(LOCAL_TIMEZONE)
        
        self.date_created = local_date.strftime("%b %d %H:%M:%S")

    def is_valid(self):
        """
        Checks if the reading value is valid
        """
        if self.reading is None:
            return False

        if self.entry_type == ENTRY_TYPE_HUMIDITY:
            return (float(self.reading) > 10)
        elif self.entry_type == ENTRY_TYPE_LUMINANCE:
            return (float(self.reading) > 0)
        elif self.entry_type == ENTRY_TYPE_LOUDNESS:
            return (float(self.reading) > 0)
        elif self.entry_type == ENTRY_TYPE_UV:
            return (float(self.reading) > 150)
        elif self.entry_type == ENTRY_TYPE_TEMPERATURE:
            return (float(self.reading) > -10)
            
        return True
