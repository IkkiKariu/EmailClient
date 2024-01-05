import imaplib
import sys
from PyQt6 import QtCore, QtWidgets, QtGui

import EmailEncryptor
import EmailSender
import Mailboxes
import config
from Models import EmailMessagesModels
import OutcomingEmailValidator
import EmailFetcher
from email_validate import exceptions
import Mailboxes
from Mailboxes import create_mailbox_files
import webbrowser
import Repository
sizes = {'MainWindow': QtCore.QSize(1920, 1080), 'SideMainMenu': QtCore.QSize(300, 1080)}


def load_already_peeked_email_messages():
    pass


# letters data updating threads
class UpdateIncomingLettersDataThread(QtCore.QThread):
    data_ready = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        current_user_data = Repository.JsonWriter.get_current_user_data()
        appropriate_folder = Mailboxes.get_corresponding_folder(current_user_data['imap_host'], 'inbox')

        peeked_letter_list = Repository.JsonWriter.get_peeked_email_messages(current_user_data['email_address'],
                                                                             'inbox')
        if not peeked_letter_list:
            self.exit()

        newest_peeked_letter_uid = peeked_letter_list[0]['uid']

        imap_conn = EmailFetcher.email_fetcher.establish_login_select(current_user_data['imap_host'],
                                                                      appropriate_folder,
                                                                      current_user_data['email_address'],
                                                                      current_user_data['password'])
        uids_list = EmailFetcher.email_fetcher.get_all_uid(imap_conn)

        new_uid_for_peeking_list = []
        for servers_uid in uids_list:
            if servers_uid <= newest_peeked_letter_uid:
                break
            else:
                new_uid_for_peeking_list.append(servers_uid)

        if not new_uid_for_peeking_list:
            EmailFetcher.email_fetcher.imap_logout(imap_conn)
            self.exit()

        new_uid_for_peeking_list.reverse()

        for uid_for_peeking in new_uid_for_peeking_list:
            letter_data = EmailFetcher.email_fetcher.peek_email_data(imap_conn, uid_for_peeking)
            Repository.JsonWriter.insert_first_letter_data(current_user_data['email_address'], 'inbox', letter_data)
            self.data_ready.emit(letter_data)

        EmailFetcher.email_fetcher.imap_logout(imap_conn)


def start_update_incoming_letters_data_thread():
    main_window.incoming_letters_panel.update_incoming_letters_data_thread.start()


# ---> Letter peeking threads
class PeekAndPrepareIncomingLetterThread(QtCore.QThread):
    data_ready = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        current_user_data = Repository.JsonWriter.get_current_user_data()
        appropriate_folder = Mailboxes.get_corresponding_folder(current_user_data['imap_host'], 'inbox')
        imap_conn = EmailFetcher.email_fetcher.establish_login_select(current_user_data['imap_host'],
                                                                      appropriate_folder,
                                                                      current_user_data['email_address'],
                                                                      current_user_data['password'])

        uids_list = EmailFetcher.email_fetcher.get_all_uid(imap_conn)
        print(uids_list)
        for uid in uids_list:
            letter_data = EmailFetcher.email_fetcher.peek_email_data(imap_conn, uid)
            Repository.JsonWriter.add_peeked_letter_data(current_user_data['email_address'], 'inbox', letter_data)
            self.data_ready.emit(letter_data)

        EmailFetcher.email_fetcher.imap_logout(imap_conn)


class PeekAndPrepareSentLetterThread(QtCore.QThread):
    data_ready = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        current_user_data = Repository.JsonWriter.get_current_user_data()
        appropriate_folder = Mailboxes.get_corresponding_folder(current_user_data['imap_host'], 'sent')

        imap_conn = EmailFetcher.email_fetcher.establish_login_select(current_user_data['imap_host'],
                                                                      appropriate_folder,
                                                                      current_user_data['email_address'],
                                                                      current_user_data['password'])

        uids_list = EmailFetcher.email_fetcher.get_all_uid(imap_conn)
        print(uids_list)
        for uid in uids_list:
            letter_data = EmailFetcher.email_fetcher.peek_email_data(imap_conn, uid)
            Repository.JsonWriter.add_peeked_letter_data(current_user_data['email_address'], 'sent', letter_data)
            self.data_ready.emit(letter_data)

        EmailFetcher.email_fetcher.imap_logout(imap_conn)
# />


def start_incoming_message_peek_thread():
    main_window.incoming_letters_panel.peek_and_prepare_incoming_letter_thread.start()


def start_sent_message_peek_thread():
    main_window.sent_letters_panel.peek_and_prepare_sent_letter_thread.start()


def send_letter(event_arg):
    print('a')


