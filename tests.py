import unittest
from datetime import datetime
import sqlite3
import os
import tempfile

from SystemObslugi import *

class TestObliczanieOplat(unittest.TestCase):
    def test_oplata_za_godzine_w_dzien_roboczy(self):
        """Test opłaty za jedną godzinę w dzień roboczy (8:00-16:00)"""
        czas_wejscia = datetime(2025, 1, 7, 10, 0)  # Wtorek 10:00
        czas_wyjscia = datetime(2025, 1, 7, 11, 0)  # Wtorek 11:00
        koszt = SystemObslugi().oblicz_koszt_pobytu(czas_wejscia, czas_wyjscia)
        self.assertEqual(koszt, 10)

    def test_oplata_za_godzine_wieczorem(self):
        """Test opłaty za jedną godzinę wieczorem"""
        czas_wejscia = datetime(2025, 1, 7, 18, 0)  # Wtorek 18:00
        czas_wyjscia = datetime(2025, 1, 7, 19, 0)  # Wtorek 19:00
        koszt = SystemObslugi().oblicz_koszt_pobytu(czas_wejscia, czas_wyjscia)
        self.assertEqual(koszt, 14)

    def test_oplata_za_godzine_w_weekend(self):
        """Test opłaty za jedną godzinę w weekend"""
        czas_wejscia = datetime(2025, 1, 11, 12, 0)  # Sobota 12:00
        czas_wyjscia = datetime(2025, 1, 11, 13, 0)  # Sobota 13:00
        koszt = SystemObslugi().oblicz_koszt_pobytu(czas_wejscia, czas_wyjscia)
        self.assertEqual(koszt, 16)

    def test_oplata_za_pobyt_w_roznych_strefach_czasowych(self):
        """Test opłaty za pobyt przechodzący przez różne strefy czasowe"""
        czas_wejscia = datetime(2025, 1, 7, 15, 30)  # Wtorek 15:30
        czas_wyjscia = datetime(2025, 1, 7, 17, 30)  # Wtorek 17:30
        koszt = SystemObslugi().oblicz_koszt_pobytu(czas_wejscia, czas_wyjscia)
        # 15:30-16:00 (dzień) = 10zł
        # 16:00-17:00 (wieczór) = 14zł
        # 17:00-17:30 (rozpoczęta godzina wieczór) = 14zł
        self.assertEqual(koszt, 38)

    def test_oplata_za_pobyt_overnight(self):
        """Test opłaty za pobyt przez noc"""
        czas_wejscia = datetime(2025, 1, 7, 23, 0)  # Wtorek 23:00
        czas_wyjscia = datetime(2025, 1, 8, 1, 0)  # Środa 1:00
        koszt = SystemObslugi().oblicz_koszt_pobytu(czas_wejscia, czas_wyjscia)
        # 23:00-00:00 (wieczór) = 14zł
        # 00:00-01:00 (wieczór) = 14zł
        self.assertEqual(koszt, 28)

    def test_oplata_za_pobyt_przez_weekend(self):
        """Test opłaty za pobyt przechodzący przez weekend"""
        czas_wejscia = datetime(2025, 1, 10, 23, 0)  # Piątek 23:00
        czas_wyjscia = datetime(2025, 1, 11, 1, 0)  # Sobota 1:00
        koszt = SystemObslugi().oblicz_koszt_pobytu(czas_wejscia, czas_wyjscia)
        # 23:00-00:00 (wieczór piątek) = 14zł
        # 00:00-01:00 (weekend) = 16zł
        self.assertEqual(koszt, 30)


