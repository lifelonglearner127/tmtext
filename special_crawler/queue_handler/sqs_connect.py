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

# import queue
from boto.sqs.message import Message
import boto.sqs

class SQS_Queue():
    def __init__(self, name):
        # self.item_queue = queue.Queue()

        self.conn = boto.sqs.connect_to_region("us-east-1")

        self.q = self.conn.get_queue(name)

        self.currentM = None

        # print("CLEARING QUEUE : (makes testing cleaner, but will be bad in production (IE if you have two nodes, one will clear the old one's contributions to the queue))")
        # self.q.clear() ####### WARNING : THIS CLEARS THE QUEUE


    def put(self, message):
        m = Message()
        if isinstance(message, str):
            m.set_body(message)
            self.q.write(m)
        elif isinstance(message, list) | isinstance(message, tuple):
            for row in message:
                m.set_body(row)
                self.q.write(m)

    def get(self):
        if self.currentM is None:
            rs = self.q.get_messages()
            m = rs[0]
            self.currentM = m
            return m.get_body()
        else:
            raise Exception("Incompleted message exists, consider issuing \"task_done\" before getting another message off the Queue. Message : %s"%self.currentM)

    def task_done(self):
        if self.currentM is not None:
            self.q.delete_message(self.currentM)
            self.currentM = None
        else:
            raise Exception("No current task to finish")
        #

    # Check if the SQS Queue is empty
    # due to a lag in the queue count, the count may be off,
    # so be sure to include some error checking 
    # (IE if you think the queue is full but it's really not)
    def empty(self):
        return self.q.count()<=0




def main():
    sqs = SQS_Queue()
    while(not sqs.empty()):
        print(sqs.get())
        sqs.task_done()

if __name__ == "__main__":
    print("starting...")
    main()
    print("...end")