def set_receiver_public_key_visible(checked: bool):
    if checked:
        main_window.new_letter_editor_panel.sending_parameters_subpanel.receiver_public_key_input.setVisible(True)
    else:
        main_window.new_letter_editor_panel.sending_parameters_subpanel.receiver_public_key_input.setVisible(False)


'''def letter_clicked(index: QtCore.QModelIndex):
    model = index.model()
    current_row_logical_index = index.row()

    uid = model.index(current_row_logical_index, 0).data()
    print(uid)
    raw_email_data = EmailFetcher.email_fetcher.fetch_letter_by_uid('imap.gmail.com', 'inbox', config.USER_ADDRESS, config.USER_PASSWORD, uid)
    prepared_email_data = EmailFetcher.email_fetcher.convert_raw_email_data(raw_email_data)
    main_window.letter_detail_panel.display_letter_detail(prepared_email_data)
    main_window.main_content_container.setCurrentIndex(1)'''


def show_managing_mailboxes_panel():
    main_window.main_content_container.setCurrentIndex(3)


def show_new_letter_editor_panel():
    main_window.main_content_container.setCurrentIndex(2)


def show_incoming_letters_panel():
    main_window.main_content_container.setCurrentIndex(0)


def show_sent_letters_panel():
    main_window.main_content_container.setCurrentIndex(4)


def show_settings_panel():
    main_window.main_content_container.setCurrentIndex(5)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        # ---> Config
        self.resize(sizes['MainWindow'])
        self.setWindowTitle('Mail client')
        # self.showFullScreen()
        # />

        # ---> Outer horizontal container
        self.outer_h_container = QtWidgets.QHBoxLayout(self)
        self.outer_h_container.setContentsMargins(0, 0, 0, 0)
        # />

        # ---> SideMainMenu
        self.side_main_menu = SideMainMenu()
        # />

        # ---> IncomingLettersPanel
        self.incoming_letters_panel = LettersPanel('inbox', self)  # may initiate problem, delete self
        self.incoming_letters_panel.peek_and_prepare_incoming_letter_thread.data_ready.connect(self.incoming_letters_panel.add_letter_view)
        # self.incoming_letters_panel.update_incoming_letters_data_thread.data_ready.connect()
        # />

        # ---> SentLettersPanel
        self.sent_letters_panel = LettersPanel('sent', self)
        self.sent_letters_panel.peek_and_prepare_sent_letter_thread.data_ready.connect(self.sent_letters_panel.add_letter_view)
        # />

        # ---> TrashLettersPanel
        self.trash_letter_panel = LettersPanel('trash', self)
        # />

        # ---> SpamLettersPanel
        self.spam_letters_panel = LettersPanel('spam', self)
        # />

        # ---> LetterDetailPanel
        self.letter_detail_panel = LetterDetailPanel(self)
        # />

        # ---> NewLetterEditorPanel
        self.new_letter_editor_panel = NewLetterEditorPanel(self)
        # <---

        # ---> MailboxesManagingPanel
        self.managing_mailboxes_panel = ManagingMailboxesPanel(self)
        # <---

        # ---> SettingsPanel
        self.settings_panel = SettingsPanel(self)
        # />

        # ---> SideMainMenu container
        self.side_main_menu_container = QtWidgets.QVBoxLayout()
        self.side_main_menu_container.setContentsMargins(0, 0, 0, 0)
        self.side_main_menu_container.addWidget(self.side_main_menu)
        self.outer_h_container.addLayout(self.side_main_menu_container)
        # />

        # ---> Main content container implemented by QStackedLayout
        self.main_content_container = QtWidgets.QStackedLayout()
        self.main_content_container.setContentsMargins(0, 0, 0, 0)
        self.main_content_container.addWidget(self.incoming_letters_panel)
        self.main_content_container.addWidget(self.letter_detail_panel)
        self.main_content_container.addWidget(self.new_letter_editor_panel)
        self.main_content_container.addWidget(self.managing_mailboxes_panel)
        self.main_content_container.addWidget(self.sent_letters_panel)
        self.main_content_container.addWidget(self.settings_panel)
        self.main_content_container.currentChanged.connect(
            lambda: self.clear_letter_details(self.main_content_container.currentIndex()))
        self.side_main_menu.inbox.clicked.connect(show_incoming_letters_panel)
        self.side_main_menu.mail.clicked.connect(show_new_letter_editor_panel)
        self.side_main_menu.outcome.clicked.connect(show_sent_letters_panel)

        self.main_content_container.setCurrentIndex(3)

        self.outer_h_container.addLayout(self.main_content_container)
        # />

    def clear_letter_details(self, current_index):
        if current_index != 1:
            self.letter_detail_panel.body_area.clear()

            self.letter_detail_panel.letter_decryption_section.setVisible(False)


class SideMainMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        # ---> Config
        self.move(QtCore.QPoint())
        # self.setFixedSize(sizes['SideMainMenu'])
        self.setContentsMargins(0, 0, 0, 0)
        # self.hide()
        # />

        # ---> Menu items
        self.mail = MainMenuItemButton()
        self.mail.setText('Написать')
        self.mail.setFixedHeight(60)

        self.inbox = MainMenuItemButton()
        self.inbox.setText('Входящие')

        self.outcome = MainMenuItemButton()
        self.outcome.setText('Исходящие')

        self.drafts = MainMenuItemButton()
        self.drafts.setText('Черновики')

        self.archive = MainMenuItemButton()
        self.archive.setText('Архив')

        self.accounts_btn = MainMenuItemButton('Аккаунты')
        self.accounts_btn.setFixedHeight(60)
        # self.accounts_btn.clicked.connect(start_thread)
        self.accounts_btn.clicked.connect(show_managing_mailboxes_panel)

        self.settings_btn = MainMenuItemButton("Настройки")
        self.settings_btn.clicked.connect(show_settings_panel)

        self.mailbox_button_1 = MainMenuMailboxButton(self)
        self.mailbox_button_1.setVisible(False)
        self.mailbox_button_2 = MainMenuMailboxButton(self)
        self.mailbox_button_2.setVisible(False)
        self.mailbox_button_3 = MainMenuMailboxButton(self)
        self.mailbox_button_3.setVisible(False)
        self.mailbox_button_4 = MainMenuMailboxButton(self)
        self.mailbox_button_4.setVisible(False)
        self.mailbox_button_5 = MainMenuMailboxButton(self)
        self.mailbox_button_5.setVisible(False)

        self.mailbox_buttons = [self.mailbox_button_1, self.mailbox_button_2, self.mailbox_button_3, self.mailbox_button_4, self.mailbox_button_5]
        # />

        # ---> App sections container
        self.app_sections_container = QtWidgets.QVBoxLayout()
        self.setContentsMargins(0, 0, 0, 0)
        self.app_sections_container.addWidget(self.mail)
        self.app_sections_container.addWidget(self.inbox)
        self.app_sections_container.addWidget(self.outcome)
        self.app_sections_container.addWidget(self.drafts)
        self.app_sections_container.addWidget(self.archive)
        # />

        # ---> mailbox selection container
        self.mailbox_selection_container = QtWidgets.QVBoxLayout()
        self.mailbox_selection_container.setContentsMargins(0, 0, 0, 0)
        self.mailbox_selection_container.addWidget(self.settings_btn)
        self.mailbox_selection_container.addWidget(self.accounts_btn)
        # />

        # ---> Menu items container
        self.menu_items_container = QtWidgets.QVBoxLayout(self)
        self.menu_items_container.addSpacing(self.mail.height())
        self.menu_items_container.addLayout(self.app_sections_container)
        self.menu_items_container.addSpacing(self.height())
        self.menu_items_container.addLayout(self.mailbox_selection_container)
        # />

    def add_mailbox_button(self, email_address: str):
        # print(email_address)
        self.mailbox_buttons[config.MAILBOX_COUNT].setText(email_address)
        self.mailbox_selection_container.addWidget(self.mailbox_buttons[config.MAILBOX_COUNT])
        self.mailbox_buttons[config.MAILBOX_COUNT].setVisible(True)
        self.mailbox_buttons[config.MAILBOX_COUNT].clicked.connect(
            lambda: self.set_current_account(email_address))
        config.MAILBOX_COUNT += 1
        self.mailbox_buttons[config.MAILBOX_COUNT].setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

    def load_existing_mailboxes(self):
        mailbox_list = Mailboxes.load_mailboxes()
        for mailbox in mailbox_list:
            self.add_mailbox_button(mailbox)

    def set_current_account(self, email_address: str):
        appropriate_imap_host = Mailboxes.get_appropriate_imap_host(email_address)
        creds = Mailboxes.get_account_credentials(email_address)
        Repository.JsonWriter.save_current_user_data(creds['address'], creds['password'], appropriate_imap_host)


class MainMenuItemButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)

        # self.setMaximumSize(240, 70)
        self.setMinimumSize(200, 40)


class MainMenuMailboxButton(MainMenuItemButton):
    def __init__(self, parent=None):
        MainMenuItemButton.__init__(self, parent)


