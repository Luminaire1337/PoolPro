from datetime import datetime

class OpaskaNFC:
    def __init__(self, numer_seryjny):
        self.numerSeryjny = numer_seryjny
        self.czasWejscia = None
        self.czasWyjscia = None
        self.klient_id = None

    def aktywuj(self, klient, conn):
        self.klient_id = klient.identyfikator
        self.czasWejscia = datetime.now()
        
        # Sync with database
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Opaska 
            SET czasWejscia = ?, czasWyjscia = NULL, klient_id = ? 
            WHERE numerSeryjny = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.klient_id, self.numerSeryjny))
        conn.commit()

    def deaktywuj(self, conn):
        self.klient_id = None
        self.czasWyjscia = datetime.now()

        # Sync with database
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Opaska 
            SET czasWyjscia = ?, klient_id = NULL
            WHERE numerSeryjny = ?
        """, (self.czasWyjscia.strftime("%Y-%m-%d %H:%M:%S"), self.numerSeryjny))
        conn.commit()