import boto3
from botocore.exceptions import ClientError

 # Create an s3 client.
s3 = boto3.client('s3')


try:
    # Upload parrot.gif to a user-specified bucket.
    s3.put_object(Body=open("parrot.gif", 'rb'),
                  Bucket="kivmob.com",
                  Key=input("Enter key: "))
except ClientError as e:
    print(e)