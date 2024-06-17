from app import app
from app.veiws import cnx, cursor

if __name__ == '__main__':
    app.run()
    cursor.close()
    cnx.close()
