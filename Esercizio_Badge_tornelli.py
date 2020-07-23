import time # MI SERVE PER L'ANIMAZIONE CON IL DELAY
import random # SERVE PER ESTRARRE IL NUMERO RANDOM
import datetime # SERVE PER CALCOLARE DATA E ORA ATTUALE
import sqlite3 #SERVE PER LA CONNESSIONE AL DB

date_format = "%d/%m/%Y %H:%M:%S" #FORMATO DATETIME
GIORNI_DI_VALIDITA = 180

conn = sqlite3.connect('file:./registrobadge.sqlite?mode=rw', uri=True) #CONNECTION STRING


def setNuovo(nom,cogn,cfis,ind,role): #CREAZIONE NUOVO BADGE
    
    while True:
        cont = 0
        r = random.randint(1,1000)  #ASSEGNO UN NUMERO RANDOM AL BADGE
        with conn:
            cursore = conn.cursor() #CREO IL CURSORE
            try:
                cursore.execute("SELECT NumeroBadge FROM [Utente]")
                ok = cursore.fetchall() #RESTITUISCE SOLO LA PRIMA RIGA

            except sqlite3.Error as error:
                print("Non è stato possibile inserire i dati nel database", error)    #CONTROLLO UNICITA' NUMERO BADGE

            finally:
                cursore.close() #CHIUDO IN TUTTI I CASI LA CONNESSIONE
        cont = 0
        # N.B. Tupla[][] --> Prima Quadra N° Riga , Seconda Quadra N° Colonna
        for i in range(len(ok)):
            if r == ok[i][0]: #LEGGO IL PRIMO VALORE DI OGNI RIGA (ok[i][0]) 
                cont = cont +1
        if cont == 0:
            break #ESCO DAL WHILE TRUE

    data = datetime.datetime.now().strftime(date_format) #ORARIO ATTUALE FORMATO PRESTABILITO
    with conn:
        cursore = conn.cursor()  #CREO IL CURSORE
        try:
        
            cursore.execute("INSERT INTO [Utente](Nome,Cognome,Indirizzo,CodFis,NumeroBadge,DataRinnovo,Presenza,Validita) VALUES (?,?,?,?,?,?,?,?)",(nom, cogn, ind, cfis, r, data, False, True))
            cursore.execute("INSERT INTO [UtenteRuolo](IdUtente,IdRuolo) VALUES ((SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?),(SELECT IdRuolo From [Ruolo] WHERE Nome = ?))",[ r, role])
            cursore.execute("INSERT INTO [Operazioni](Tipo,DataOra,IdUtente) VALUES ('Nuovo Badge',?,(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?))", [data, r])
            #NEL CASO DELL'INSERT BASTA SOLO IL .execute(), I PARAMETRI SI PASSANO CON ?  E POI DOPO LA VIRGOLA DELLA STRINGA LE VARIABILI, IDEM UPDATE E DELETE
        except sqlite3.Error as error: 
            print("Non è stato possibile inserire i dati nella tabella", error) #INSERIMENTO NUOVO BADGE
        finally:
            cursore.close()  #CHIUDO IN TUTTI I CASI LA CONNESSIONE

