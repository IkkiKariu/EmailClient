import os
from pathlib import Path
from Repository import JsonWriter
import config


def create_mailbox_files(address: str, password: str):
    Path(f'Mailboxes\\{address}').mkdir()

    JsonWriter.create_mailbox_credentials_file(f'Mailboxes\\{address}', address, password)


def load_mailboxes() -> list[str]:
    mailboxes_folder_path = Path('Mailboxes')
    mailbox_list = JsonWriter.fetch_all_mailboxes(mailboxes_folder_path)
    return mailbox_list


def get_already_peeked_messages(email_address: str) -> list[dict[str, str]]:
    return JsonWriter.fetch_already_peeked_email_messages(email_address)


def get_account_credentials(email_address: str) -> dict[str, str]:
    creds = JsonWriter.fetch_account_credentials(email_address)
    return creds


def get_appropriate_imap_host(email_address: str):
    email_address_parts = email_address.split('@')
    if 'gmail' in email_address_parts[1]:
        return config.HOSTS[0]
    elif 'yandex' in email_address_parts[1]:
        return config.HOSTS[1]


def get_appropriate_smtp_host(email_address: str):
    email_address_parts = email_address.split('@')
    if 'gmail' in email_address_parts[1]:
        return config.SMTP_HOSTS[0]
    elif 'yandex' in email_address_parts[1]:
        return config.SMTP_HOSTS[1]


def get_corresponding_folder(imap_host: str, common_name: str) -> str:
    return config.CORRESPONDING_FOLDERS[imap_host][common_name]


def get_mailbox_directories():
    dir_list = []
    for root, dirs, files in os.walk('Mailboxes'):
        for dir in dirs:
            dir_list.append(dir)
    print(dir_list)
    return dir_list


get_mailbox_directories()