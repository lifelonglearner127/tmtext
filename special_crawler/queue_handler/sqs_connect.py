#!usr/bin/env python


""" 

This is a helper function that wraps the SQS Queue functionality 
so that it can be used like a regular Queue.

Make sure to issue "task_done" to delete an successfully
used item from the queue.



***  Note that AWS CREDENTIALS must be saved at:
***  
***  ~/.aws/credentials (Linux/Mac)
***  USERPROFILE%\.aws\credentials  (Windows)
***  
***  "credentials" is an extension-less file.
***  It must look like: (Note, the following are not real).
***  
***  [default]
***  aws_access_key_id = AKIAJEUCNGQ123AHDJEK
***  aws_secret_access_key = 4sdhHjdas78Kha8BdisasUdb17dhJdaks8As
***  
***  boto.sqs.connect_to_region needs these credentials to exist

"""

from boto.s3.connection import S3Connection
from boto.sqs.message import Message
import boto.sqs
import zlib
import json

class SQS_Queue():
    # Connect to the SQS Queue
    def __init__(self, name, region="us-east-1"):
        self.conn = boto.sqs.connect_to_region(region)
        self.q = self.conn.get_queue(name)
        self.currentM = None
        self.s3 = S3Connection('AKIAJPOFQWU54DCMDKLQ', '/aebM4IZ97NEwVnfS6Jys6sKVvDXa6eDZsB2X7gP')

    # Add message/a list of messages to the queue
    # Messages are strings (or at least serialized to strings)
    def put(self, sqs_message, s3_content=None):
        m = Message()
        try:
            if isinstance(sqs_message, basestring):
                m.set_body(sqs_message)
#                self.s3 = S3Connection('AKIAJPOFQWU54DCMDKLQ', '/aebM4IZ97NEwVnfS6Jys6sKVvDXa6eDZsB2X7gP')
                bucket = self.s3.create_bucket('contentanalytcis.inc.ch.s3')  # bucket names must be unique
                key = bucket.new_key(sqs_message["uuid"])
                key.set_contents_from_string(s3_content)

                self.q.write(m)
        except NameError:
            print "**********************"
            if isinstance(sqs_message, str):
                m.set_body(sqs_message)
                self.q.write(m)
        if isinstance(sqs_message, list) | isinstance(sqs_message, tuple):
            for row in sqs_message:
                m.set_body(row)
                self.q.write(m)

    # Get an item from the queue
    # Note : it remains on the queue until you call task_done
    def get(self, timeout=None):
        if self.currentM is None:
            rs = self.q.get_messages(visibility_timeout=timeout) \
                if timeout else self.q.get_messages()
            m = rs[0]
            self.currentM = m
            sqs_message = json.loads(m.get_body())

            bucket = self.s3.get_bucket('contentanalytcis.inc.ch.s3')  # bucket names must be unique
            key = bucket.get_key(sqs_message["uuid"])
            result_message = key.get_contents_as_string()
            bucket.delete_key(sqs_message["uuid"])
            return result_message
        else:
            raise Exception("Incompleted message exists, consider issuing \"task_done\" before getting another message off the Queue. Message : %s"%self.currentM)

    # SQS won't remove an item from the queue until you tell it to
    # this is how you tell it to
    def task_done(self):
        if self.currentM is not None:
            self.q.delete_message(self.currentM)
            self.currentM = None
        else:
            raise Exception("No current task to finish")
    
    # if a process gets a message, and fails, the currentM needs to be reset. Use this.
    def reset_message(self):
        self.currentM = None

    # completely clear out the SQS queue
    def clear(self):
        self.q.clear()

    # a rough estimate of how many objects are currently in the queue
    def count(self):
        return self.q.count()

    # Check if the SQS Queue is empty
    # due to a lag in the queue count, the count may be off,
    # so be sure to include some error checking 
    # (IE if you think the queue is full but it's really not)
    def empty(self):
        return self.q.count()<=0



#Some trial connection stuff for testing, may become outdated as the above is continually integrated into other components
def main():
    sqs = SQS_Queue()
    while(not sqs.empty()):
        print(sqs.get())
        sqs.task_done()

if __name__ == "__main__":
    print("starting...")
    main()
    print("...end")