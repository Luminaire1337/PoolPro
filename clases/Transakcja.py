class Transakcja:
    def __init__(self, kwota, data, metoda_platnosci, klient_id, pracownik_id):
        self.kwota = kwota
        self.data = data
        self.metodaPlatnosci = metoda_platnosci
        self.klient_id = klient_id
        self.pracownik_id = pracownik_id

    def przetworz_platnosc(self, conn):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Transakcja 
            (kwota, data, metodaPlatnosci, klient_id, pracownik_id)
            VALUES (?, ?, ?, ?, ?)
        """, (self.kwota, self.data,
              self.metodaPlatnosci, self.klient_id, self.pracownik_id))
        conn.commit()
        self.identyfikatorTransakcji = cursor.lastrowid
        return True

    def wydrukuj_paragon(self):
        with open('paragon.txt', 'w', encoding='utf-8') as plik:
            plik.write("========================\n")
            plik.write("Pływalnia - Paragon\n")
            plik.write(f"ID Transakcji: {self.identyfikatorTransakcji or "BŁĄD"}\n")
            plik.write(f"Data: {self.data}\n")
            plik.write(f"Kwota: {self.kwota} zł\n")
            plik.write(f"Metoda płatności: {self.metodaPlatnosci}\n")
            plik.write("========================\n")