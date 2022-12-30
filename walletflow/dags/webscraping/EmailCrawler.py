import base64
import os
from os.path import join
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from lazyutils.structure.Callable import Callable
from lazyutils.config.Configuration import ConfigFromEnv


class EmailCrawler(Callable):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.modify',
              'https://www.googleapis.com/auth/gmail.labels']

    json_file = '.token.json'
    creds = None
    gmail = None
    download_folder = None

    def get_emails_attachments(self):
        # Query for messages with the subject "invoice"
        query = 'has:attachment newer_than:30d'
        has_next = True

        while has_next:
            result = self.gmail.users().messages().list(userId='me', q=query).execute()
            has_next = 'nextPageToken' in result

            # Download each message and save it to the folder
            for message in result['messages']:
                msg = self.gmail.users().messages().get(userId='me', id=message['id']).execute()
                # body = msg['payload']['body']
                data = None

                if msg['payload']['mimeType'] == 'multipart/mixed':
                    for part in msg['payload']['parts']:

                        if 'attachmentId' in part['body']:
                            attachment = self.gmail.users().messages().attachments().get(
                                userId='me', messageId=message['id'], id=part['body']['attachmentId']).execute()
                            data = attachment['data']
                        elif 'data' in part['body']:
                            data = part['body']['data']
                        else:
                            logging.info('Email without HTML body')

                        if data is not None:
                            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

                            if part['mimeType'] == 'application/pdf':
                                file_name = part['headers'][-1]['value']\
                                    .replace('attachment; filename="', '')\
                                    .replace('"', '')

                                file_path = os.path.join(self.download_folder, file_name)
                                with open(file_path, 'wb') as f:
                                    f.write(file_data)

                self.gmail\
                    .users()\
                    .messages()\
                    .modify(userId='me',
                            id=message['id'],
                            body={
                                'removeLabelIds': ['UNREAD', 'INBOX'],
                                'addLabelIds': ['Label_7731538836183880201']
                            })\
                    .execute()

    def login(self):
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.json_file):
            self.creds = Credentials.from_authorized_user_file(self.json_file, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_filepath, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.json_file, 'w') as token:
                token.write(self.creds.to_json())

        try:
            self.gmail = build('gmail', 'v1', credentials=self.creds)
        except HttpError as error:
            logging.warning(f'Not possible to log into gmail: {error}')

    def run(self):
        self.login()
        self.get_emails_attachments()

    def __init__(self):
        self.config = ConfigFromEnv()  # Initialize logging handler also

        self.download_folder = self.config['Webscrapping']['invoices_folder']

        self.credentials_filepath = join(self.config['Secrets']['folder'], self.config['Secrets']['gmail-credentials'])


if __name__ == '__main__':
    c = EmailCrawler()
    c.run()
    logging.info("Finished download invoices from Gmail")