class TestGenerowanieRaportow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Przygotowanie bazy danych testowej"""
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False)
        cls.conn = sqlite3.connect(cls.temp_db.name)
        cls._create_test_database(cls.conn)

    @classmethod
    def tearDownClass(cls):
        """Sprzątanie po testach"""
        try:
            cls.conn.close()
            os.unlink(cls.temp_db.name)
        except Exception:
            pass

    @classmethod
    def _create_test_database(cls, conn):
        """Tworzenie testowej bazy danych"""
        cursor = conn.cursor()
        
        # Tworzenie tabel
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Transakcja (
            identyfikatorTransakcji INTEGER PRIMARY KEY AUTOINCREMENT,
            kwota REAL NOT NULL,
            data TEXT NOT NULL,
            metodaPlatnosci TEXT NOT NULL,
            klient_id INTEGER,
            pracownik_id INTEGER
        )
        """)

        # Dodawanie testowych danych
        test_data = [
            (1, 50.0, "2025-01-07 10:00:00", "Gotówka", 1, 1),
            (2, 75.0, "2025-01-07 11:00:00", "Karta", 2, 1),
            (3, 100.0, "2025-01-07 12:00:00", "Gotówka", 3, 2),
            (4, 120.0, "2025-01-07 13:00:00", "Karta", 4, 2),
        ]
        
        cursor.executemany(
            "INSERT INTO Transakcja VALUES (?, ?, ?, ?, ?, ?)",
            test_data
        )
        conn.commit()

    def test_generowanie_raportu_finansowego(self):
        """Test generowania raportu finansowego"""
        raport = Raport("2025-01-07", "finansowy")
        dane = raport._generuj_raport_finansowy("2025-01-07 0:00:00", "2025-01-07 23:59:59", self.conn)
        
        self.assertIsNotNone(dane)
        self.assertTrue(len(dane) > 0)
        
        # Sprawdzanie sum dla różnych metod płatności
        suma_gotowka = sum(row[2] for row in dane if row[1] == "Gotówka")
        suma_karta = sum(row[2] for row in dane if row[1] == "Karta")
        
        self.assertEqual(suma_gotowka, 150.0)  # 50 + 100
        self.assertEqual(suma_karta, 195.0)    # 75 + 120

    def test_generowanie_raportu_statystycznego(self):
        """Test generowania raportu statystycznego"""
        raport = Raport("2025-01-07", "statystyki")
        dane = raport._generuj_raport_statystyczny("2025-01-07", "2025-01-07", self.conn)
        
        self.assertIsNotNone(dane)
        self.assertEqual(len(dane), 4)  # 4 różnych klientów
        
        # Sprawdzanie sum dla poszczególnych klientów
        sumy_klientow = {row[0]: row[1] for row in dane}
        self.assertEqual(sumy_klientow[1], 50.0)
        self.assertEqual(sumy_klientow[2], 75.0)
        self.assertEqual(sumy_klientow[3], 100.0)
        self.assertEqual(sumy_klientow[4], 120.0)

    def test_generowanie_raportu_dla_pustego_okresu(self):
        """Test generowania raportu dla okresu bez danych"""
        raport = Raport("2025-01-08", "finansowy")
        dane = raport._generuj_raport_finansowy("2025-01-08", "2025-01-08", self.conn)
        
        self.assertEqual(len(dane), 0)

class TestAuthorization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Przygotowanie bazy danych testowej"""
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False)
        cls.conn = sqlite3.connect(cls.temp_db.name)
        cls._create_test_database(cls.conn)

    @classmethod
    def tearDownClass(cls):
        """Sprzątanie po testach"""
        try:
            cls.conn.close()
            os.unlink(cls.temp_db.name)
        except Exception:
            pass

    @classmethod
    def _create_test_database(cls, conn):
        """Tworzenie testowej bazy danych"""
        cursor = conn.cursor()
        
        # Tworzenie tabel
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pracownik (
            identyfikator INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL UNIQUE,
            haslo TEXT NOT NULL,
            imie TEXT NOT NULL,
            nazwisko TEXT NOT NULL,
            stanowisko TEXT NOT NULL
        )
        """)

        # Dodawanie testowych danych
        test_data = [
            (1, "jan", SystemObslugi().szyfruj_haslo("secure123"), "Jan", "Kowalski", "Recepcjonista"),
        ]
        
        cursor.executemany(
            "INSERT INTO Pracownik VALUES (?, ?, ?, ?, ?, ?)",
            test_data
        )
        conn.commit()

    def test_szyfruj_haslo(self):
        """Test szyfrowania hasła"""
        haslo = "tajnehaslo123"
        zaszyfrowane_haslo = SystemObslugi().szyfruj_haslo(haslo)
        self.assertNotEqual(haslo, zaszyfrowane_haslo)

    def test_sprawdz_haslo(self):
        """Test sprawdzania poprawności hasła"""
        haslo = "tajnehaslo123"
        system = SystemObslugi()
        zaszyfrowane_haslo = system.szyfruj_haslo(haslo)
        self.assertTrue(system.weryfikuj_haslo(haslo, zaszyfrowane_haslo))

    def test_autoryzacja_poprawnego_pracownika(self):
        """Test autoryzacji poprawnego pracownika"""
        system = SystemObslugi()
        system.conn = self.conn
        self.assertTrue(system.zaloguj_uzytkownika("jan", "secure123"))

    def test_autoryzacja_niepoprawnego_pracownika(self):
        """Test autoryzacji niepoprawnego pracownika"""
        system = SystemObslugi()
        system.conn = self.conn
        self.assertFalse(system.zaloguj_uzytkownika("jan", "wrongpassword"))

if __name__ == '__main__':
    unittest.main()