def accesso():

    numero = int(input('Inserire numero Badge: ')) #ACCESSO AI TORNELLI CONTROLLO SE ESISTE O ACCESSO GIA' FATTO
    with conn:
        cursore = conn.cursor()     #CREO IL CURSORE
        try:
            cursore.execute("SELECT NumeroBadge FROM [Utente]") #TROVA IL NUMERO BADGE SE ESISTENTE
            ok = cursore.fetchall() #RESTITUISCE TUTTE LE RIGHE NELLA TUPLA ok
            cont = 0
            for i in range(len(ok)): #FA SCORRERE LA TUPLA
                if numero == ok[i][0]:   #LEGGO IL PRIMO VALORE DI OGNI RIGA (ok[i][0])
                    cont = cont +1
            if cont >= 1: #SE ESISTE ENTRO NELL'IF
                if controlloValidita(numero) == True:
                    cursore.execute("SELECT Presenza FROM [Utente] WHERE NumeroBadge=?",[numero]) #CONTROLLA SE GIA' PRESENTE
                    pre = cursore.fetchall()   #RESTITUISCE TUTTE LE RIGHE NELLA TUPLA pre
                    if pre[0][0] == 0: #SE NON E' PRESENTE ( 0 = FALSE )
                        time.sleep(1)
                        print('.',end=' ',flush=True)
                        time.sleep(1)
                        print('.',end=' ',flush=True) #ANIMAZIONI . . .
                        time.sleep(1)
                        print('.',flush=True)
                        time.sleep(1.5)
                        
                        cursore.execute("SELECT Cognome,Utente.Nome,Ruolo.Nome FROM Utente JOIN UtenteRuolo ON Utente.IdUtente = UtenteRuolo.IdUtente JOIN Ruolo ON UtenteRuolo.IdRuolo = Ruolo.IdRuolo WHERE NumeroBadge = ?",[numero])
                        # QUERY CHE MI DA I CAMPI DA SCRIVERE NEL BENVENUTO
                        d = cursore.fetchone()
                        dati = []
                        for i in d:
                            dati.append(i) #METTO I CAMPI IN UN VETTORE ( dati[] )
                        if len(dati) == 3:
                            print(f"{dati[1]} {dati[0]} Benvenuto nella stanza! Ruolo: {dati[2]}")
                            cursore.execute("UPDATE [Utente] SET Presenza=True WHERE NumeroBadge=?",[numero])   #SEGNA PRESENTE = tRUE ( 1 )
                            data = datetime.datetime.now().strftime(date_format) #DATETIME CORRENTE
                            cursore.execute("INSERT INTO [EntrateTornello] (IdUtente,DataOra,EntrataUscita) VALUES ((SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?),?,'Entrata')",[numero,data])
                            return True #   RESTITUISCO TRUE PER POI ACCEDERE ALLE PORTE INTERNE


                            #APERTURA PORTE



                        else:
                            print(f"{dati[1]} {dati[0]} Devi prima farti assegnare un ruolo dal direttore per entrare")
                            return False

                    else:
                        print("Entrata senza uscita!") #CHIUSURA VARI CONTROLLI + RESTITUISCO FALSO
                        return False
                else:
                    print("il badge è scaduto!")

            else:
                print("Questo numero badge non esiste!")
                return False
                    
        except sqlite3.Error as error:
            print("Impossibile inserire i dati all'interno della tabella", error)

        finally:
            cursore.close()

def uscita():
    numero = int(input('Inserire numero Badge: ')) #USCITA TORNELLI CONTROLLO SE ESISTE O NON ENTRATO
    with conn:
        cursore = conn.cursor() #CREO CURSORE
        try:
            cursore.execute("SELECT NumeroBadge FROM [Utente]")
            ok = cursore.fetchall() #RESTITUISCO TUTTE LE RIGHE
            cont = 0
            for i in range(len(ok)): #SCORRO TUTTA LA TUPLA
                if numero == ok[i][0]:  #LEGGO IL PRIMO VALORE DI OGNI RIGA (ok[i][0])
                    cont = cont +1
            if cont >= 1:
                cursore.execute("SELECT Presenza FROM [Utente] WHERE NumeroBadge=?",[numero])    #CONTROLLA SE GIA' PRESENTE
                pre = cursore.fetchall()  #RESTITUISCO TUTTE LE RIGHE, in questo caso potevo usare benissimo il .fetchone() perchè mi serve solo la prima riga e prima colonna
                if pre[0][0] == 1:
                    time.sleep(1)
                    print('.',end=' ',flush=True)
                    time.sleep(1)
                    print('.',end=' ',flush=True) #animazioni . . .
                    time.sleep(1)
                    print('.',flush=True)
                    time.sleep(1.5)
                    cursore.execute("UPDATE [Utente] SET Presenza=False WHERE NumeroBadge=?",[numero])   #SEGNA USCITA Presenza = false ( 0 )
                    cursore.execute("SELECT Cognome FROM Utente WHERE NumeroBadge=?",[numero])  #Trovo il nome per salutarlo
                    d = cursore.fetchone()  #restituisco solo la prima riga nel vettore d[]
                    print(f"Arrivederci Sig. {d[0]}!") #d[0] è la prima colonna
                    data = datetime.datetime.now().strftime(date_format) #DATETIME CORRENTE
                    cursore.execute("INSERT INTO [EntrateTornello] (IdUtente,DataOra,EntrataUscita) VALUES ((SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?),?,'Uscita')",[numero,data])


                    #APERTURA PORTE



                else:
                    print("Devi prima effettuare l'accesso!")
            else:
                print("Questo numero badge non esiste!") #controlli vari
                    
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
        finally: 
            cursore.close() #CHIUDO IN OGNI CASO LA CONNESSIONE

