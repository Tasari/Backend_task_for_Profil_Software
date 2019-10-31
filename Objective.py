import sqlite3
from sqlite3 import Error
import requests
import ast

class Movies_Info:
    def __init__(self, database):
        conn = None
        try:
            conn = sqlite3.connect(database)
        except Error as e:
            print(e)
        self.database = conn
        self.cur = conn.cursor()

    def print_database(self):
        '''
        Print all rows in the tasks table
        '''
        self.cur.execute("SELECT * FROM MOVIES")
        rows = self.cur.fetchall()
        for row in rows:
            print(row)

    def update_single_movie(self, Title):
        '''
        Updating single movie in database
        '''
        request = requests.get("http://www.omdbapi.com/", 
        params = {"t":Title, "apikey":"b88afbe7"}, 
        )
        dictionary = ast.literal_eval(request.text)
        self.cur.execute('PRAGMA table_info(MOVIES)')
        table_columns_info = self.cur.fetchall()
        all_criteria = ('Year', 'Runtime', 'Genre', 'Director', 'Actors', 'Writer', 'Language', 'Country', 'Awards', 'imdbRating', 'imdbVotes', 'BoxOffice')           
        it = iter(table_columns_info)
        next(it)
        next(it)
        index=0
        for column in it:
            try:
                x = dictionary[all_criteria[index]]
            except KeyError:
                x = 'N/A'
            try:
                self.cur.execute("""UPDATE MOVIES SET {} = ? WHERE TITLE = ?""".format(column[1]),(x, dictionary['Title']))
                index+=1
            except Error as e:
                print(e)
                index+=1

    def update_database(self):
        '''
        Updating all movies in database with info from IMDb
        '''
        self.cur.execute("SELECT * FROM MOVIES")
        rows = self.cur.fetchall()
        for row in rows:
            self.update_single_movie(row[1])




Movies = Movies_Info("movies.sqlite")
Movies.update_database()
Movies.print_database()

