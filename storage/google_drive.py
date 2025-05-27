# pylint: disable=no-member, line-too-long

import io
import os

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import arrow

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

CACHED_FOLDER_IDS = {}

def find_folder(service, parent_id, path, child_components):
    if path in CACHED_FOLDER_IDS:
        return CACHED_FOLDER_IDS[path]

    if len(child_components) == 0: # pylint: disable=len-as-condition
        CACHED_FOLDER_IDS[path] = parent_id

        return parent_id

    child_component = child_components[0]

    results = (service.files().list(q='"%s" in parents and name = "%s" and mimeType = "application/vnd.google-apps.folder"' % (parent_id, child_component), \
                                    pageSize=100, fields='nextPageToken, files(id, name, size, parents, modifiedTime, mimeType)').execute())

    items = results.get('files', [])

    if len(items) == 0: # pylint: disable=len-as-condition
        folder_metadata = {
            'parents': [parent_id],
            'name': child_component,
            'mimeType': 'application/vnd.google-apps.folder',
        }

        new_file = service.files().create(body=folder_metadata, fields="id").execute()

        identifier = new_file.get('id')

        CACHED_FOLDER_IDS[path] = identifier

        return identifier

    match = items[0]

    return find_folder(service, match['id'], path, child_components[1:])

def fetch_service(scopes):
    credentials = None

    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', scopes)

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)

            credentials = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w', encoding='utf8') as token:
            token.write(credentials.to_json())

    service = build('drive', 'v3', credentials=credentials)

    return service

def upload_content(destination, file_path, file_content, file_type):
    url = urlparse(destination)

    scopes = [
        'https://www.googleapis.com/auth/drive',
    ]

    root_id = url.netloc

    service = fetch_service(scopes)

    path_components = file_path.split('/')

    folder_id = find_folder(service, root_id, '/'.join(path_components[:-1]), path_components[:-1])

    file_metadata = {
        'parents': [folder_id],
        'name': path_components[-1],
        'mimeType': file_type,
    }

    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype=file_type, resumable=True)

    new_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    identifier = new_file.get('id')

    return identifier

def needs_update(service, root_id, name, size, updated):
    path_components = name.split('/')

    folder_id = find_folder(service, root_id, '/'.join(path_components[:-1]), path_components[:-1])

    results = (service.files().list(q='"%s" in parents and name = "%s"' % (folder_id, path_components[-1]), \
                                    pageSize=20, fields='nextPageToken, files(id, name, size, parents, modifiedTime, mimeType)').execute())

    items = results.get('files', [])

    if len(items) == 0: # pylint: disable=len-as-condition
        return True

    match = items[0]

    if int(match['size']) != size:
        return True

    last_updated = arrow.get(match['modifiedTime']).datetime

    if last_updated < updated:
        return True

    return False

def create_sync_request(file_list, destination):
    url = urlparse(destination)

    scopes = [
        'https://www.googleapis.com/auth/drive',
    ]

    service = fetch_service(scopes)

    requested_files = []

    for file_item in file_list:
        if needs_update(service, url.netloc, file_item['name'], file_item['size'], file_item['updated']):
            requested_files.append(file_item['name'])
        else:
            print('Skipping %s...' % file_item['name'])

    return requested_files