def nuovoBadge(): #NUOVO BADGE 
    n = input('Nome: ')
    cn = input('Cognome: ')
    while True:
        cf = input('Codice Fiscale: ')
        with conn:
            cursore = conn.cursor() #CREO CURSORE
            try:
                cursore.execute("SELECT CodFis FROM [Utente]")          #CONTROLLA SE CODICE FISCALE GIA' PRESENTE NEL DB
                ok = cursore.fetchall() #RESTITUISCO TUTTE LE RIGHE

            except sqlite3.Error as error:
                print("Impossibile inserire i dati all'interno della tabella", error)

            finally:
                cursore.close()
        cont = 0
        for i in range(len(ok)): #FACCIO SCORRERE TUTTA LA TUPLA
            if cf == ok[i][0]:
                cont = cont +1
        if cont == 1:
            print("Codice fiscale già presente!")
        else:
            break #ESCO DAL WHILE TRUE
    ind = input('Indirizzo: ')

    while True:
        role = input("Ruolo: ")
        with conn:
            cursore = conn.cursor() #CREO CURSORE
            try:
                cursore.execute("SELECT Nome FROM [Ruolo]")          #CONTROLLA SE IL RUOLO ESISTE NEL DB
                ok = cursore.fetchall() #RESTITUISCO TUTTE LE RIGHE

            except sqlite3.Error as error:
                print("Impossibile inserire i dati all'interno della tabella", error) #FA IL CICLO FINCHE' NON METTO UN RUOLO ESISTENTE

            finally:
                cursore.close()
        cont = 0
        for i in range(len(ok)):  #FACCIO SCORRERE TUTTA LA TUPLA
            if role == ok[i][0]:
                cont = cont +1
        if cont == 1:
            break
        else:
            print(f"Immettere un Ruolo esistente! {ok}")

    setNuovo(n, cn, cf, ind, role) #CHIAMO LA FUNZIONE CHE MI FA GLI INSERT 
    time.sleep(1)
    print('.',end=' ',flush=True)
    time.sleep(1)
    print('.',end=' ',flush=True)
    time.sleep(1)
    print('.',flush=True)
    time.sleep(1.5)
    print('Operazione andata a buon fine! (Il suo badge ha validità 6 mesi - 180 giorni)\nIl suo numero badge è: ', end="")
    with conn:
        cursore = conn.cursor()
        try:
            cursore.execute("SELECT NumeroBadge FROM [Utente] WHERE CodFis=?",[cf]) #ESTRAGGO NUMERO BADGE PER COMUNICARGLIELO
            nb = cursore.fetchall() #RESTITUISCO TUTTE LE RIGHE
            print(nb[0][0]) #PRIMA RIGA PRIMA COLONNA
        except sqlite3.Error as error:
            print("Impossibile inserire i dati all'interno della tabella", error)
        finally:
            cursore.close()

def rinnova():
    numero = int(input('Inserire numero Badge: ')) #RINNOVA DI 180 GIORNI IL BADGE + CONTROLLI SE ANCORA VALIDO O NON ESISTENTE
    with conn:
        cursore = conn.cursor()
        try:
            cursore.execute("SELECT NumeroBadge FROM [Utente]") #SOLITO CONTROLLO SE ESISTE BADGE
            ok = cursore.fetchall()
            cont = 0
            for i in range(len(ok)): #SOLITO CICLO TUPLA
                if numero == ok[i][0]: 
                    cont = cont +1
            if cont >= 1:
                    cursore.execute("SELECT Validita FROM [Utente] WHERE NumeroBadge=?",[numero]) #CONTROLLA SE REALMENTE SCADUTO
                    pre = cursore.fetchall()
                    if pre[0][0] == 0: # pre[0][0] PRIMA RIGA PRIMA COLONNA
                        time.sleep(1)
                        print('.',end=' ',flush=True)
                        time.sleep(1)
                        print('.',end=' ',flush=True)
                        time.sleep(1)
                        print('.',flush=True)
                        time.sleep(1.5)
                        data = datetime.datetime.now().strftime(date_format) #DATETIME CORRENTE
                        cursore.execute("UPDATE [Utente] SET Validita=True,DataRinnovo=? WHERE NumeroBadge=?",(data,numero))
                        cursore.execute("INSERT INTO [Operazioni](Tipo,DataOra,IdUtente) VALUES ('Rinnovo',?,(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?))", [data, numero])
                        #RINNOVO CON VALIDITA = TRUE ( 1 ) , E DATETIME CORRENTE
                        print("Rinnovo eseguito con successo!") #RINNOVO
                    else:
                        print("Il suo badge è ancora valido!")
                    
            else:
                print("Numero badge non valido!. Ricontrollare il numero") #CHIUSURA CONTROLLI VARI
                    
        except sqlite3.Error as error:
            print("Impossibile inserire i dati all'interno della tabella", error)
        finally:
            cursore.close()

