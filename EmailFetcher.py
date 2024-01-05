import imaplib
import email
from email import header
import email.utils
from Models import EmailMessagesModels


class EmailFetcher:
    def __init__(self):
        pass

    def establish_login_select(self, imap_server: str, folder: str, login: str, password: str):
        imap_conn = imaplib.IMAP4_SSL(imap_server)
        imap_conn.login(login, password)
        imap_conn.select(folder)

        return imap_conn

    def imap_logout(self, imap_conn: imaplib.IMAP4_SSL):
        imap_conn.logout()

    def fetch_letter_by_uid(self, imap_conn: imaplib.IMAP4_SSL, uid: str) -> list[bytes]:
        result, data = imap_conn.uid("fetch", uid, "(RFC822)")

        return [uid.encode(), data]

    def obtain_header(self, msg):
        # decode the email subject
        header_data = ""

        for data_part in msg:
            if isinstance(data_part[0], bytes):
                if data_part[1] == None:
                    header_data += data_part[0].decode()
                else:
                    header_data += data_part[0].decode(data_part[1])
            else:
                if len(data_part[0]) == 0:
                    header_data += "(нет данных)"
                else:
                    header_data += data_part[0]

        return header_data

    def convert_raw_email_data(self, raw_email_message_data: list[bytes]) -> EmailMessagesModels.IncomingEmailMessage:
        uid: str = raw_email_message_data[0].decode()
        msg = raw_email_message_data[1]

        raw_email_data = msg[0][1]
        email_message = email.message_from_bytes(raw_email_data)

        subject = self.obtain_header(email.header.decode_header(email_message["Subject"]))
        sender = self.obtain_header(email.header.decode_header(email_message["From"]))
        receiver = self.obtain_header(email.header.decode_header(email_message["To"]))

        is_ik_encrypted_message = email_message["X-IK-Encrypted"]
        if is_ik_encrypted_message:
            is_ik_encrypted_message = self.obtain_header(email.header.decode_header(is_ik_encrypted_message))

        text = None
        html = None

        # Извлечение полезных нагрузок
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain':
                # Извлечение обычного текста
                text = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
            if part.get_content_type() == 'text/html':
                # Извлечение HTML
                html = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
            if part.get_content_disposition() == 'attachment':
                # Извлечение вложений
                raw_filename = email.header.decode_header(part.get_filename())
                print(f"raw_filename: {raw_filename}")
                filename = self.obtain_header(email.header.decode_header(part.get_filename()))
                print(f"filename: {filename}")
                filename = filename.replace('\\', '/').split('/')[-1]
                if is_ik_encrypted_message != None and part.get_content_type() == "application/octet-stream":
                    # it means that letter was encrypted by this mail client
                    with open(f"tmpEncryptedMessage\\{filename}", "wb") as f:
                        if part.get_content_charset():
                            attachment = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                        else:
                            attachment = part.get_payload(decode=True)

                        f.write(attachment)
                else:
                    with open(f"tmpAttachments\\{filename}", "wb") as f:
                        if part.get_content_charset():
                            attachment = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                        else:
                            attachment = part.get_payload(decode=True)

                        f.write(attachment)

        # ---> letter composing
        incoming_email_message = EmailMessagesModels.IncomingEmailMessage(uid, sender, 'me', subject, text,
                                                                          html, is_ik_encrypted_message)
        return incoming_email_message

    def peek_email_data(self, imap_conn: imaplib.IMAP4_SSL, uid: str) -> dict[str, str]:
        resp, msg_data = imap_conn.uid('fetch', uid, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE TO)])')

        letter_data = {}

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                # subject extracting
                try:
                    subject = self.obtain_header(email.header.decode_header(msg['Subject']))
                except:
                    subject = '(без темы)'

                # sender extracting
                try:
                    sender = self.obtain_header(email.header.decode_header(msg['From']))
                except:
                    sender = '(без отправителя)'

                # receiver extracting
                try:
                    receiver = self.obtain_header(email.header.decode_header(msg['To']))
                except:
                    receiver = '(без адресата)'

                # date and time extracting
                raw_date = msg["Date"]
                date_obj = email.utils.parsedate_to_datetime(raw_date)
                local_date_obj = date_obj.astimezone()

                prepared_date = local_date_obj.date().strftime("%Y-%m-%d")
                prepared_time = local_date_obj.time().strftime("%H:%M")

                # packaging
                letter_data["Sender"] = sender
                letter_data["Subject"] = subject
                letter_data["uid"] = uid
                letter_data["Date"] = prepared_date
                letter_data["Time"] = prepared_time
                letter_data["Receiver"] = receiver

        return letter_data

    def get_all_uid(self, imap_conn: imaplib.IMAP4_SSL) -> list[str]:
        uids_list = []

        resp, uids = imap_conn.uid('search', None, 'ALL')

        for uid in uids[0].split():
            uids_list.append(uid.decode())

        uids_list.reverse()
        return uids_list


email_fetcher = EmailFetcher()
