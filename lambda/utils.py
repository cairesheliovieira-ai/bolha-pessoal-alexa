import logging
import os
import boto3
from botocore.exceptions import ClientError

def create_presigned_url(object_name):
    """Generate a presigned URL to share an S3 object"""
    s3_client = boto3.client('s3',
                             region_name=os.environ.get('AWS_REGION'))
    try:
        bucket_name = os.environ.get('S3_PERSISTENCE_BUCKET')
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=3600)
    except ClientError as e:
        logging.error(e)
        return None

    return response