def nuovaStanza():
    numero = int(input('Inserire numero Badge: ')) #ACCESSO AI TORNELLI CONTROLLO SE ESISTE O ACCESSO GIA' FATTO
    with conn:
        cursore = conn.cursor()     #CREO IL CURSORE
        try:
            cursore.execute("SELECT NumeroBadge FROM [Utente]") #TROVA IL NUMERO BADGE SE ESISTENTE
            ok = cursore.fetchall() #RESTITUISCE TUTTE LE RIGHE NELLA TUPLA ok
            cont = 0
            for i in range(len(ok)): #FA SCORRERE LA TUPLA
                if numero == ok[i][0]:   #LEGGO IL PRIMO VALORE DI OGNI RIGA (ok[i][0])
                    cont = cont +1
            if cont >= 1: #SE ESISTE ENTRO NELL'IF

                cursore.execute("SELECT Ruolo.Nome FROM [Ruolo] JOIN [UtenteRuolo] ON [UtenteRuolo].IdRuolo=[Ruolo].IdRuolo JOIN [Utente] ON [Utente].IdUtente=[UtenteRuolo].IdUtente WHERE NumeroBadge=?",[numero]) 
                ro = cursore.fetchall()
                cont = 0
                for i in range(len(ro)):
                    if ro[i][0] == 'Amministratore':
                        cont = cont + 1
                if cont > 0:

                    while True:
                        nst = input('Nome nuova stanza (COLORE): ')
                        with conn:
                            cursore = conn.cursor() #CREO CURSORE
                            try:
                                cursore.execute("SELECT Nome FROM [Stanza]")          #CONTROLLA SE COLORE STANZA GIA' PRESENTE NEL DB
                                ok = cursore.fetchall() #RESTITUISCO TUTTE LE RIGHE

                            except sqlite3.Error as error:
                                print("Impossibile inserire i dati all'interno della tabella", error)

                            finally:
                                cursore.close()
                        cont = 0
                        for i in range(len(ok)): #FACCIO SCORRERE TUTTA LA TUPLA
                            if nst == ok[i][0]:
                                cont = cont +1
                        if cont > 0:
                            print("Colore stanza già presente!")
                        else:
                            break #ESCO DAL WHILE TRUE
                    
                    des = input('Aggiungi un eventuale descrizione: ')
                    with conn:
                        cursore = conn.cursor()
                        try:
                            cursore.execute("INSERT INTO [Stanza](Nome, Descrizione) VALUES (?,?)",[nst,des]) #INSERIMENTO COMPLETATO
                            data = datetime.datetime.now().strftime(date_format)
                            cursore.execute("INSERT INTO [Operazioni](Tipo,DataOra,IdUtente) VALUES ('Nuova Stanza',?,(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?))", [data, numero])
                            print("Stanza inserita con successo!")

                        except sqlite3.Error as error:
                            print("Impossibile inserire i dati all'interno della tabella: ", error)
                        finally:
                            cursore.close()

                else:
                    print("Devi essere amministratore per accedere a questa sezione!!!")
            else:
                print("Questo numero badge non esiste!")


        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table: ", error)

        finally:
            cursore.close()

def nuovoRuolo():
    numero = int(input('Inserire numero Badge: ')) #ACCESSO AI TORNELLI CONTROLLO SE ESISTE O ACCESSO GIA' FATTO
    with conn:
        cursore = conn.cursor()     #CREO IL CURSORE
        try:
            cursore.execute("SELECT NumeroBadge FROM [Utente]") #TROVA IL NUMERO BADGE SE ESISTENTE
            ok = cursore.fetchall() #RESTITUISCE TUTTE LE RIGHE NELLA TUPLA ok
            cont = 0
            for i in range(len(ok)): #FA SCORRERE LA TUPLA
                if numero == ok[i][0]:   #LEGGO IL PRIMO VALORE DI OGNI RIGA (ok[i][0])
                    cont = cont +1
            if cont >= 1: #SE ESISTE ENTRO NELL'IF

                cursore.execute("SELECT Ruolo.Nome FROM [Ruolo] JOIN [UtenteRuolo] ON [UtenteRuolo].IdRuolo=[Ruolo].IdRuolo JOIN [Utente] ON [Utente].IdUtente=[UtenteRuolo].IdUtente WHERE NumeroBadge=?",[numero]) 
                ro = cursore.fetchall()
                cont = 0
                for i in range(len(ro)):
                    if ro[i][0] == 'Amministratore':
                        cont = cont + 1
                if cont > 0:

                    while True:
                        nruolo = input('Nome nuovo Ruolo: ')
                        with conn:
                            cursore = conn.cursor() #CREO CURSORE
                            try:
                                cursore.execute("SELECT Nome FROM [Ruolo]")          #CONTROLLA SE RUOLO STANZA GIA' PRESENTE NEL DB
                                ok = cursore.fetchall() #RESTITUISCO TUTTE LE RIGHE

                            except sqlite3.Error as error:
                                print("Failed to insert data into sqlite table", error)

                            finally:
                                cursore.close()
                        cont = 0
                        for i in range(len(ok)): #FACCIO SCORRERE TUTTA LA TUPLA
                            if nruolo == ok[i][0]:
                                cont = cont +1
                        if cont > 0:
                            print("Ruolo già presente!")
                        else:
                            break #ESCO DAL WHILE TRUE
                    
                    des = input('Aggiungi un eventuale descrizione: ')
                    with conn:
                        cursore = conn.cursor()
                        try:
                            cursore.execute("INSERT INTO [Ruolo](Nome, Descrizione) VALUES (?,?)",[nruolo,des]) #INSERIMENTO COMPLETATO
                            data = datetime.datetime.now().strftime(date_format)
                            cursore.execute("INSERT INTO [Operazioni](Tipo,DataOra,IdUtente) VALUES ('Nuovo Ruolo',?,(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?))", [data, numero])
                            print("Ruolo inserito con successo!")

                        except sqlite3.Error as error:
                            print("Failed to insert data into sqlite table: ", error)
                        finally:
                            cursore.close()

                else:
                    print("Devi essere amministratore per accedere a questa sezione!!!")
            else:
                print("Questo numero badge non esiste!")


        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table: ", error)

        finally:
            cursore.close()

