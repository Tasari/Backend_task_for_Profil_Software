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
        self.cur.execute('PRAGMA table_info(MOVIES)')
        self.table_columns_info = self.cur.fetchall()
        print(self.table_columns_info)

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
        if Title.endswith(' '):
            target = Title[:-1]
            self.cur.execute("""UPDATE MOVIES SET TITLE = ? WHERE TITLE = ?""",(target, Title))
        request = requests.get("http://www.omdbapi.com/", 
        params = {"t":Title, "apikey":"b88afbe7"}, 
        )
        dictionary = ast.literal_eval(request.text)
        all_criteria = ('Year', 'Runtime', 'Genre', 'Director', 'Actors', 'Writer', 'Language', 'Country', 'Awards', 'imdbRating', 'imdbVotes', 'BoxOffice')           
        it = iter(self.table_columns_info)
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
    def sort_database(self, columns={'ID':'ASC'}):
        '''
        Sorting database by multiple columns, main column is given as argument
        '''
        command = "SELECT * FROM MOVIES ORDER BY "
        for col in columns.keys():
            if col == 'BOX_OFFICE':
                added_condition = "CAST(REPLACE(SUBSTR({},2), ',', '') AS FLOAT) {}, ".format(col, columns[col])
            elif col == 'RUNTIME':
                added_condition = "CAST({} AS UNSIGNED) {}, ".format(col, columns[col])
            elif col == 'IMDb_votes':
                added_condition = 'CAST(REPLACE({}, ",", "") AS UNSIGNED) {}, '.format(col, columns[col])
            else:
                added_condition = "{} {}, ".format(col, columns[col])
            command += added_condition
        command = command[:-2] + ';'
        print(command)
        self.cur.execute(command)
        rows = self.cur.fetchall()
        for row in rows:
            print(row)
    def filtered_data(self, column, data):
        if data == 'Ratio':
            movies_with_good_ratio = []
            x = '"{}"'.format(column)
            self.cur.execute("SELECT TITLE, AWARDS FROM MOVIES")
            all_movies_awards = self.cur.fetchall()
            i = 0
            for movie_award in all_movies_awards:
                all_numbers = []
                for word in movie_award[1].split():
                    print(type(word))
                    if word.isdigit():
                        all_numbers.append(word)
                    print(all_numbers)
     #           if len(all_numbers)>1:  
                print(movie_award[0])  
                ratio = int(all_numbers[len(all_numbers)-2])/int(all_numbers[len(all_numbers)-1])
                print(ratio)

                if ratio > 0.8:
                    movies_with_good_ratio.append(all_movies_awards[i][0])
                i+=1
            print(movies_with_good_ratio)
        elif data == 'Income':
            self.cur.execute("SELECT TITLE, BOX_OFFICE FROM MOVIES")
            rows = self.cur.fetchall()
            high_income = []
            for row in rows:
                income = row[1]
                x = income.replace("$", "")
                z = x.replace(",", "")
                if income != 'N/A':
                    if int(z) > 100000000:
                        high_income.append(row[0])
            print(high_income)
        else:
            x = '"{}"'.format(column)
            print(x)
            self.cur.execute("SELECT * FROM MOVIES WHERE instr({}, ?)".format(x), (data,))
            rows = self.cur.fetchall()
            for row in rows:
                print(row)


Movies = Movies_Info("movies.sqlite")
Movies.update_database()
#Movies.sort_database({'IMDb_Rating':'DESC', 'IMDb_votes':'DESC' })
Movies.filtered_data('AWARDS', 'Income')


