import csv

class Raport:
    def __init__(self, data, typ_raportu):
        self.data = data
        self.typRaportu = typ_raportu

    def generuj_raport(self, data_od, data_do, conn):
        if self.typRaportu == "finansowy":
            return self._generuj_raport_finansowy(data_od, data_do, conn)
        elif self.typRaportu == "statystyki":
            return self._generuj_raport_statystyczny(data_od, data_do, conn)
        return None

    def _generuj_raport_finansowy(self, data_od, data_do, conn):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE(data) AS dzien, metodaPlatnosci, SUM(kwota) AS laczna_kwota
            FROM Transakcja
            WHERE data BETWEEN ? AND ?
            GROUP BY dzien, metodaPlatnosci
            ORDER BY dzien, metodaPlatnosci
        """, (data_od, data_do))
        return cursor.fetchall()

    def _generuj_raport_statystyczny(self, data_od, data_do, conn):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.klient_id, SUM(t.kwota) AS wydane
            FROM Transakcja t
            WHERE DATE(t.data) BETWEEN ? AND ?
            GROUP BY t.klient_id
        """, (data_od, data_do))
        return cursor.fetchall()

    def eksportuj_dane(self, dane, nazwa_pliku):
        with open(nazwa_pliku, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if self.typRaportu == "finansowy":
                writer.writerow(["Data", "Metoda płatności", "Łączna kwota"])
            else:
                writer.writerow(["ID klienta", "Łączna kwota wydana"])
            writer.writerows(dane)