from datetime import datetime
from classes.OpaskaNFC import *
from classes.Raport import *

class Recepcjonista:
    def __init__(self, identyfikator, login, imie, nazwisko, stanowisko):
        self.identyfikator = identyfikator
        self.login = login
        self.imie = imie
        self.nazwisko = nazwisko
        self.stanowisko = stanowisko

    def wydaj_opaske_nfc(self, klient, conn):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT numerSeryjny FROM Opaska 
            WHERE klient_id IS NULL
            LIMIT 1
        """)
        wynik = cursor.fetchone()
        if wynik:
            opaska = OpaskaNFC(wynik[0])
            opaska.aktywuj(klient, conn)
            return opaska
        return None

    def przyjmij_platnosc(self, transakcja, conn):
        return transakcja.przetworz_platnosc(conn)

    def generuj_raport(self, typ_raportu, data_od, data_do, conn):
        raport = Raport(datetime.now().strftime("%Y-%m-%d"), typ_raportu)
        return raport.generuj_raport(data_od, data_do, conn)