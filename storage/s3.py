try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import boto3

def s3_objects(paginator, bucket_name, prefix='/', delimiter='/', start_after=''):
    # Credit: https://stackoverflow.com/a/54014862/193812

    prefix = prefix.lstrip(delimiter)

    start_after = (start_after or prefix) if prefix.endswith(delimiter) else start_after

    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, StartAfter=start_after):
        for content in page.get('Contents', ()): # pylint: disable=use-yield-from
            yield content

def list_files(source):
    url = urlparse(source)

    bucket_name = url.netloc

    client = boto3.client('s3')
    paginator = client.get_paginator('list_objects_v2')

    file_list = []

    for s3_object in s3_objects(paginator, bucket_name, url.path):
        file_list.append({
            'name': s3_object['Key'],
            'size': s3_object['Size'],
            'updated': s3_object['LastModified'],
        })

    return file_list

def fetch_content(source, path):
    url = urlparse(source)

    bucket_name = url.netloc

    client = boto3.client('s3')

    s3_response_object = client.get_object(Bucket=bucket_name, Key=path)

    return s3_response_object['Body'].read(), s3_response_object['ContentType']
