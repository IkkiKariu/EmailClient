class EmailMessage:
    def __init__(self, uid, sender, receiver):
        self._uid = uid
        self._sender = sender
        self._receiver = receiver

    def uid(self):
        return self._uid

    def sender(self):
        return self._sender

    def receiver(self):
        return self._receiver


class IncomingEmailMessage(EmailMessage):
    def __init__(self, uid, sender, receiver, subject, plain_text, html_text, is_ik_encrypted):
        super().__init__(uid, sender, receiver)
        self._subject = subject
        self._plain_text = plain_text
        self._html_text = html_text
        self._is_ik_encrypted = is_ik_encrypted

    def subject(self):
        return self._subject

    def plain_text(self):
        return self._plain_text

    def html_text(self):
        return self._html_text

    def is_ik_encrypted(self):
        return self._is_ik_encrypted