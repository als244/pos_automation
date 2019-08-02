import email
import imaplib
import os
from email.utils import parseaddr

class FetchEmail():

    connection = None
    error = None

    def __init__(self, mail_server, username, password):
        self.connection = imaplib.IMAP4_SSL(mail_server)
        self.connection.login(username, password)
        self.connection.select("INBOX", readonly=False) # so we can mark mails as read

    def close_connection(self):
        """
        Close the connection to the IMAP server
        """
        self.connection.logout()
        

    def fetch_unread_messages(self):
        """
        Retrieve unread messages
        """
        self.connection.select()
        emails = []
        (result, messages) = self.connection.search(None, 'UnSeen')
        if result == "OK":

            for message in messages[0].split(b' '):
                try:
                    ret, data = self.connection.fetch(message,'(RFC822)')
                except Exception as e:
                    return emails

                msg = email.message_from_bytes(data[0][1])
                if isinstance(msg, str) == False:
                    emails.append(msg)
                response, data = self.connection.store(message, '+FLAGS','\\Seen')

            return emails

        self.error = "Failed to retreive emails."
        return emails