import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
    QDialog, QFormLayout, QWidget, QMessageBox, QComboBox,
    QStackedWidget, QDateEdit, QFrame, QGridLayout, QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt6.QtCore import QTimer, QDate, Qt, QSize
from PyQt6.QtGui import QIcon
from SystemObslugi import SystemObslugi

ACCENT_COLOR = "#2979ff"
BG_COLOR = "#f5f5f5"
CARD_BG = "#ffffff"
TEXT_COLOR = "#333333"
SECONDARY_TEXT = "#757575"


def validate_pesel(pesel):
    if not pesel.isdigit() or len(pesel) != 11:
        raise ValueError("PESEL musi składać się z 11 cyfr")
    return int(pesel)


class ModernButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #1c54b2;
            }}
            QPushButton:pressed {{
                background-color: #0d47a1;
            }}
            QPushButton:disabled {{
                background-color: #bbdefb;
                color: #78909c;
            }}
        """)
        
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))


class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                padding: 8px;
                background-color: {CARD_BG};
                color: {TEXT_COLOR};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {ACCENT_COLOR};
            }}
        """)


class ModernComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                padding: 8px;
                background-color: {CARD_BG};
                color: {TEXT_COLOR};
                font-size: 14px;
            }}
            QComboBox:focus {{
                border: 2px solid {ACCENT_COLOR};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 0px;
            }}
        """)


class DatePickerEdit(QDateEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setDate(QDate.currentDate())
        self.setMinimumHeight(40)
        self.setDisplayFormat("yyyy-MM-dd")
        
        self.setStyleSheet(f"""
            QDateEdit {{
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                padding: 8px;
                background-color: {CARD_BG};
                color: {TEXT_COLOR};
                font-size: 14px;
            }}
            QDateEdit:focus {{
                border: 2px solid {ACCENT_COLOR};
            }}
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 0px;
            }}
        """)


class CardWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        self.setContentsMargins(20, 20, 20, 20)
        
        self.setStyleSheet(f"""
            CardWidget {{
                background-color: {CARD_BG};
                border-radius: 8px;
                border: none;
                margin: 10px;
            }}
        """)

class BaseDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setMinimumWidth(400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_COLOR};
                border-radius: 8px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
            }}
            QLabel#title {{
                font-size: 18px;
                font-weight: bold;
                color: {ACCENT_COLOR};
            }}
        """)

    def show_notification(self, icon, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {BG_COLOR};
                color: {TEXT_COLOR};
            }}
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #1c54b2;
            }}
        """)
        
        return msg_box.exec()


class AuthorizationDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Autoryzacja", parent)
        
        title_label = QLabel("Logowanie do systemu", self)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"margin-bottom: 20px;")
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        self.login_input = ModernLineEdit("Login użytkownika", self)
        self.password_input = ModernLineEdit("Hasło", self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Login:", self.login_input)
        form_layout.addRow("Hasło:", self.password_input)

        button_layout = QHBoxLayout()
        
        self.cancel_button = ModernButton("Anuluj", None, self)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        
        self.login_button = ModernButton("Zaloguj", None, self)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.login_button)
        
        self.cancel_button.clicked.connect(self.reject)
        self.login_button.clicked.connect(self.accept)
        
        form_card = CardWidget(self)
        form_card.setLayout(form_layout)
        
        self.layout.addWidget(title_label)
        self.layout.addWidget(form_card)
        self.layout.addLayout(button_layout)

    def get_credentials(self):
        return self.login_input.text(), self.password_input.text()


class ClientRegistrationDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Rejestracja Klienta", parent)
        
        title_label = QLabel("Nowy klient", self)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        self.imie_input = ModernLineEdit("Imię klienta", self)
        self.nazwisko_input = ModernLineEdit("Nazwisko klienta", self)
        self.wiek_input = ModernLineEdit("Wiek klienta", self)
        self.id_klienta_input = ModernLineEdit("PESEL (11 cyfr)", self)

        form_layout.addRow("Imię:", self.imie_input)
        form_layout.addRow("Nazwisko:", self.nazwisko_input)
        form_layout.addRow("Wiek:", self.wiek_input)
        form_layout.addRow("PESEL:", self.id_klienta_input)

        button_layout = QHBoxLayout()
        self.cancel_button = ModernButton("Anuluj", None, self)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        
        self.submit_button = ModernButton("Zarejestruj", None, self)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.submit_button)
        
        self.cancel_button.clicked.connect(self.reject)
        self.submit_button.clicked.connect(self.submit)
        
        form_card = CardWidget(self)
        form_card.setLayout(form_layout)
        
        self.layout.addWidget(title_label)
        self.layout.addWidget(form_card)
        self.layout.addLayout(button_layout)

    def submit(self):
        try:
            wiek = int(self.wiek_input.text())
            pesel = validate_pesel(self.id_klienta_input.text())
            message = self.parent().system.obsluz_wejscie(
                self.imie_input.text(), self.nazwisko_input.text(), wiek, pesel
            )
            self.show_notification(QMessageBox.Icon.Information, "Rejestracja", message)
            self.accept()
        except ValueError as e:
            self.show_notification(QMessageBox.Icon.Warning, "Błąd", str(e))


class CheckoutDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Wyjście Klienta", parent)
        
        title_label = QLabel("Skanowanie opaski", self)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        self.numer_opaski_input = ModernLineEdit("Numer seryjny opaski", self)
        
        self.metoda_platnosci_input = ModernComboBox(self)
        self.metoda_platnosci_input.addItems(["Gotówka", "Karta"])

        form_layout.addRow("Numer seryjny opaski:", self.numer_opaski_input)
        form_layout.addRow("Metoda płatności:", self.metoda_platnosci_input)

        button_layout = QHBoxLayout()
        self.cancel_button = ModernButton("Anuluj", None, self)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        
        self.submit_button = ModernButton("Zakończ wizytę", None, self)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.submit_button)
        
        self.cancel_button.clicked.connect(self.reject)
        self.submit_button.clicked.connect(self.submit)
        
        form_card = CardWidget(self)
        form_card.setLayout(form_layout)
        
        self.layout.addWidget(title_label)
        self.layout.addWidget(form_card)
        self.layout.addLayout(button_layout)

    def submit(self):
        payment_method = self.metoda_platnosci_input.currentText().lower()
        message = self.parent().system.obsluz_wyjscie(
            self.numer_opaski_input.text(), payment_method
        )
        self.show_notification(QMessageBox.Icon.Information, "Wyjście klienta", message)
        self.accept()


class ReportDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Generowanie Raportu", parent)
        
        title_label = QLabel("Raport", self)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        self.typ_raportu_input = ModernComboBox(self)
        self.typ_raportu_input.addItems(["Finansowy", "Statystyki"])

        self.data_od_input = DatePickerEdit(self)
        self.data_do_input = DatePickerEdit(self)
        
        self.data_do_input.setDate(QDate.currentDate())
        self.data_od_input.setDate(QDate.currentDate().addDays(-30))

        form_layout.addRow("Typ raportu:", self.typ_raportu_input)
        form_layout.addRow("Data od:", self.data_od_input)
        form_layout.addRow("Data do:", self.data_do_input)

        button_layout = QHBoxLayout()
        self.cancel_button = ModernButton("Anuluj", None, self)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        
        self.submit_button = ModernButton("Generuj raport", None, self)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.submit_button)
        
        self.cancel_button.clicked.connect(self.reject)
        self.submit_button.clicked.connect(self.submit)
        
        form_card = CardWidget(self)
        form_card.setLayout(form_layout)
        
        self.layout.addWidget(title_label)
        self.layout.addWidget(form_card)
        self.layout.addLayout(button_layout)

    def submit(self):
        date_from = self.data_od_input.date().toString("yyyy-MM-dd")
        date_to = self.data_do_input.date().toString("yyyy-MM-dd")
        
        message = self.parent().system.obsluz_raport(
            self.typ_raportu_input.currentText().lower(),
            date_from,
            date_to,
        )
        self.show_notification(QMessageBox.Icon.Information, "Raport", message)
        self.accept()

class UserManagementDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Zarządzanie Użytkownikami", parent)
        
        title_label = QLabel("Zarządzanie użytkownikami systemu", self)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Tabela użytkowników
        users_card = CardWidget(self)
        users_layout = QVBoxLayout(users_card)
        
        self.users_table = QTableWidget(0, 5, self)
        self.users_table.setHorizontalHeaderLabels(["ID", "Login", "Imię", "Nazwisko", "Stanowisko"])
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.users_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {CARD_BG};
                color: {TEXT_COLOR};
                border: 1px solid #bdbdbd;
            }}
            QHeaderView::section {{
                background-color: #e0e0e0;
                color: {TEXT_COLOR};
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #bdbdbd;
                padding: 4px;
            }}
            QTableWidget::item {{
                padding: 4px;
            }}
            QTableWidget::item:selected {{
                background-color: {ACCENT_COLOR};
                color: white;
            }}
        """)
        
        users_layout.addWidget(self.users_table)
        
        # Przyciski zarządzania
        table_buttons_layout = QHBoxLayout()
        
        self.delete_button = ModernButton("Usuń użytkownika", None, self)
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #f44336;
                color: white;
            }}
            QPushButton:hover {{
                background-color: #d32f2f;
            }}
        """)
        self.delete_button.clicked.connect(self.delete_user)
        
        self.refresh_button = ModernButton("Odśwież", None, self)
        self.refresh_button.clicked.connect(self.load_users)
        
        table_buttons_layout.addWidget(self.delete_button)
        table_buttons_layout.addWidget(self.refresh_button)
        
        users_layout.addLayout(table_buttons_layout)
        
        # Formularz dodawania nowego użytkownika
        add_user_card = CardWidget(self)
        form_layout = QFormLayout(add_user_card)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        self.login_input = ModernLineEdit("Login użytkownika", self)
        self.password_input = ModernLineEdit("Hasło", self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.imie_input = ModernLineEdit("Imię", self)
        self.nazwisko_input = ModernLineEdit("Nazwisko", self)
        
        self.stanowisko_input = ModernComboBox(self)
        self.stanowisko_input.addItems(["Recepcjonista", "Kierownik"])

        form_layout.addRow("Login:", self.login_input)
        form_layout.addRow("Hasło:", self.password_input)
        form_layout.addRow("Imię:", self.imie_input)
        form_layout.addRow("Nazwisko:", self.nazwisko_input)
        form_layout.addRow("Stanowisko:", self.stanowisko_input)
        
        self.add_button = ModernButton("Dodaj użytkownika", None, self)
        self.add_button.clicked.connect(self.add_user)
        form_layout.addRow("", self.add_button)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.close_button = ModernButton("Zamknij", None, self)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addStretch(1)
        button_layout.addWidget(self.close_button)
        
        # Adding all components to main layout
        self.layout.addWidget(title_label)
        self.layout.addWidget(users_card)
        self.layout.addWidget(add_user_card)
        self.layout.addLayout(button_layout)
        
        self.setMinimumWidth(600)
        
        # Load users when dialog is created
        self.load_users()
    
    def load_users(self):
        """
        Wczytuje użytkowników z bazy danych do tabeli
        """
        users = self.parent().system.pobierz_pracownikow()
        
        self.users_table.setRowCount(0)  # Clear current table
        
        for user in users:
            row_position = self.users_table.rowCount()
            self.users_table.insertRow(row_position)
            
            for col, value in enumerate(user):
                item = QTableWidgetItem(str(value))
                item.setBackground(Qt.GlobalColor.white)
                self.users_table.setItem(row_position, col, item)
                
        # Zaznaczenie aktualnie zalogowanego użytkownika
        current_user_id = self.parent().system.zalogowany_pracownik.identyfikator
        for row in range(self.users_table.rowCount()):
            if int(self.users_table.item(row, 0).text()) == current_user_id:
                for col in range(self.users_table.columnCount()):
                    self.users_table.item(row, col).setBackground(Qt.GlobalColor.lightGray)
    
    def delete_user(self):
        """
        Usuwa wybranego użytkownika
        """
        selected_rows = self.users_table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_notification(
                QMessageBox.Icon.Warning,
                "Brak wyboru",
                "Proszę wybrać użytkownika do usunięcia."
            )
            return
            
        user_id = int(self.users_table.item(selected_rows[0].row(), 0).text())
        
        # Sprawdzenie czy to nie jest zalogowany użytkownik
        if user_id == self.parent().system.zalogowany_pracownik.identyfikator:
            self.show_notification(
                QMessageBox.Icon.Warning,
                "Błąd",
                "Nie można usunąć własnego konta."
            )
            return
            
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("Potwierdź usunięcie")
        msg_box.setText(f"Czy na pewno chcesz usunąć użytkownika {self.users_table.item(selected_rows[0].row(), 2).text()} {self.users_table.item(selected_rows[0].row(), 3).text()}?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            success, message = self.parent().system.usun_pracownika(user_id)
            
            if success:
                self.show_notification(
                    QMessageBox.Icon.Information,
                    "Sukces",
                    message
                )
                self.load_users()  # Odświeżenie tabeli
            else:
                self.show_notification(
                    QMessageBox.Icon.Warning,
                    "Błąd",
                    message
                )
    
    def add_user(self):
        """
        Dodaje nowego użytkownika
        """
        login = self.login_input.text()
        password = self.password_input.text()
        imie = self.imie_input.text()
        nazwisko = self.nazwisko_input.text()
        stanowisko = self.stanowisko_input.currentText()
        
        if not login or not password or not imie or not nazwisko:
            self.show_notification(
                QMessageBox.Icon.Warning,
                "Brak danych",
                "Wszystkie pola są wymagane."
            )
            return
            
        success, message = self.parent().system.dodaj_pracownika(
            login, password, imie, nazwisko, stanowisko
        )
        
        if success:
            self.show_notification(
                QMessageBox.Icon.Information,
                "Sukces",
                message
            )
            # Clear form
            self.login_input.clear()
            self.password_input.clear()
            self.imie_input.clear()
            self.nazwisko_input.clear()
            self.load_users()  # Refresh table
        else:
            self.show_notification(
                QMessageBox.Icon.Warning,
                "Błąd",
                message
            )

class StatusPanel(CardWidget):
    status_keys = ["status", "liczba_klientow", "aktywne_opaski", "data"]
    friendly_names = {
        "status": "Status systemu",
        "liczba_klientow": "Liczba klientów",
        "aktywne_opaski": "Aktywne opaski",
        "data": "Data i czas"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.title_label = QLabel("Status systemu", self)
        self.title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {ACCENT_COLOR};
            background-color: {CARD_BG};
        """)
        
        self.layout.addWidget(self.title_label)
        
        self.status_widgets = {}
        
        for key in self.status_keys:
            label = QLabel(f"{self.friendly_names[key]}: --", self)
            label.setStyleSheet(f"font-size: 14px; background-color: {CARD_BG}; color: {TEXT_COLOR};")
            self.layout.addWidget(label)
            self.status_widgets[key] = label
        
        self.layout.addStretch(1)

    def update_status(self, status_dict):
        for key, value in status_dict.items():
            if key in self.status_widgets:
                friendly_name = self.friendly_names.get(key, key)
                self.status_widgets[key].setText(f"{friendly_name}: {value}")


