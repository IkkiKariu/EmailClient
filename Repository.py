import json
from pathlib import Path
import config


class JsonWriter:
    @staticmethod
    def create_mailbox_credentials_file(mailbox_dir_path: str, email_address: str, password: str):
        mailbox_credential_dict = {'address': email_address, 'password': password}

        with open(f"{mailbox_dir_path}\\credentials.json", 'w') as f:
            json.dump(mailbox_credential_dict, f)

        config.USER_ADDRESS = email_address
        config.USER_PASSWORD = password

    @staticmethod
    def fetch_account_credentials(email_address: str) -> dict[str, str]:
        path_to_account_credentials = f"Mailboxes\\{email_address}\\credentials.json"
        with open(path_to_account_credentials, 'r') as f:
            credentials = json.load(f)
        return credentials

    @staticmethod
    def fetch_all_mailboxes(mailboxes_folder_path: Path) -> list[str]:
        mailbox_list = list()

        for item in mailboxes_folder_path.iterdir():
            path_to_credentials = item.__str__() + '\\credentials.json'
            # print(path_to_credentials)

            with open(path_to_credentials, 'r') as f:
                credentials = json.load(f)
                # print(credentials)
                address = credentials['address']
                # print(address)
                mailbox_list.append(address)

        # print(mailbox_list)
        return mailbox_list

    @staticmethod
    def fetch_already_peeked_email_messages(address: str) -> list[dict[str, str]]:
        peeked_email_messages_path = f"Mailboxes\\{address}\\peekedEmailMessages.json"

        try:
            with open(peeked_email_messages_path, 'r') as f:
                already_peeked_messages = json.load(f)
                return already_peeked_messages
        except json.decoder.JSONDecodeError:
            print('JSONDecodeError')

    @staticmethod
    def initialize_empty_data_folder(email_address: str, folder: str):
        with open(f"Mailboxes\\{email_address}\\{folder}.json", 'w') as f:
            json.dump([], f)

    @staticmethod
    def save_letter(email_address: str, folder: str, letter_data: dict[str, str]):
        with open(f"Mailboxes\\{email_address}\\{folder}.json", 'r') as f:
            letter_list = json.load(f)

        with open(f"Mailboxes\\{email_address}\\{folder}.json", 'w') as f:
            letter_list.append(letter_data)
            json.dump(letter_list, f)

    @staticmethod
    def save_current_user_data(email_address: str, password: str, imap_host: str):
        current_user_data = {'email_address': email_address, 'password': password, 'imap_host': imap_host}
        with open('current_user.json', 'w') as f:
            json.dump(current_user_data, f)

    @staticmethod
    def get_current_user_data() -> dict[str, str]:
        with open('current_user.json', 'r') as f:
            current_user_data = json.load(f)
            return current_user_data

    @staticmethod
    def initialize_empty_folders(email_address: str):
        with open(f"Mailboxes\\{email_address}\\inbox.json", 'w') as f:
            json.dump([], f)

        with open(f"Mailboxes\\{email_address}\\sent.json", 'w') as f:
            json.dump([], f)

    @staticmethod
    def add_peeked_letter_data(email_address: str, folder: str, peeked_letter: dict[str, str]):
        f = open(f"Mailboxes\\{email_address}\\{folder}.json", 'r')
        letters = json.load(f)
        f.close()

        letters.append(peeked_letter)
        f = open(f"Mailboxes\\{email_address}\\{folder}.json", 'w')
        json.dump(letters, f)
        f.close()

    @staticmethod
    def get_peeked_email_messages(email_address: str, folder: str) -> list[dict[str, str]]:
        f = open(f"Mailboxes\\{email_address}\\{folder}", 'r')
        peeked_letter_list = json.load(f)
        f.close()

        return peeked_letter_list

    @staticmethod
    def insert_first_letter_data(email_address: str, folder: str, peeked_letter: dict[str, str]):
        f = open(f"Mailboxes\\{email_address}\\{folder}.json", 'r')
        letters = json.load(f)
        f.close()

        letters.insert(0, peeked_letter)
        f = open(f"Mailboxes\\{email_address}\\{folder}.json", 'w')
        json.dump(letters, f)
        f.close()