class LettersPanel(QtWidgets.QWidget):
    def __init__(self, folder: str, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        # self.setFixedSize(sizes['MainWindow'].width() - sizes['SideMainMenu'].width(), sizes['MainWindow'].height())
        self.move(QtCore.QPoint())
        self.setContentsMargins(0, 0, 0, 0)

        self._folder = folder

        # ---> Threads
        self.peek_and_prepare_incoming_letter_thread = PeekAndPrepareIncomingLetterThread()

        self.peek_and_prepare_sent_letter_thread = PeekAndPrepareSentLetterThread()

        self.update_incoming_letters_data_thread = UpdateIncomingLettersDataThread()
        # />

        self.outer_container = QtWidgets.QVBoxLayout(self)

        self.table_view = QtWidgets.QTableView(self)
        self.table_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                                       QtWidgets.QSizePolicy.Policy.Expanding)
        self.table_view.setSizePolicy(self.table_size_policy)

        self.item_model = QtGui.QStandardItemModel(parent=self)
        self.item_model.setHorizontalHeaderLabels(['UID', 'Отправитель', 'Адресат', 'Тема', 'Дата', 'Время'])

        self.table_view.setModel(self.item_model)

        for i in range(self.item_model.rowCount()):
            self.table_view.setRowHeight(i, 50)

        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table_view.horizontalHeader().setSectionsClickable(False)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.table_view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.clicked.connect(self.letter_clicked)
        #self.table_view.doubleClicked.connect(letter_clicked)
        self.table_view.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.outer_container.addWidget(self.table_view)

    def letter_clicked(self, index: QtCore.QModelIndex):
        model = index.model()
        current_row_logical_index = index.row()

        uid = model.index(current_row_logical_index, 0).data()
        print(uid)

        current_user_data = Repository.JsonWriter.get_current_user_data()
        appropriate_folder = config.CORRESPONDING_FOLDERS[current_user_data['imap_host']][self._folder]
        imap_conn = EmailFetcher.email_fetcher.establish_login_select(current_user_data['imap_host'], appropriate_folder,
                                                                      current_user_data['email_address'],
                                                                      current_user_data['password'])
        raw_email_data = EmailFetcher.email_fetcher.fetch_letter_by_uid(imap_conn, uid)
        prepared_email_data = EmailFetcher.email_fetcher.convert_raw_email_data(raw_email_data)
        EmailFetcher.email_fetcher.imap_logout(imap_conn)

        main_window.letter_detail_panel.display_letter_detail(prepared_email_data)
        main_window.main_content_container.setCurrentIndex(1)

    def add_letter_view(self, letter_data: dict[str, str]):
        subject = QtGui.QStandardItem(letter_data["Subject"])
        date = QtGui.QStandardItem(letter_data["Date"])
        sender = QtGui.QStandardItem(letter_data["Sender"])
        uid = QtGui.QStandardItem(letter_data['uid'])
        time = QtGui.QStandardItem(letter_data['Time'])
        receiver = QtGui.QStandardItem(letter_data['Receiver'])
        self.item_model.appendRow([uid, sender, receiver, subject, date, time])

        for i in range(self.item_model.rowCount()):
            self.table_view.setRowHeight(i, 50)

        # print(letter_data.values())

    def folder(self):
        return self._folder


class LetterItemView(QtWidgets.QAbstractItemView):
    def __init__(self, parent=None):
        QtWidgets.QAbstractItemView.__init__(self, parent)

        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)


class LetterDetailPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.move(QtCore.QPoint())
        self.setStyleSheet(" {border: 1px solid black;}")

        self.letter_decryption_section = LetterDecryptionSection(self)

        self.toolbar = LetterDetailToolBar(self)

        self.sender_area = LetterSenderLabel(self)

        self.subject_area = LetterSubjectLabel(self)

        self.body_area = LetterEditPanel(self)
        self.body_area.anchorClicked.connect(self.go)

        self.body_area_container = QtWidgets.QVBoxLayout(self)

        self.body_area_container.addWidget(self.toolbar)
        self.body_area_container.addWidget(self.letter_decryption_section)
        self.body_area_container.addWidget(self.sender_area)
        self.body_area_container.addWidget(self.subject_area)
        self.body_area_container.addWidget(self.body_area)

    def display_letter_detail(self, letter: EmailMessagesModels.IncomingEmailMessage):
        plain_text = letter.plain_text()
        html_text = letter.html_text()
        self.sender_area.setText(f"От: {letter.sender()}")
        self.subject_area.setText(f"Тема: {letter.subject()}")
        # print(html_text)
        # print(plain_text)
        '''if html_text != None:
            self.body_area.setHtml(letter.html_text())'''
        if plain_text != None:
            self.body_area.setText(plain_text)
        if letter.is_ik_encrypted():
            self.letter_decryption_section.setVisible(True)

    def go(self, resource: QtCore.QUrl):
        webbrowser.open(resource.url())


