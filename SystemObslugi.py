import random
import sqlite3
from datetime import datetime, timedelta
import os
import bcrypt

from classes.Klient import *
from classes.OpaskaNFC import *
from classes.Raport import *
from classes.Recepcjonista import *
from classes.Transakcja import *

class SystemObslugi:
    def __init__(self):
        self.wersja_systemu = "1.0"
        self.status_systemu = "aktywny"
        self.conn = None
        self.zalogowany_pracownik = None

    def zaloguj_uzytkownika(self, identyfikator, haslo):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Pracownik WHERE identyfikator = ?", (identyfikator,))
        pracownik = cursor.fetchone()
        if pracownik:
            if self.weryfikuj_haslo(haslo, pracownik[1]):
                self.zalogowany_pracownik = Recepcjonista(
                    pracownik[0], pracownik[2], pracownik[3], pracownik[4]
                )
                return True
        return False
    
    def szyfruj_haslo(self, haslo):
        return bcrypt.hashpw(haslo.encode('utf-8'), bcrypt.gensalt())
    
    def weryfikuj_haslo(self, haslo, zaszyfrowane_haslo):
        return bcrypt.checkpw(haslo.encode('utf-8'), zaszyfrowane_haslo)

    def wyloguj_uzytkownika(self):
        self.zalogowany_pracownik = None
        return True

    def monitoruj_status(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Klient")
        liczba_klientow = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Opaska WHERE czasWyjscia IS NULL")
        aktywne_opaski = cursor.fetchone()[0]
        return {
            "status": self.status_systemu,
            "liczba_klientow": liczba_klientow,
            "aktywne_opaski": aktywne_opaski,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def inicjalizuj_baze_danych(self):
        if os.path.exists('baza_danych.db'):
            os.remove('baza_danych.db')
        self.conn = sqlite3.connect('baza_danych.db')
        self._utworz_tabele()
        self._dodaj_przykladowe_dane()

    def _utworz_tabele(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Klient (
            identyfikator INTEGER PRIMARY KEY,
            imie TEXT NOT NULL,
            nazwisko TEXT NOT NULL,
            wiek INTEGER NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pracownik (
            identyfikator INTEGER PRIMARY KEY AUTOINCREMENT,
            haslo TEXT NOT NULL,
            imie TEXT NOT NULL,
            nazwisko TEXT NOT NULL,
            stanowisko TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Opaska (
            numerSeryjny INTEGER PRIMARY KEY,
            czasWejscia TEXT,
            czasWyjscia TEXT,
            klient_id INTEGER,
            FOREIGN KEY (klient_id) REFERENCES Klient(identyfikator)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Transakcja (
            identyfikatorTransakcji INTEGER PRIMARY KEY AUTOINCREMENT,
            kwota REAL NOT NULL,
            data TEXT NOT NULL,
            metodaPlatnosci TEXT NOT NULL,
            klient_id INTEGER,
            pracownik_id INTEGER,
            FOREIGN KEY (klient_id) REFERENCES Klient(identyfikator),
            FOREIGN KEY (pracownik_id) REFERENCES Pracownik(identyfikator)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Raport (
            identyfikatorRaportu INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            typRaportu TEXT NOT NULL,
            pracownik_id INTEGER,
            FOREIGN KEY (pracownik_id) REFERENCES Pracownik(identyfikator)
        );
        """)
        self.conn.commit()

    def _dodaj_przykladowe_dane(self):
        cursor = self.conn.cursor()

        cursor.execute("INSERT INTO Pracownik (identyfikator, haslo, imie, nazwisko, stanowisko) VALUES (?, ?, ?, ?, ?)", (1, self.szyfruj_haslo("piotr123"), "Piotr", "Zielinski", "Recepcjonista"))

        pesele = [self.generuj_testowy_pesel() for _ in range(5)]
        for i in range(1, 6):
            cursor.execute("INSERT INTO Klient (identyfikator, imie, nazwisko, wiek) VALUES (?, ?, ?, ?)", (pesele[i - 1], f"Klient{i}", f"Testowy{i}", random.randint(18, 65)))

        for i in range(1, 6):
            cursor.execute("INSERT INTO Opaska (numerSeryjny, czasWejscia, czasWyjscia, klient_id) VALUES (?, ?, ?, ?)", (1000 + i, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None, pesele[i - 1]))

        # Wolne opaski
        for i in range(6, 11):
            cursor.execute("INSERT INTO Opaska (numerSeryjny, czasWejscia, czasWyjscia, klient_id) VALUES (?, ?, ?, ?)", (1000 + i, (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), (datetime.now() - timedelta(hours=23)).strftime("%Y-%m-%d %H:%M:%S"), None))

        self.conn.commit()

    def oblicz_koszt_pobytu(self, czas_wejscia, czas_wyjscia):
        """
        Oblicza koszt pobytu na basenie na podstawie czasu wejścia i wyjścia.
        
        Args:
            czas_wejscia (datetime): Data i czas wejścia
            czas_wyjscia (datetime): Data i czas wyjścia
            
        Returns:
            float: Całkowity koszt pobytu
        """
        koszt = 0
        current_time = czas_wejscia
        
        while current_time < czas_wyjscia:
            is_weekend = current_time.weekday() >= 5
            hour = current_time.hour
            
            # Określenie stawki godzinowej
            if is_weekend:
                rate = 16  # Stawka weekendowa
            elif 8 <= hour < 16:
                rate = 10  # Stawka dzienna (8:00-16:00)
            else:
                rate = 14  # Stawka wieczorowa

            # Oblicz proporcjonalny czas w tej godzinie
            next_hour = (current_time + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            end_of_interval = min(next_hour, czas_wyjscia)
            duration = (end_of_interval - current_time).total_seconds() / 3600  # W godzinach

            # Zaokrąglenie czasu do pełnych godzin
            if duration % 1 > 0:
                duration = int(duration) + 1
            
            koszt += rate * duration
            current_time = end_of_interval

        return round(koszt, 2)  # Zaokrąglenie kosztu
    
    def obsluz_wejscie(self, imie, nazwisko, wiek, id_klienta):
        try:
            # Tworzenie nowego klienta
            klient = Klient(id_klienta, imie, nazwisko, wiek)

            # Wydawanie opaski przez recepcjonistę
            opaska = self.zalogowany_pracownik.wydaj_opaske_nfc(klient, self.conn)

            if opaska:
                # Zapisywanie klienta do bazy
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO Klient (identyfikator, imie, nazwisko, wiek) VALUES (?, ?, ?, ?)",
                    (klient.identyfikator, klient.imie, klient.nazwisko, klient.wiek)
                )
                self.conn.commit()

                return f"Pomyślnie zarejestrowano klienta i wydano opaskę nr {opaska.numerSeryjny}"
            else:
                return "Brak dostępnych opasek!"

        except ValueError as e:
            return f"Błąd podczas wprowadzania danych: {e}"
        except sqlite3.Error as e:
            return f"Błąd bazy danych: {e}"
        
    def obsluz_wyjscie(self, numer_seryjny, metoda_platnosci):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT o.numerSeryjny, o.czasWejscia, o.klient_id, k.imie, k.nazwisko
                FROM Opaska o
                JOIN Klient k ON o.klient_id = k.identyfikator
                WHERE o.numerSeryjny = ? AND o.czasWyjscia IS NULL
            """, (numer_seryjny,))

            dane_opaski = cursor.fetchone()
            if not dane_opaski:
                return "Nie znaleziono aktywnej opaski o podanym numerze."
            
            opaska = OpaskaNFC(dane_opaski[0])
            opaska.czasWejscia = datetime.strptime(dane_opaski[1], "%Y-%m-%d %H:%M:%S")
            opaska.klient_id = dane_opaski[2]

            czas_wyjscia = datetime.now()
            czas_pobytu = (czas_wyjscia - opaska.czasWejscia).total_seconds() / 3600
            godziny = int(czas_pobytu) + (1 if czas_pobytu % 1 > 0 else 0)

            koszt = self.oblicz_koszt_pobytu(opaska.czasWejscia, czas_wyjscia)

            transakcja = Transakcja(
                koszt,
                czas_wyjscia.strftime("%Y-%m-%d %H:%M:%S"),
                metoda_platnosci,
                opaska.klient_id,
                self.zalogowany_pracownik.identyfikator
            )

            if self.zalogowany_pracownik.przyjmij_platnosc(transakcja, self.conn):
                opaska.deaktywuj(self.conn)

                summary = f"\nPodsumowanie wizyty dla klienta {dane_opaski[3]} {dane_opaski[4]}:"
                summary += f"\nCzas wejścia: {opaska.czasWejscia}"
                summary += f"\nCzas wyjścia: {czas_wyjscia.strftime("%Y-%m-%d %H:%M:%S")}"
                summary += f"\nCzas pobytu: {godziny} godz."
                summary += f"\nNależność: {koszt} zł"

                transakcja.wydrukuj_paragon()

                return summary
            else:
                return "Błąd podczas przetwarzania płatności."

        except sqlite3.Error as e:
            return f"Błąd bazy danych: {e}"
        except Exception as e:
            return f"Wystąpił błąd: {e}"
        
    def obsluz_raport(self, typ_raportu, data_od, data_do):
        try:
            # Pobieranie parametrów raportu
            typ_raportu = typ_raportu.lower()
            if typ_raportu not in ["finansowy", "statystyki"]:
                return "Nieprawidłowy typ raportu. Dostępne opcje: finansowy, statystyki"

            # Tworzenie i generowanie raportu
            raport = Raport(
                datetime.now().strftime("%Y-%m-%d"),
                typ_raportu
            )

            dane_raportu = self.zalogowany_pracownik.generuj_raport(typ_raportu, data_od, data_do, self.conn)

            if dane_raportu:
                # Eksport do pliku
                nazwa_pliku = f"raport_{typ_raportu}_{data_od}_do_{data_do}.csv"
                raport.eksportuj_dane(dane_raportu, nazwa_pliku)

                # Loguj generowanie raportu
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO Raport (data, typRaportu, pracownik_id) VALUES (?, ?, ?)", (datetime.now().strftime("%Y-%m-%d"), typ_raportu, self.zalogowany_pracownik.identyfikator))
                self.conn.commit()

                return f"Raport wygenerowany i zapisany w pliku {nazwa_pliku}"

            else:
                return "Brak danych do wygenerowania raportu."

        except ValueError as e:
            return f"Błąd podczas wprowadzania danych: {e}"
        except sqlite3.Error as e:
            return f"Błąd bazy danych: {e}"
        except Exception as e:
            return f"Wystąpił błąd: {e}"
        
    def generuj_testowy_pesel(self):
        start_date = datetime(1800, 1, 1)
        end_date = datetime(2299, 12, 31)
        random_date = start_date + (end_date - start_date) * random.random()
        
        year = random_date.year
        month = random_date.month
        day = random_date.day
        
        if 1800 <= year < 1900:
            month += 80
        elif 2000 <= year < 2100:
            month += 20
        elif 2100 <= year < 2200:
            month += 40
        elif 2200 <= year < 2300:
            month += 60
        
        year_str = f"{year % 100:02}"
        month_str = f"{month:02}"
        day_str = f"{day:02}"
        
        sequence = random.randint(0, 9999)
        sequence_str = f"{sequence:04}"
        
        pesel_without_checksum = f"{year_str}{month_str}{day_str}{sequence_str}"
        
        weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
        checksum = sum(int(pesel_without_checksum[i]) * weights[i] for i in range(10)) % 10
        checksum = (10 - checksum) % 10
        
        pesel = pesel_without_checksum + str(checksum)
        return int(pesel)
