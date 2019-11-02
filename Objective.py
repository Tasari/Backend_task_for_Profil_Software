import sqlite3
from sqlite3 import Error
import requests
import ast
import re
import sys
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
        self.last_fetch = 0
        print(self.table_columns_info)

    def print_database(self):
        '''
        Print all rows in the tasks table
        '''
        self.cur.execute("SELECT * FROM MOVIES")
        self.last_fetch = self.cur.fetchall()
        for row in self.last_fetch:
            print(row)

    def print_last_fetch(self):
        for row in self.last_fetch:
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
            
    def sort_database(self, columns={'ID':'ASC'}, titles=0, out=0):
        '''
        Sorting database by multiple columns, main column is given as argument
        '''
        string=''
        for table_col in columns.keys():
            if table_col == 'CAST':
                x = '"{}"'.format(table_col)
                string += '{}, '.format(x)
            else:
                string += '{}, '.format(table_col)
        string = string[:-2] + ' '
        command = "SELECT TITLE, {}FROM MOVIES ".format(string)
        if titles:
            command += 'WHERE '
            for title in titles:
                command += 'TITLE = "{}" OR '.format(title)
            command = command[:-3]
        command += 'ORDER BY '
        for col in columns.keys():
            if col == 'BOX_OFFICE':
                added_condition = "CAST(REPLACE(SUBSTR({},2), ',', '') AS FLOAT) {}, ".format(col, columns[col])
            elif col == 'RUNTIME':
                added_condition = "CAST({} AS UNSIGNED) {}, ".format(col, columns[col])
            elif col == 'IMDb_votes':
                added_condition = 'CAST(REPLACE({}, ",", "") AS UNSIGNED) {}, '.format(col, columns[col])
            elif col == 'CAST':
                x = '"{}"'.format(col)
                added_condition = '{} {}, '.format(x, columns[col])
            else:
                added_condition = "{} {}, ".format(col, columns[col])
            command += added_condition

        command = command[:-2] + ';'
        self.cur.execute(command)
        self.last_fetch = self.cur.fetchall()
        if out: 
            for row in self.last_fetch:
                print(row)

    def filtered_data(self, column, data, out=0):
        if data == 'Ratio':
            movies_with_good_ratio = {}
            x = '"{}"'.format(column)
            self.cur.execute("SELECT TITLE, AWARDS FROM MOVIES")
            all_movies_awards = self.cur.fetchall()
            i = 0
            for movie_award in all_movies_awards:
                all_numbers = []
                for word in movie_award[1].split():
                    if word.isdigit():
                        all_numbers.append(word)
                if len(all_numbers)>1:  
                    ratio = int(all_numbers[len(all_numbers)-2])/int(all_numbers[len(all_numbers)-1])
                if ratio > 0.8:
                    movies_with_good_ratio[all_movies_awards[i][0]]=ratio
                i+=1
            command = "SELECT TITLE FROM MOVIES WHERE "
            for movie_with_good_ratio in movies_with_good_ratio.keys():
                command = command + "TITLE = '{}' OR ".format(movie_with_good_ratio)
            command = command[:-4]+";"
            print(command)
            self.cur.execute(command)
            self.last_fetch = self.cur.fetchall()
            if out:
                for row in self.last_fetch:
                    print(row[0] + " Ratio: " + str(movies_with_good_ratio[row[0]]))
        elif data == 'Income':
            self.cur.execute("SELECT TITLE, BOX_OFFICE FROM MOVIES")
            rows = self.cur.fetchall()
            high_income = {}
            for row in rows:
                income = row[1]
                x = income.replace("$", "")
                z = x.replace(",", "")
                if income != 'N/A':
                    if int(z) > 100000000:
                        high_income[row[0]]=income
            command = "SELECT TITLE, BOX_OFFICE FROM MOVIES WHERE "
            for high_income_movie in high_income.keys():
                command = command + "TITLE = '{}' OR ".format(high_income_movie)
            command = command[:-4]+";"
            print(command)
            self.cur.execute(command)
            self.last_fetch = self.cur.fetchall()
        elif data == 'NomOsc':
            self.cur.execute("SELECT TITLE, AWARDS FROM MOVIES WHERE AWARDS LIKE 'Nomi%Oscar%';")
            self.last_fetch = self.cur.fetchall()
        else:
            x = '"{}"'.format(column)
            print(x)
            self.cur.execute("SELECT TITLE, {} FROM MOVIES WHERE instr({}, ?)".format(column, x), (data,))
            self.last_fetch = self.cur.fetchall()
        if out:
            for row in self.last_fetch:
                print(row)
    def add_movie_to_database(self, title):
        self.cur.execute("INSERT INTO MOVIES (TITLE) VALUES(?);",(title,))
        self.update_single_movie(title)

    def find_with_regex(self, regex, compared_movies=0):
        command = "SELECT TITLE, AWARDS FROM MOVIES WHERE "
        if compared_movies:
            for title in compared_movies:
                command += 'TITLE = "{}" OR '.format(title)
                command = command[:-4]
            self.cur.execute(command)
        else:
            self.cur.execute("SELECT TITLE, AWARDS FROM MOVIES")
        self.last_fetch = self.cur.fetchall()
        expression = re.compile(regex)
        print(expression)
        all_awards = {}
        for row in self.last_fetch:
            found = expression.findall(row[1])
            if len(found):
                words = found[0].split()
                for word in words:
                    try:
                        all_awards[row[0]] = int(word)
                    except ValueError:
                        pass
        max_val = max(all_awards.values())
        best = {}
        for key in all_awards:
            if all_awards[key] == max_val:
                best[key] = all_awards[key]
        return best
            
    def compare_movies(self, attribute, compared_ones=0):
        if attribute == 'MOST_NOMINATIONS':
            all_found = self.find_with_regex('\d+ nomina', compared_ones)
            print(all_found)
        elif attribute == 'ALL_AWARDS':
            all_found = self.find_with_regex('\d+ win', compared_ones)
            print(all_found)
        elif attribute == 'OSCARS':
            all_found = self.find_with_regex('on \d+ Osc', compared_ones)
            print(all_found)
        elif compared_ones:
            self.sort_database({attribute:'DESC'}, compared_ones)
            print(self.last_fetch[0])
        else:
            self.sort_database({attribute:'DESC'})
            print(self.last_fetch[0])

    def high_scores(self):
        self.compare_movies('RUNTIME')
        self.compare_movies('BOX_OFFICE')
        self.compare_movies('MOST_NOMINATIONS')
        self.compare_movies('ALL_AWARDS')
        self.compare_movies('OSCARS')
        self.compare_movies('IMDb_Rating')
Movies = Movies_Info("movies.sqlite")
Movies.update_database()
if sys.argv[1] == '--sort_by':
    given_columns = {}
    for argument in sys.argv[2:]:
        given_columns[argument.upper()] = 'DESC'
    Movies.sort_database(given_columns)
    for column in Movies.last_fetch:
        print(column[0] +"|"+str(column[1]))