class LetterDetailToolBar(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        QtWidgets.QToolBar.__init__(self, parent)
        self.setIconSize(QtCore.QSize(40, 40))

        self.move_to_trashbox_action1 = QtGui.QAction(QtGui.QIcon('icons/letterDetailToolbarIcons/trashbox.png'),
                                                      'Remove', self)
        '''self.move_to_trashbox_action2 = QtGui.QAction(QtGui.QIcon('icons/letterDetailToolbarIcons/trashbox.png'),
                                                      'Remove', self)
        self.move_to_trashbox_action3 = QtGui.QAction(QtGui.QIcon('icons/letterDetailToolbarIcons/trashbox.png'),
                                                      'Remove', self)
        self.move_to_trashbox_action4 = QtGui.QAction(QtGui.QIcon('icons/letterDetailToolbarIcons/trashbox.png'),
                                                      'Remove', self)
        self.move_to_trashbox_action5 = QtGui.QAction(QtGui.QIcon('icons/letterDetailToolbarIcons/trashbox.png'),
                                                      'Remove', self)
        self.move_to_trashbox_action6 = QtGui.QAction(QtGui.QIcon('icons/letterDetailToolbarIcons/trashbox.png'),
                                                      'Remove', self)'''

        self.addAction(self.move_to_trashbox_action1)
        self.addSeparator()
        '''self.addAction(self.move_to_trashbox_action2)
        self.addSeparator()
        self.addAction(self.move_to_trashbox_action3)
        self.addSeparator()
        self.addAction(self.move_to_trashbox_action4)
        self.addSeparator()
        self.addAction(self.move_to_trashbox_action5)
        self.addSeparator()
        self.addAction(self.move_to_trashbox_action6)
        self.addSeparator()'''


class LetterDecryptionSection(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

        self.info_label = QtWidgets.QLabel(self)
        self.info_label.setStyleSheet("QLabel {color: green}")
        self.info_label.setText("Письмо было зашифровано. "
                                "Загрузите соответствующий приватный ключ чтобы расшифровать письмо")

        self.load_private_key_btn = QtWidgets.QPushButton(self)
        self.load_private_key_btn.setText("Загрузить приватный ключ")
        self.load_private_key_btn.clicked.connect(self.decrypt_message)

        self.h_container = QtWidgets.QHBoxLayout()
        self.h_container.addWidget(self.info_label)
        self.h_container.addWidget(self.load_private_key_btn)

        self.setVisible(False)

        self.setLayout(self.h_container)

    def decrypt_message(self):
        path_to_private_key = QtWidgets.QFileDialog.getOpenFileName(self, "Загрузить приватный ключ",
                                                                    filter="PEM File (*.pem)")[0]
        try:
            decrypted_letter = EmailEncryptor.EmailEncryptor.decrypt_message(path_to_private_key)
            main_window.letter_detail_panel.body_area.clear()
            main_window.letter_detail_panel.body_area.setText(decrypted_letter)
            main_window.letter_detail_panel.letter_decryption_section.setVisible(False)
        except:
            pass


class LetterEditPanel(QtWidgets.QTextBrowser):
    def __init__(self, parent=None):
        QtWidgets.QTextEdit.__init__(self, parent)
        self.setOpenLinks(False)


class LetterSubjectLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)


class LetterSenderLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)