def nuoviPermessi():
    numero = int(input('Inserire numero Badge: ')) #ACCESSO AI TORNELLI CONTROLLO SE ESISTE O ACCESSO GIA' FATTO
    with conn:
        cursore = conn.cursor()     #CREO IL CURSORE
        try:
            cursore.execute("SELECT NumeroBadge FROM [Utente]") #TROVA IL NUMERO BADGE SE ESISTENTE
            ok = cursore.fetchall() #RESTITUISCE TUTTE LE RIGHE NELLA TUPLA ok
            cont = 0
            for i in range(len(ok)): #FA SCORRERE LA TUPLA
                if numero == ok[i][0]:   #LEGGO IL PRIMO VALORE DI OGNI RIGA (ok[i][0])
                    cont = cont +1
            if cont >= 1: #SE ESISTE ENTRO NELL'IF

                cursore.execute("SELECT Ruolo.Nome FROM [Ruolo] JOIN [UtenteRuolo] ON [UtenteRuolo].IdRuolo=[Ruolo].IdRuolo JOIN [Utente] ON [Utente].IdUtente=[UtenteRuolo].IdUtente WHERE NumeroBadge=?",[numero]) 
                ro = cursore.fetchall()
                cont = 0
                for i in range(len(ro)):
                    if ro[i][0] == 'Amministratore':
                        cont = cont + 1
                if cont > 0:
                    while True:
                        role = input("Ruolo: ")
                        with conn:
                            cursore = conn.cursor() #CREO CURSORE
                            try:
                                cursore.execute("SELECT Nome FROM [Ruolo]")          #CONTROLLA SE IL RUOLO ESISTE NEL DB
                                ok = cursore.fetchall() #RESTITUISCO TUTTE LE RIGHE

                            except sqlite3.Error as error:
                                print("Failed to insert data into sqlite table", error) #FA IL CICLO FINCHE' NON METTO UN RUOLO ESISTENTE

                            finally:
                                cursore.close()
                        cont = 0
                        for i in range(len(ok)):  #FACCIO SCORRERE TUTTA LA TUPLA
                            if role == ok[i][0]:
                                cont = cont +1
                        if cont == 1:
                            break
                        else:
                            print(f"Immettere un Ruolo esistente! {ok}")


                    while True:
                        sta = input("Stanza: ")
                        with conn:
                            cursore = conn.cursor() #CREO CURSORE
                            try:
                                cursore.execute("SELECT Nome FROM [Stanza]")          #CONTROLLA SE LA STANZA ESISTE NEL DB
                                ok = cursore.fetchall() #RESTITUISCO TUTTE LE RIGHE

                            except sqlite3.Error as error:
                                print("Failed to insert data into sqlite table", error) #FA IL CICLO FINCHE' NON METTO UN RUOLO ESISTENTE

                            finally:
                                cursore.close()
                        cont = 0
                        for i in range(len(ok)):  #FACCIO SCORRERE TUTTA LA TUPLA
                            if sta == ok[i][0]:
                                cont = cont +1
                        if cont == 1:
                            break
                        else:
                            print(f"Immettere una Stanza esistente! {ok}")

                    with conn:
                        cursore = conn.cursor()
                        try:
                            cursore.execute("SELECT * FROM [Permessi] WHERE IdRuolo=(SELECT IdRuolo FROM [Ruolo] WHERE Nome=?) AND IdStanza=(SELECT IdStanza FROM [Stanza] WHERE Nome=?)",[role, sta])
                            ris = cursore.fetchone()
                        except sqlite3.Error as error:
                                print("Failed to insert data into sqlite table: ", error)
                        finally:
                            cursore.close()
                        
                    if ris == None:

                        while True:
                            risp = input("Permesso Concesso o Negato? (Rispondere con Accesso-Negato) ")
                            if risp == 'Accesso':
                                permesso = 1
                                break
                            if risp == 'Negato':
                                permesso = 0
                                break

                        with conn:
                            cursore = conn.cursor()
                            try:
                                cursore.execute("INSERT INTO [Permessi](IdRuolo, IdStanza, Permesso) VALUES ((SELECT IdRuolo FROM [Ruolo] WHERE Nome=?),(SELECT IdStanza FROM [Stanza] WHERE Nome=?),?)",[role, sta, permesso]) #INSERIMENTO COMPLETATO
                                data = datetime.datetime.now().strftime(date_format)
                                cursore.execute("INSERT INTO [Operazioni](Tipo,DataOra,IdUtente) VALUES ('Nuovo Permesso',?,(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?))", [data, numero])
                                print("Permesso inserito con successo!")

                            except sqlite3.Error as error:
                                print("Failed to insert data into sqlite table: ", error)
                            finally:
                                cursore.close()
                    else:
                        print("Tra questo Ruolo e questa Stanza c'è già un permesso esistente")
                else:
                    print("Devi essere amministratore per accedere a questa sezione!!!")
            else:
                print("Questo numero badge non esiste!")


        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table: ", error)

        finally:
            cursore.close()

