MAILBOX_COUNT = 0

HOSTS = ['imap.gmail.com', 'imap.yandex.ru']
SMTP_HOSTS = ['smtp.gmail.com', 'smtp.yandex.ru']
SMTP_PORTS = {'smtp.gmail.com': 465, 'smtp.yandex.ru': 465}

CORRESPONDING_FOLDERS = {
    'imap.gmail.com': {
        'inbox': 'inbox',
        'trash': '[Gmail]/&BBoEPgRABDcEOAQ9BDA-',
        'sent': '[Gmail]/&BB4EQgQ,BEAEMAQyBDsENQQ9BD0ESwQ1-',
        'drafts': "[Gmail]/&BB4EQgQ,BEAEMAQyBDsENQQ9BD0ESwQ1-",
        'spam': '[Gmail]/&BCEEPwQwBDw-'
    },
    'imap.yandex.ru': {
        'inbox': 'inbox',
        'trash': 'Trash',
        'sent': 'Sent',
        'drafts': "Drafts",
        'spam': 'Spam'
    }
}