# ----------------------------------------------------
class NewLetterEditorPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.new_letter_receiver_label = NewLetterReceiverLabel()
        self.new_letter_receiver_input = NewLetterReceiverInput()

        self.new_letter_subject_label = NewLetterSubjectLabel()
        self.new_letter_subject_input = NewLetterSubjectInput()

        self.new_letter_text_label = NewLetterTextLabel()
        self.new_letter_text_editor = NewLetterTextEditor()

        self.sending_parameters_subpanel = SendingParametersSubpanel(self)
        self.sending_parameters_subpanel.send_btn.clicked.connect(self.send_letter)

        self.form_layout = QtWidgets.QFormLayout()

        self.form_layout.addRow(self.new_letter_receiver_label, self.new_letter_receiver_input)
        self.form_layout.addRow(self.new_letter_subject_label, self.new_letter_subject_input)
        self.form_layout.addRow(self.new_letter_text_label, self.new_letter_text_editor)

        self.sending_parameters_container = QtWidgets.QVBoxLayout()
        self.sending_parameters_container.addWidget(self.sending_parameters_subpanel)

        self.h_container = QtWidgets.QHBoxLayout()
        self.h_container.addLayout(self.form_layout)
        self.h_container.addLayout(self.sending_parameters_container)

        self.setLayout(self.h_container)

    def ValidateEmailAdderssInput(self) -> str:
        address = self.new_letter_receiver_input.text()

        try:
            OutcomingEmailValidator.EmailAddressValidator.check_address(address)
        except exceptions.AddressFormatError:
            self.sending_parameters_subpanel.address_format_error.setVisible(True)
            return 'BAD'
        except exceptions.SMTPError:
            self.sending_parameters_subpanel.address_existence_error.setVisible(True)
            return 'BAD'
        except exceptions.DNSError:
            self.sending_parameters_subpanel.address_domain_error.setVisible(True)
            return 'BAD'

        return 'OK'

    def send_letter(self, event_arg):
        if self.sending_parameters_subpanel.address_format_error.isVisible():
            self.sending_parameters_subpanel.address_format_error.setVisible(False)

        if self.sending_parameters_subpanel.address_existence_error.isVisible():
            self.sending_parameters_subpanel.address_existence_error.setVisible(False)

        if self.sending_parameters_subpanel.address_domain_error.isVisible():
            self.sending_parameters_subpanel.address_domain_error.setVisible(False)

        if self.sending_parameters_subpanel.body_text_error_label.isVisible():
            self.sending_parameters_subpanel.body_text_error_label.setVisible(False)

        if self.sending_parameters_subpanel.encryption_error_label.isVisible():
            self.sending_parameters_subpanel.encryption_error_label.setVisible(False)

        if self.sending_parameters_subpanel.public_key_error.isVisible():
            self.sending_parameters_subpanel.public_key_error.setVisible(False)

        if self.sending_parameters_subpanel.public_key_is_not_loaded_label.isVisible():
            self.sending_parameters_subpanel.public_key_is_not_loaded_label.setVisible(False)

        validator_response = self.ValidateEmailAdderssInput()
        if validator_response != 'OK':
            return

        receiver_address = self.new_letter_receiver_input.text()
        print(f"receiver_address: {receiver_address}")
        subject = self.new_letter_subject_input.text()
        print(f"subject: {subject}")
        body_text = self.new_letter_text_editor.toPlainText()
        print(f"body_text: {body_text}")

        encryption_requirement = self.sending_parameters_subpanel.encrypt_checkbox.checkState()
        print(encryption_requirement)

        if len(subject) == 0:
            subject = '(без темы)'

        if len(body_text) != 0:
            current_user = Repository.JsonWriter.get_current_user_data()
            sender_address = current_user["email_address"]
            sender_password = current_user["password"]
            sender_smtp_host = Mailboxes.get_appropriate_smtp_host(sender_address)
            sender_smtp_port = config.SMTP_PORTS[sender_smtp_host]

            smtp_conn = EmailSender.email_sender.establish_login_smtp(sender_smtp_host, sender_smtp_port,
                                                                      sender_address, sender_password)

            prepared_email_message = EmailSender.email_sender.compose_email_message(sender_address,
                                                                                    receiver_address,
                                                                                    subject=subject,
                                                                                    body_text=body_text)

            if encryption_requirement == QtCore.Qt.CheckState.Checked:
                if self.sending_parameters_subpanel.public_key_path != None and self.sending_parameters_subpanel.public_key_path[0] != '':
                    prepared_email_message = EmailSender.email_sender.compose_email_message(sender_address,
                                                                                            receiver_address,
                                                                                            subject=subject)

                    try:
                        EmailEncryptor.EmailEncryptor.encrypt_data(body_text,
                                                                   self.sending_parameters_subpanel.public_key_path[0])

                        with open(f"SendingEmailData\\EncryptedMessage\\encrypted_data.bin", "rb") as file:
                            encrypted_message = file.read()

                        prepared_email_message.add_attachment(encrypted_message, maintype='application',
                                                              subtype='octet-stream', filename='encrypted_data.bin')
                        prepared_email_message["X-IK-Encrypted"] = "True"
                    except:
                        self.sending_parameters_subpanel.encryption_error_label.setVisible(True)
                        return
                else:
                    self.sending_parameters_subpanel.public_key_is_not_loaded_label.setVisible(True)
                    return
            else:
                print("unchecked")

            EmailSender.email_sender.send_email(smtp_conn, prepared_email_message)
            EmailSender.email_sender.close_smtp_connection(smtp_conn)
        else:
            self.sending_parameters_subpanel.body_text_error_label.setVisible(True)


class NewLetterReceiverLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        self.setText('Кому:')


class NewLetterReceiverInput(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)

        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)


class NewLetterSubjectLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        self.setText('Тема:')


class NewLetterSubjectInput(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)

        self.setText('Невероятно интересная тема')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)


class NewLetterTextLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        self.setText('Текст:')