def gestisciUtente():
    numero = int(input('Inserire numero Badge: ')) #ACCESSO AI TORNELLI CONTROLLO SE ESISTE O ACCESSO GIA' FATTO
    with conn:
        cursore = conn.cursor()     #CREO IL CURSORE
        try:
            cursore.execute("SELECT NumeroBadge FROM [Utente]") #TROVA IL NUMERO BADGE SE ESISTENTE
            ok = cursore.fetchall() #RESTITUISCE TUTTE LE RIGHE NELLA TUPLA ok
            cont = 0
            for i in range(len(ok)): #FA SCORRERE LA TUPLA
                if numero == ok[i][0]:   #LEGGO IL PRIMO VALORE DI OGNI RIGA (ok[i][0])
                    cont = cont +1
            if cont >= 1: #SE ESISTE ENTRO NELL'IF

                cursore.execute("SELECT Ruolo.Nome FROM [Ruolo] JOIN [UtenteRuolo] ON [UtenteRuolo].IdRuolo=[Ruolo].IdRuolo JOIN [Utente] ON [Utente].IdUtente=[UtenteRuolo].IdUtente WHERE NumeroBadge=?",[numero]) 
                ro = cursore.fetchall()
                cont = 0
                for i in range(len(ro)):
                    if ro[i][0] == 'Amministratore':
                        cont = cont + 1
                if cont > 0:
                    while True:
                        nub = int(input('Inserire numero Badge da Gestire: ')) #ACCESSO AI TORNELLI CONTROLLO SE ESISTE O ACCESSO GIA' FATTO
                        with conn:
                            cursore = conn.cursor()     #CREO IL CURSORE
                            try:
                                cursore.execute("SELECT NumeroBadge FROM [Utente]") #TROVA IL NUMERO BADGE SE ESISTENTE
                                ok = cursore.fetchall() #RESTITUISCE TUTTE LE RIGHE NELLA TUPLA ok
                                cont = 0
                                for i in range(len(ok)): #FA SCORRERE LA TUPLA
                                    if nub == ok[i][0]:   #LEGGO IL PRIMO VALORE DI OGNI RIGA (ok[i][0])
                                        cont = cont +1
                            except sqlite3.Error as error:
                                print("Failed to insert data into sqlite table: ", error)
                            finally:
                                cursore.close()
                        if cont >= 1:
                            break
                        else:
                            print("numero badge non esistente")

                    while True:
                        s =int(input("\n ( 1 ) Disattiva\n ( 2 ) Elimina\n ( 3 ) Torna Indietro\n -> "))
                        if s == 1:
                            with conn:
                                cursore = conn.cursor()
                                try:
                                    cursore.execute("UPDATE [Utente] SET Validita=False WHERE NumeroBadge=?",[nub])
                                    print("Utente disattivato con successo!")
                                except sqlite3.Error as error:
                                    print("Failed to insert data into sqlite table: ", error)
                                finally:
                                    cursore.close()
                                    break
                        if s == 2:
                            with conn:
                                cursore = conn.cursor()
                                try:
                                    cursore.execute("DELETE FROM [Utente] WHERE NumeroBadge=?",[nub])
                                    print("Utente eliminato con successo!")
                                except sqlite3.Error as error:
                                    print("Failed to insert data into sqlite table: ", error)
                                finally:
                                    cursore.close()
                                    break
                        if s == 3:
                            break



                    

                else:
                    print("Devi essere amministratore per accedere a questa sezione!!!")
            else:
                print("Questo numero badge non esiste!")


        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table: ", error)

        finally:
            cursore.close()    