class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f5f5f5;
                border: none;
                border-radius: 0;
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.2);
                border-left: 4px solid #2979ff;
            }
        """)
        self.setCheckable(True)


class MainWindow(QMainWindow):
    stats_friendly_names = {
        "dzienne_przychody": "Przychód dzienny",
        "miesieczne_przychody": "Przychód miesięczny",
    }

    def __init__(self, screen_geometry):
        super().__init__()
        self.system = SystemObslugi()
        self.system.inicjalizuj_baze_danych()
        self.screen_geometry = screen_geometry
        self.init_ui()
        self.init_timer()

    def init_ui(self):
        self.setWindowTitle("PoolPro")
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BG_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR};
            }}
        """)
        
        window_width = int(self.screen_geometry.width() * 0.8)
        window_height = int(self.screen_geometry.height() * 0.8)
        self.setGeometry(
            self.screen_geometry.width() // 2 - window_width // 2,
            self.screen_geometry.height() // 2 - window_height // 2,
            window_width, window_height
        )
        self.setMinimumSize(800, 600)
        
        self.central_widget = QWidget()
        self.central_layout = QHBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)
        
        self.content_stack = QStackedWidget()
        
        self.create_login_page()
        
        self.create_main_app_page()
        
        self.content_stack.setCurrentIndex(0)
        self.central_layout.addWidget(self.content_stack)

    def create_login_page(self):
        login_page = QWidget()
        login_layout = QVBoxLayout(login_page)
        
        login_card = CardWidget()
        login_card_layout = QVBoxLayout(login_card)
        
        logo_label = QLabel("POOLPRO")
        logo_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #2979ff;
            margin: 20px;
            qproperty-alignment: AlignCenter;
        """)
        
        subtitle = QLabel("System obsługi pływalni")
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #757575;
            margin-bottom: 40px;
            qproperty-alignment: AlignCenter;
        """)
        
        login_button = ModernButton("Zaloguj się", None)
        login_button.clicked.connect(self.show_auth_dialog)
        
        login_card_layout.addWidget(logo_label)
        login_card_layout.addWidget(subtitle)
        login_card_layout.addWidget(login_button)
        
        login_layout.addStretch(2)
        login_layout.addWidget(login_card, alignment=Qt.AlignmentFlag.AlignCenter)
        login_layout.addStretch(3)
        
        self.content_stack.addWidget(login_page)

    def create_main_app_page(self):
        main_page = QWidget()
        main_layout = QHBoxLayout(main_page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            background-color: #2c3e50;
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        logo_container = QWidget()
        logo_container.setStyleSheet("background-color: #1f2d3d; padding: 20px;")
        logo_layout = QVBoxLayout(logo_container)
        
        logo_label = QLabel("POOLPRO")
        logo_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
            qproperty-alignment: AlignLeft;
        """)
        
        logo_layout.addWidget(logo_label)
        sidebar_layout.addWidget(logo_container)
        
        self.menu_buttons = []
        menu_items = [
            ("Pulpit", self.show_dashboard),
            ("Rejestruj wejście", self.show_client_registration),
            ("Skanuj opaskę", self.show_checkout_dialog),
            ("Raporty", self.show_report_dialog),
            ("Zarządzanie użytkownikami", self.show_user_management)
        ]
        
        menu_items.append(("Wyloguj", self.logout))
        
        for text, handler in menu_items:
            button = SidebarButton(text)
            button.clicked.connect(handler)
            sidebar_layout.addWidget(button)
            self.menu_buttons.append(button)
        
        sidebar_layout.addStretch(1)
        
        content_area = QWidget()
        content_area.setStyleSheet(f"background-color: {BG_COLOR};")
        self.content_layout = QVBoxLayout(content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area, 1)
        
        self.content_stack.addWidget(main_page)
        
        self.status_panel = StatusPanel()
        self.status_panel.setMaximumHeight(200)
        self.content_layout.addWidget(self.status_panel)
        
        self.dashboard_stack = QStackedWidget()
        self.content_layout.addWidget(self.dashboard_stack, 1)
        
        # Create and build the dashboard page
        self.create_dashboard_page()

    def create_dashboard_page(self):
        """
        Tworzy stronę z pulpitem dla użytkownika
        """
        dashboard_page = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_page)
        
        welcome_label = QLabel("Witaj w systemie POOLPRO")
        welcome_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0;
            color: #2c3e50;
        """)
        
        stats_grid = QGridLayout()
        
        stats = self.system.pobierz_statystyki()
        item_counter = 0
        for key, value in stats.items():
            title = self.stats_friendly_names.get(key, key)
            card = CardWidget()
            card_layout = QVBoxLayout(card)
            
            title_label = QLabel(title)
            title_label.setStyleSheet(f"font-size: 14px; color: {TEXT_COLOR}; background-color: {CARD_BG};")
            
            value_label = QLabel(f"{value} zł")
            value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {ACCENT_COLOR}; background-color: {CARD_BG};")
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            
            row, col = divmod(item_counter, 2)
            item_counter += 1
            stats_grid.addWidget(card, row, col)
        
        # Add last refresh time indicator
        refresh_label = QLabel(f"Ostatnia aktualizacja: {datetime.now().strftime('%H:%M:%S')}")
        refresh_label.setStyleSheet(f"""
            font-size: 12px; 
            color: {SECONDARY_TEXT}; 
            margin-top: 10px;
            qproperty-alignment: AlignRight;
        """)
        refresh_label.setObjectName("refresh_label")
        
        dashboard_layout.addWidget(welcome_label)
        dashboard_layout.addLayout(stats_grid)
        dashboard_layout.addWidget(refresh_label)
        dashboard_layout.addStretch(1)
        
        self.dashboard_stack.addWidget(dashboard_page)

    def init_timer(self):
        # Timer for status updates (every second)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)
        
        # Timer for statistics updates (every minute)
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(60000)

    def update_status(self):
        if self.status_panel:
            status = self.system.monitoruj_status()
            self.status_panel.update_status(status)
            
    def update_statistics(self):
        # Only update if we're on the dashboard page
        if self.content_stack.currentIndex() == 1 and self.dashboard_stack.currentIndex() == 0:
            self.refresh_dashboard_stats()

    def refresh_dashboard_stats(self):
        """
        Aktualizuje statystyki na pulpicie
        """
        # Get current dashboard page
        dashboard_page = self.dashboard_stack.widget(0)
        if not dashboard_page:
            return
        
        # Look for the stats grid in the layout
        stats_grid = None
        for i in range(dashboard_page.layout().count()):
            item = dashboard_page.layout().itemAt(i)
            if isinstance(item, QGridLayout):
                stats_grid = item
                break
        
        if not stats_grid:
            return
        
        # Get updated statistics
        stats = self.system.pobierz_statystyki()
        
        # Update each card with new data
        for i in range(stats_grid.count()):
            widget_item = stats_grid.itemAt(i)
            if not widget_item:
                continue
                
            card = widget_item.widget()
            if not card or not isinstance(card, CardWidget):
                continue
                
            # Find the key from the card's title label
            card_layout = card.layout()
            for j in range(card_layout.count()):
                title_label = card_layout.itemAt(0).widget()
                value_label = card_layout.itemAt(1).widget()
                
                if not title_label or not value_label:
                    continue
                
                # Find the key by matching the title label text
                found_key = None
                for key, friendly_name in self.stats_friendly_names.items():
                    if title_label.text() == friendly_name:
                        found_key = key
                        break
                
                if found_key and found_key in stats:
                    value_label.setText(f"{stats[found_key]} zł")
                
                break
        
        # Update the refresh timestamp
        for i in range(dashboard_page.layout().count()):
            item = dashboard_page.layout().itemAt(i)
            if item.widget() and item.widget().objectName() == "refresh_label":
                refresh_label = item.widget()
                refresh_label.setText(f"Ostatnia aktualizacja: {datetime.now().strftime('%H:%M:%S')}")
                break

    def show_auth_dialog(self):
        dialog = AuthorizationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            login, password = dialog.get_credentials()
            if self.system.zaloguj_uzytkownika(login, password):
                self.content_stack.setCurrentIndex(1)
                self.menu_buttons[0].setChecked(True)
                self.show_dashboard()
            else:
                self.show_notification(QMessageBox.Icon.Warning, "Błąd logowania", "Nieprawidłowe dane logowania")

    def show_dashboard(self):
        sender = self.sender()
        if sender in self.menu_buttons:
            for button in self.menu_buttons:
                button.setChecked(button == sender)
        
        # If dashboard is already created, refresh it
        if self.dashboard_stack.count() > 0:
            self.refresh_dashboard_stats()
        
        self.dashboard_stack.setCurrentIndex(0)

    def show_notification(self, icon, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {BG_COLOR};
                color: {TEXT_COLOR};
            }}
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #1c54b2;
            }}
        """)
        
        return msg_box.exec()

    def show_client_registration(self):
        sender = self.sender()
        if sender in self.menu_buttons:
            for button in self.menu_buttons:
                button.setChecked(button == sender)
                
        ClientRegistrationDialog(self).exec()

    def show_checkout_dialog(self):
        sender = self.sender()
        if sender in self.menu_buttons:
            for button in self.menu_buttons:
                button.setChecked(button == sender)
                
        CheckoutDialog(self).exec()

    def show_report_dialog(self):
        sender = self.sender()
        if sender in self.menu_buttons:
            for button in self.menu_buttons:
                button.setChecked(button == sender)
                
        ReportDialog(self).exec()

    def show_user_management(self):
        sender = self.sender()
        if sender in self.menu_buttons:
            for button in self.menu_buttons:
                button.setChecked(button == sender)
        
        # Sprawdzamy uprawnienia - tylko kierownik może zarządzać użytkownikami
        if self.system.zalogowany_pracownik and self.system.zalogowany_pracownik.stanowisko == "Kierownik":
            UserManagementDialog(self).exec()
        else:
            self.show_notification(QMessageBox.Icon.Warning, "Brak dostępu", 
                                 "Tylko kierownicy mają dostęp do zarządzania użytkownikami.")

    def logout(self):
        self.system.wyloguj_uzytkownika()
        self.content_stack.setCurrentIndex(0)
        self.show_notification(QMessageBox.Icon.Information, "Wylogowano", "Pomyślnie wylogowano z systemu")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(app.primaryScreen().availableGeometry())
    window.show()
    sys.exit(app.exec())