class NewLetterTextEditor(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        QtWidgets.QTextEdit.__init__(self, parent)

        self.setMinimumWidth(800)


class SendingParametersSubpanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Maximum))
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)

        self.encrypt_checkbox = EncryptCheckBox(self)
        self.encrypt_checkbox.toggled.connect(set_receiver_public_key_visible)

        self.encryption_error_label = EncryptionError(self)

        self.receiver_public_key_input = ReceiverPublicKeyInput()
        self.receiver_public_key_input.clicked.connect(self.receiver_public_key_input.load_public_key)

        self.public_key_error = PublicKeyError(self)
        self.public_key_is_not_loaded_label = PublicKeyIsNotLoaded(self)

        self.encryption_section = QtWidgets.QHBoxLayout()
        self.encryption_section.addWidget(self.encrypt_checkbox)
        self.encryption_section.addWidget(self.receiver_public_key_input)

        self.address_format_error = AddressFormatErrorLabel(self)
        self.address_existence_error = AddressExistenceErrorLabel(self)
        self.address_domain_error = AddressDomainErrorLabel(self)

        self.body_text_error_label = BodyTextIsNotComposedError(self)

        self.errors_section = QtWidgets.QVBoxLayout()
        self.errors_section.addWidget(self.address_format_error)
        self.errors_section.addWidget(self.address_existence_error)
        self.errors_section.addWidget(self.address_domain_error)
        self.errors_section.addWidget(self.public_key_error)
        self.errors_section.addWidget(self.public_key_is_not_loaded_label)
        self.errors_section.addWidget(self.encryption_error_label)
        self.errors_section.addWidget(self.body_text_error_label)

        self.send_btn = QtWidgets.QPushButton(self)
        self.send_btn.setText('Отправить')

        self.send_container = QtWidgets.QHBoxLayout()
        self.send_container.addWidget(self.send_btn)

        self.v_container = QtWidgets.QVBoxLayout()
        self.v_container.addLayout(self.errors_section)
        self.v_container.addLayout(self.encryption_section)
        self.v_container.addLayout(self.send_container)

        self.public_key_path = None

        self.setLayout(self.v_container)


class EncryptCheckBox(QtWidgets.QCheckBox):
    def __init__(self, parent=None):
        QtWidgets.QCheckBox.__init__(self, parent)

        self.setTristate(False)
        self.setText('Шифрование')


class ReceiverPublicKeyInput(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)

        self.setText('Загрузить публичный ключ')
        self.setVisible(False)

    def load_public_key(self):
        res = QtWidgets.QFileDialog.getOpenFileName(self, "Load public key", filter="PEM File (*.pem)")
        print(res)
        main_window.new_letter_editor_panel.sending_parameters_subpanel.public_key_path = res


class ErrorLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        self.setStyleSheet('color: red;')


class AddressFormatErrorLabel(ErrorLabel):
    def __init__(self, parent=None):
        ErrorLabel.__init__(self, parent)

        self.setText('Ошибка формата адреса: неверный формат адреса!')
        self.setVisible(False)


class AddressExistenceErrorLabel(ErrorLabel):
    def __init__(self, parent=None):
        ErrorLabel.__init__(self, parent)

        self.setText('Ошибка действительности адреса: данный адрес не существует!')
        self.setVisible(False)


class AddressDomainErrorLabel(ErrorLabel):
    def __init__(self, parent=None):
        ErrorLabel.__init__(self, parent)

        self.setText('Ошибка адреса: невалидный домен!')
        self.setVisible(False)


class EncryptionError(ErrorLabel):
    def __init__(self, parent=None):
        ErrorLabel.__init__(self, parent)

        self.setText('Ошибка шифрования!')
        self.setVisible(False)


class PublicKeyError(ErrorLabel):
    def __init__(self, parent=None):
        ErrorLabel.__init__(self, parent)

        self.setText('Ошибка шифрования: невалидный публичный ключ!')
        self.setVisible(False)


class PublicKeyIsNotLoaded(ErrorLabel):
    def __init__(self, parent=None):
        ErrorLabel.__init__(self, parent)

        self.setText('Ошибка шифрования: загрузите публичный ключ адресата письма!')
        self.setVisible(False)


class BodyTextIsNotComposedError(ErrorLabel):
    def __init__(self, parent=None):
        ErrorLabel.__init__(self, parent)

        self.setText('Ошибка содержимого письма: напишите текст письма!')
        self.setVisible(False)


class ManagingMailboxesPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.email_address_label = EmailAddressLabel(self)
        self.email_address_input = EmailAddressInput(self)

        self.password_label = PasswordLabel(self)
        self.password_input = PasswordInput(self)

        self.add_mailbox_button = AddMailboxButton(self)
        self.add_mailbox_button.clicked.connect(self.add_mailbox)

        # self.form_layout = QtWidgets.QFormLayout()
        # self.form_layout.addRow(self.email_address_label, self.email_address_input)
        # self.form_layout.addRow(self.password_label, self.password_input)

        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.addWidget(self.email_address_label, 0, 0)
        self.grid_layout.addWidget(self.email_address_input, 0, 1)

        # self.email_address_error_label = QtWidgets.QLabel(self)
        # self.email_address_error_label.setText('Ошибка')
        # self.email_address_error_label.setFixedSize(200, 20)
        # self.grid_layout.addWidget(self.email_address_error_label, 0, 2)

        self.grid_layout.addWidget(self.password_label, 1, 0)
        self.grid_layout.addWidget(self.password_input, 1, 1)

        self.grid_layout.addWidget(self.add_mailbox_button, 2, 1)

        self.v_container = QtWidgets.QVBoxLayout()
        self.v_container.setContentsMargins(50, 50, 50, 50)
        # self.v_container.addLayout(self.form_layout)
        self.v_container.addLayout(self.grid_layout)
        # self.v_container.addWidget(self.add_mailbox_button)

        self.setLayout(self.v_container)

    def check_credentials(self, email_address, password):
        appropriate_imap_host = Mailboxes.get_appropriate_imap_host(email_address)

        try:
            imap_conn = imaplib.IMAP4_SSL(appropriate_imap_host)
            imap_conn.login(email_address, password)
            imap_conn.select('inbox')
            imap_conn.logout()
            return 'OK'
        except:
            return "BAD"

    def ValidateEmailAdderssInput(self, address: str) -> str:
        try:
            OutcomingEmailValidator.EmailAddressValidator.check_address(address)
        except exceptions.AddressFormatError:
            return 'BAD'
        except exceptions.SMTPError:
            return 'BAD'
        except exceptions.DNSError:
            return 'BAD'

        return 'OK'

    def add_mailbox(self):
        address = self.email_address_input.text()
        password = self.password_input.text()

        # проверка добавлен ли аккаунт на данный момент
        already_added_accounts = Mailboxes.get_mailbox_directories()
        if address in already_added_accounts:
            print("Данный аккаунт уже добавлен")
            return

        # проверка поддерживается ли почтовый сервис
        host = Mailboxes.get_appropriate_imap_host(address)
        if host not in ['imap.gmail.com', 'imap.yandex.ru']:
            return

        # проверка действительности аккаунта
        resp = self.ValidateEmailAdderssInput(address)
        if resp != 'OK':
            return

        # проверка учётных данных
        result = self.check_credentials(address, password)
        if result != 'OK':
            return

        Repository.JsonWriter.save_current_user_data(address, password, host)
        create_mailbox_files(address, password)
        Repository.JsonWriter.initialize_empty_folders(address)

        main_window.side_main_menu.add_mailbox_button(address)

        '''rows = main_window.incoming_letters_panel.item_model.rowCount()
        columns = main_window.incoming_letters_panel.item_model.columnCount()
        for row in range(rows):
            for column in range(columns):
                index = main_window.incoming_letters_panel.item_model.index(row, column)
                main_window.incoming_letters_panel.item_model.clearItemData(index)'''

        start_incoming_message_peek_thread()
        start_sent_message_peek_thread()


class EmailAddressLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        self.setText('Адрес:')


class EmailAddressInput(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)

        self.setPlaceholderText('example@domain.com')


class PasswordLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        self.setText('Пароль:')


class PasswordInput(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)


class AddMailboxButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)

        self.setText('Добавить')


class SettingsPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.encryption_section = SettingsEncryptionSection(self)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.encryption_section, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)


class SettingsEncryptionSection(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setFixedSize(600, 400)

        self.generate_keys_btn = QtWidgets.QPushButton(self)
        self.generate_keys_btn.setText('Сгенерировать ключи шифрования')
        self.generate_keys_btn.clicked.connect(self.generate_key_pair)

        # self.description_label = DescriptionLabel(self)

        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.addWidget(self.generate_keys_btn, 1, 2, 1, 1)
        # self.grid_layout.addWidget(self.description_label, 2, 1, 1, 3)

        self.setLayout(self.grid_layout)

    def generate_key_pair(self):
        path = QtWidgets.QFileDialog.getExistingDirectory()
        print(path)

        if len(path) > 0:
            EmailEncryptor.EmailEncryptor.generate_key_pair(path)


class DescriptionLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        self.setText('A\nB\nC')
        self.setStyleSheet("QLabel {background-color: darkgray; border: 1px solid gray;}")


# ---------------------------------------------------------------------------------
q_app = QtWidgets.QApplication(sys.argv)

main_window = MainWindow()
main_window.side_main_menu.load_existing_mailboxes()
main_window.show()

letter_detail_panel = LetterDetailPanel()

q_app.exec()