def controlloValidita(val): #CONTROLLA SE BADGE ANCORA VALIDO (CALCOLA CHE I GIORNI DALLA CREAZIONE SIANO < DI 180)
    with conn:
        cursore = conn.cursor() #CREO CURSORE
    try:
        cursore.execute("""SELECT DataRinnovo FROM [Utente] WHERE NumeroBadge=?""",[val]) 
        okdate = cursore.fetchall() #RESTITUISCO TUTTE LE RIGHE

        crea = datetime.datetime.strptime(okdate[0][0],date_format) #NEL DUBBIO LA RIFORMATTO , MA E' ABBASTANZA INUTILE
        
    except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
    finally:
        cursore.close()
        
    oggi = datetime.datetime.now().strftime(date_format) #VERIFICA CHE IL BADGE NON SIA SCADUTO  IN BASE ALLA DATA DELL' ULTIMO RINNOVO
    oggi = datetime.datetime.strptime(oggi,date_format) #DATETIME CORRENTE
    differenza = GIORNI_DI_VALIDITA - abs((oggi - crea).days) #CALCOLA DIFFERENZA TRA CREAZIONE E OGGI
    
    with conn:
        cursore = conn.cursor() #CREO CURSORE
    try:
        cursore.execute("SELECT Validita FROM [Utente] WHERE NumeroBadge=?",[val]) 
        ok = cursore.fetchone() #RESTITUISCO TUTTE LE RIGHE
        
    except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
    finally:
        cursore.close()

    if ok[0] == 0:
        print("Il suo badge è disattivato!")
        return False

    if  differenza <=0:
        print("Il suo badge è scaduto! Lo rinnovi al più presto!")
        with conn:
            cursore = conn.cursor()
            try:
                cursore.execute("UPDATE [Utente] SET Validita=False WHERE NumeroBadge=?",[val]) #SEGNA NON VALIDO IN CASO SIA SCADUTO

            except sqlite3.Error as error:
                print("Failed to insert data into sqlite table", error)
            finally:
                cursore.close()
        return False
    else:
        return True    

def AccessoStanza(colore):
    numero = int(input('Inserire numero Badge: ')) #ACCESSO AI TORNELLI CONTROLLO SE ESISTE O ACCESSO GIA' FATTO
    
    with conn:
        cursore = conn.cursor()
        try:
            cursore.execute("SELECT NumeroBadge FROM [Utente]") #TROVA IL NUMERO BADGE
            ok = cursore.fetchall()
            cont = 0
            for i in range(len(ok)):
                if numero == ok[i][0]:
                    cont = cont +1
            if cont >= 1:

                cursore.execute("SELECT Presenza FROM [Utente] WHERE NumeroBadge=?",[numero])
                va = cursore.fetchone()
                if va[0] == 1:      #VERIFICO ESISTENZA NUMERO BADGE

                    data = datetime.datetime.now().strftime(date_format)
                    cursore.execute("SELECT  [Ruolo].IdRuolo From [Ruolo] JOIN [UtenteRuolo] ON [UtenteRuolo].IdRuolo=[Ruolo].IdRuolo JOIN [Utente] ON [Utente].IdUtente=[UtenteRuolo].IdUtente WHERE [Utente].NumeroBadge=?",[numero])
                    roli = cursore.fetchall()  #TROVO RUOLO/I UTENTE
                    cont = 0
                    for i in range(len(roli)):
                        cursore.execute("SELECT Permesso FROM [Permessi] WHERE IdRuolo=? AND IdStanza=?",[roli[i][0], colore])
                        rol = cursore.fetchone()
                        if rol[0] == 1:
                            cont = cont + 1 #CONTROLLO SE HA IL PERMESSO DI ENTRARE

                    if cont >0:
                        cursore.execute("SELECT EntrataUscita FROM [Accessi] WHERE IdUtente=(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?) AND IdStanza=? ORDER BY IdAccesso DESC",[numero,colore])
                        acc = cursore.fetchone() #CONTROLLO SE STA ENTRANDO O USCENDO

                        if acc== None:
                            cursore.execute("SELECT IdStanza FROM [Accessi] WHERE IdUtente=(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?)  AND EntrataUscita='Entrata'  ORDER BY IdAccesso DESC",[numero])
                            idstanz = cursore.fetchone() #CONTROLLO SE ERA ANCORA PRESENTE IN UN ALTRA STANZA E SEGNO USCITA
                            if idstanz != None:
                                if str(idstanz[0]) != colore:
                                    cursore.execute("INSERT INTO [Accessi] (IdStanza, IdUtente, Quando, EntrataUscita) VALUES (?,(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?),?,'Uscita')",[idstanz[0],numero,data])
                            
                            cursore.execute("INSERT INTO [Accessi] (IdStanza, IdUtente, Quando, EntrataUscita) VALUES (?,(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?),?,'Entrata')",[colore,numero,data])
                            cursore.execute("SELECT Cognome FROM Utente WHERE NumeroBadge=?",[numero])
                            d = cursore.fetchone()
                            print(f"Ben Arrivato Sig. {d[0]}!")

                        else:

                            if str(acc[0]) == 'Uscita':
                                cursore.execute("SELECT IdStanza FROM [Accessi] WHERE IdUtente=(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?) AND EntrataUscita='Entrata' ORDER BY IdAccesso DESC",[numero])
                                idstanz = cursore.fetchone()
                                if idstanz != None: #CONTROLLO SE ERA ANCORA PRESENTE IN UN ALTRA STANZA E SEGNO USCITA
                                    if idstanz[0] != colore:
                                        cursore.execute("INSERT INTO [Accessi] (IdStanza, IdUtente, Quando, EntrataUscita) VALUES (?,(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?),?,'Uscita')",[idstanz[0],numero,data])
                                
                                cursore.execute("INSERT INTO [Accessi] (IdStanza, IdUtente, Quando, EntrataUscita) VALUES (?,(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?),?,'Entrata')",[colore,numero,data])
                                cursore.execute("SELECT Cognome FROM Utente WHERE NumeroBadge=?",[numero])
                                d = cursore.fetchone()
                                time.sleep(0.5)
                                print('.',end=' ',flush=True)
                                time.sleep(0.5)
                                print('.',end=' ',flush=True)
                                time.sleep(0.5)
                                print('.',flush=True)
                                print(f"Ben Arrivato Sig. {d[0]}!") #SCRIVO I DATI DELL'ACCESSO

                            else:
                                   
                                cursore.execute("INSERT INTO [Accessi] (IdStanza, IdUtente, Quando, EntrataUscita) VALUES (?,(SELECT IdUtente FROM [Utente] WHERE NumeroBadge=?),?,'Uscita')",[colore,numero,data])
                                cursore.execute("SELECT Cognome FROM Utente WHERE NumeroBadge=?",[numero])
                                d = cursore.fetchone()
                                time.sleep(0.5)
                                print('.',end=' ',flush=True)
                                time.sleep(0.5)
                                print('.',end=' ',flush=True)
                                time.sleep(0.5)
                                print('.',flush=True)
                                print(f"Arrivederci Sig. {d[0]}!")
                    else:
                        print("Non hai il permesso di entrare in questa stanza!!!")
                else:
                    print("Non hai Effettuato l'accesso al tonello!")

            else:
                print("Questo numero badge non esiste!")
                    
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
        finally:
            cursore.close()

