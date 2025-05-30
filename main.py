import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QLabel,
    QDialog, QFormLayout, QDialogButtonBox, QWidget, QMessageBox, QComboBox
)
from PyQt6.QtCore import QTimer
from SystemObslugi import SystemObslugi


def validate_pesel(pesel):
    if not pesel.isdigit() or len(pesel) != 11:
        raise ValueError("PESEL musi składać się z 11 cyfr")
    return int(pesel)


class BaseDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def show_notification(self, icon, title, message):
        QMessageBox(icon, title, message, QMessageBox.StandardButton.Ok, self).exec()


class AuthorizationDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Autoryzacja", parent)
        form_layout = QFormLayout()

        self.id_input = QLineEdit(self)
        self.id_input.setPlaceholderText("ID użytkownika")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Hasło")

        form_layout.addRow("ID użytkownika:", self.id_input)
        form_layout.addRow("Hasło:", self.password_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.buttons)

    def get_credentials(self):
        return self.id_input.text(), self.password_input.text()


class ClientRegistrationDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Rejestracja Klienta", parent)
        form_layout = QFormLayout()

        self.imie_input = QLineEdit(self)
        self.nazwisko_input = QLineEdit(self)
        self.wiek_input = QLineEdit(self)
        self.id_klienta_input = QLineEdit(self)

        form_layout.addRow("Imię:", self.imie_input)
        form_layout.addRow("Nazwisko:", self.nazwisko_input)
        form_layout.addRow("Wiek:", self.wiek_input)
        form_layout.addRow("PESEL:", self.id_klienta_input)

        self.submit_button = QPushButton("Zarejestruj", self)
        self.submit_button.clicked.connect(self.submit)

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.submit_button)

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
        form_layout = QFormLayout()

        self.numer_opaski_input = QLineEdit(self)
        self.metoda_platnosci_input = QLineEdit(self)

        form_layout.addRow("Numer seryjny opaski:", self.numer_opaski_input)
        form_layout.addRow("Metoda płatności (gotówka/karta):", self.metoda_platnosci_input)

        self.submit_button = QPushButton("Zakończ wizytę", self)
        self.submit_button.clicked.connect(self.submit)

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.submit_button)

    def submit(self):
        message = self.parent().system.obsluz_wyjscie(
            self.numer_opaski_input.text(), self.metoda_platnosci_input.text().lower()
        )
        self.show_notification(QMessageBox.Icon.Information, "Wyjście klienta", message)
        self.accept()


class ReportDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Generowanie Raportu", parent)
        form_layout = QFormLayout()

        self.typ_raportu_input = QComboBox(self)
        self.typ_raportu_input.addItems(["finansowy", "statystyki"])

        self.data_od_input = QLineEdit(self)
        self.data_od_input.setPlaceholderText("YYYY-MM-DD")
        self.data_do_input = QLineEdit(self)
        self.data_do_input.setPlaceholderText("YYYY-MM-DD")

        form_layout.addRow("Typ raportu:", self.typ_raportu_input)
        form_layout.addRow("Data od:", self.data_od_input)
        form_layout.addRow("Data do:", self.data_do_input)

        self.submit_button = QPushButton("Generuj raport", self)
        self.submit_button.clicked.connect(self.submit)

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.submit_button)

    def submit(self):
        message = self.parent().system.obsluz_raport(
            self.typ_raportu_input.currentText().lower(),
            self.data_od_input.text(),
            self.data_do_input.text(),
        )
        self.show_notification(QMessageBox.Icon.Information, "Raport", message)
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self, screen_geometry):
        super().__init__()
        self.system = SystemObslugi()
        self.system.inicjalizuj_baze_danych()
        self.screen_geometry = screen_geometry # Save for later use
        self.current_layout = None
        self.init_ui(screen_geometry)
        self.init_timer()

    def init_ui(self, screen_geometry):
        self.setWindowTitle("POOLPRO GUI")
        window_width, window_height = 400, 300
        self.setGeometry(
            screen_geometry.width() // 2 - window_width // 2, screen_geometry.height() // 2 - window_height // 2, window_width, window_height
        )
        self.setFixedSize(window_width, window_height)
    
        main_layout = QVBoxLayout()

        # Update current layout
        self.current_layout = main_layout

        self.status_label = QLabel("Witamy w POOLPRO")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(self.status_label)

        self.status_widgets = []
        self.update_status()

        self.zaloguj_button = QPushButton("Zaloguj się")
        self.zaloguj_button.clicked.connect(self.show_auth_dialog)

        main_layout.addStretch(1)
        main_layout.addWidget(self.zaloguj_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)

    def update_status(self):
        if not self.current_layout:
            return

        status = self.system.monitoruj_status()

        for widget in self.status_widgets:
            self.current_layout.removeWidget(widget)
            widget.deleteLater()
        self.status_widgets.clear()

        label_to_friendly_name = {
            "status": "Status systemu",
            "liczba_klientow": "Liczba klientów",
            "aktywne_opaski": "Aktywne opaski",
            "data": "Data",
        }

        for label, value in status.items():
            widget = QLabel(f"{label_to_friendly_name[label] if label_to_friendly_name[label] else label}: {value}", self)
            self.current_layout.insertWidget(1, widget)
            self.status_widgets.append(widget)

    def show_auth_dialog(self):
        dialog = AuthorizationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_id, password = dialog.get_credentials()
            if self.system.zaloguj_uzytkownika(user_id, password):
                self.show_main_menu()
            else:
                self.show_notification(QMessageBox.Icon.Warning, "Błąd logowania", "Nieprawidłowe dane logowania")

    def show_notification(self, icon, title, message):
        QMessageBox(icon, title, message, QMessageBox.StandardButton.Ok, self).exec()

    def show_main_menu(self):
        menu_layout = QVBoxLayout()
        
        # Update current layout
        self.current_layout = menu_layout

        self.status_widgets.clear()
        self.update_status()
        menu_layout.addStretch(1)

        buttons = [
            ("Zarejestruj wejście", self.show_client_registration),
            ("Skanuj opaskę", self.show_checkout_dialog),
            ("Wygeneruj raport", self.show_report_dialog),
            ("Wyloguj", self.logout),
        ]

        for text, handler in buttons:
            button = QPushButton(text, self)
            button.clicked.connect(handler)
            menu_layout.addWidget(button)

        container = QWidget()
        container.setLayout(menu_layout)
        self.setCentralWidget(container)

    def show_client_registration(self):
        ClientRegistrationDialog(self).exec()

    def show_checkout_dialog(self):
        CheckoutDialog(self).exec()

    def show_report_dialog(self):
        ReportDialog(self).exec()

    def logout(self):
        self.system.wyloguj_uzytkownika()
        self.init_ui(self.screen_geometry)
        self.show_notification(QMessageBox.Icon.Information, "Wylogowano", "Pomyślnie wylogowano z systemu")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(app.primaryScreen().availableGeometry())
    window.show()
    sys.exit(app.exec())
