import sys, os
import boto
import datetime
import email
import mimetypes
import time


IGNORE_FILES = (
    ".DS_Store",
)


class S3SyncClient(object):
    """
    A basic S3 sync client that synchronizes a complete directory to a bucket on S3
    """
    def __init__(self, bucket_name, directory_path):
        self.bucket_name = bucket_name
        self.directory_path = directory_path

        if not self.directory_path.endswith("/"):
            self.directory_path += "/"

    def sync(self):
        bucket = self.open_connection()

        os.path.walk(self.directory_path, self.upload, bucket)

    def open_connection(self):
        conn = boto.connect_s3()

        try:
            bucket = conn.get_bucket(self.bucket_name)
        except boto.exception.S3ResponseError:
            bucket = conn.create_bucket(self.bucket_name)

        return bucket

    def upload(self, bucket, dirname, names):
        for filename in names:
            if filename in IGNORE_FILES:
                continue

            headers = {}
            file_path = os.path.join(dirname, filename)

            if os.path.isdir(file_path):
                continue

            file_key = file_path[len(self.directory_path):]

            s3_key = bucket.get_key(file_key)

            if s3_key:
                s3_datetime = datetime.datetime(*time.strptime(s3_key.last_modified, '%a, %d %b %Y %H:%M:%S %Z')[0:6])
                local_datetime = datetime.datetime.utcfromtimestamp(os.stat(file_path).st_mtime)

                # if local_datetime < s3_datetime:
                #     continue
            else:
                s3_key = bucket.new_key(file_key)

            print "Uploading %s" % (file_key)

            content_type = mimetypes.guess_type(file_path)[0]

            if content_type:
                headers['Content-Type'] = content_type

            file_obj = open(file_path, 'rb')
            file_size = os.fstat(file_obj.fileno()).st_size
            filedata = file_obj.read()

            try:
                s3_key.set_contents_from_string(filedata, headers, replace=True)
                s3_key.make_public()
            except boto.exception.S3CreateError, e:
                print "Failed: %s" % e
            except Exception, e:
                print e
                raise

            file_obj.close()


if __name__ == "__main__":
    client = S3SyncClient(
        "hipo.homemonitor", 
        os.path.realpath(os.path.join(os.path.dirname(__file__), "../homemonitor/static"))
    )

    client.sync()