def clearAll():
    with conn:
        cursore = conn.cursor()
        try:
            sql_delete_query1 = """DELETE from Accessi """
            sql_delete_query2 = """DELETE from Operazioni """
            cursore.execute(sql_delete_query1)
            cursore.execute(sql_delete_query2)
            print("Tutti i dati sono stati cancellati ")
        finally:
            cursore.close()
            
            
def escidalprogramma():
    print('Arrivederci')
    exit()
          
    

def main ():

    while True:
        print(' \n ( 1 ) Entra nel Tornello\n ( 2 ) Esci dal Tornello\n ( 3 ) Crea Nuovo Badge\n ( 4 ) Rinnova Badge\n ( 5 ) Nuova Stanza\n ( 6 ) Nuovo Ruolo\n ( 7 ) Nuovo permesso Stanza/Ruolo\n ( 8 ) Gestisci Utenti\n ( 9 ) Pulisci i dati nel database\n ( 10 ) Esci')
        scelta = int(input("-> "))
        if scelta>=1 and scelta<=10:
            if scelta == 1:
                if accesso() == True:
                    while True:
                        with conn:
                            cursore = conn.cursor()
                            cursore.execute("SELECT Nome FROM [Stanza]")
                            nomi = cursore.fetchall()
                        print("\n")
                        for i in range(len(nomi)):
                            print(f' ( {i+1} ) Entra/Esci nella stanza '+nomi[i][0])
                        print(" ( 0 ) Esci dal Tornello")

                        s = int(input("-> "))
                        if s>=0 and s<=i+1:
                            if s == 0:
                                uscita()
                                break
                            else:
                                AccessoStanza(s)
            if scelta == 2:
                uscita()

            if scelta == 3:
                nuovoBadge()
            
            if scelta == 4:
                rinnova()

            if scelta == 5:
                nuovaStanza()
            
            if scelta == 6:
                nuovoRuolo()

            if scelta == 7:
                nuoviPermessi()
            
            if scelta == 8:
                gestisciUtente()
                
            if scelta == 9:
                clearAll()    
                
            if scelta == 10:
                escidalprogramma()

main()