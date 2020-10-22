def createTable():
    try:
        cur=db.cursor()
        cur.execute('''CREATE TABLE users (
                       UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT (20) NOT NULL,
                       password TEXT (20) NOT NULL
                       );''')
        print ('Tabela criada com sucesso')
    except:
        db.rollback()