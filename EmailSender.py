import smtplib
import email


class EmailSender:
    def __init__(self):
        pass

    def establish_login_smtp(self, smtp_host: str, smtp_port: int, cur_user_address: str, cur_user_password) -> smtplib.SMTP_SSL:
        smtp_conn = smtplib.SMTP_SSL(smtp_host, smtp_port)
        smtp_conn.login(cur_user_address, cur_user_password)
        return smtp_conn

    def close_smtp_connection(self, smtp_conn: smtplib.SMTP_SSL):
        smtp_conn.close()

    def compose_email_message(self, sender: str, receiver: str, subject=None, body_text=None, attachments=None,
                             ) -> email.message.EmailMessage:
        # headers adding
        email_message = email.message.EmailMessage()
        email_message["From"] = sender
        email_message["To"] = receiver
        if subject == None:
            subject = "(без темы)"
        email_message["Subject"] = subject

        #content adding
        if body_text == None:
            body_text = "(письмо зашифровано)"
        email_message.set_content(body_text)

        #attachments adding


        return email_message

    def send_email(self, smtp_conn: smtplib.SMTP_SSL, prepared_email_message: email.message.EmailMessage):
        smtp_conn.send_message(prepared_email_message)

    def get_appropriate_smt_server(self, receiver_address: str):
        pass


email_sender = EmailSender()
