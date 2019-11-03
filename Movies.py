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
        self.all_columns = []
        for column in self.table_columns_info:
            self.all_columns.append(column[1])
        self.last_fetch = 0
        self.cur.execute('SELECT TITLE FROM MOVIES')
        titles = self.cur.fetchall()
        self.all_titles = []
        for title in titles:
            self.all_titles.append(title[0])
            
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
        it = iter(self.all_columns)
        next(it)
        next(it)
        index=0
        for column in it:
            if len(dictionary['Year'])>4:
                dictionary['Year'] = re.search("^\d{4}", dictionary['Year']).group(0)
            try:
                x = dictionary[all_criteria[index]]
            except KeyError:
                x = 'N/A'


            try:
                self.cur.execute("""UPDATE MOVIES SET {} = ? WHERE TITLE = ?""".format(column),(x, dictionary['Title']))
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
            
    def sort_database(self, columns={'ID':'ASC'}, titles=0, default='ASC',out=0):
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
            self.cur.execute(command)
            self.last_fetch = self.cur.fetchall()
        elif data == 'NomOsc':
            self.cur.execute("SELECT TITLE, AWARDS FROM MOVIES WHERE AWARDS LIKE 'Nomi%Oscar%';")
            self.last_fetch = self.cur.fetchall()
        else:
            x = '"{}"'.format(column)
            self.cur.execute("SELECT TITLE, {} FROM MOVIES WHERE instr({}, ?)".format(column, x), (data,))
            self.last_fetch = self.cur.fetchall()
        if out:
            for row in self.last_fetch:
                print(row)
    def add_movie_to_database(self, title):
        if title not in self.all_titles:
            self.cur.execute("INSERT INTO MOVIES (TITLE) VALUES(?);",(title,))
            self.update_single_movie(title)
            self.all_titles.append(title)
    def find_with_regex(self, regex, compared_movies=0):
        command = "SELECT TITLE, AWARDS FROM MOVIES WHERE "
        if compared_movies:
            for title in compared_movies:
                command += 'TITLE = "{}" OR '.format(title)
            command = command[:-4]
            print(command)
            self.cur.execute(command)
        else:
            self.cur.execute("SELECT TITLE, AWARDS FROM MOVIES")
        self.last_fetch = self.cur.fetchall()
        expression = re.compile(regex)
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
        if len(all_awards)>0:
            max_val = max(all_awards.values())
        else:
            max_val = 0
        best = {}
        for key in all_awards:
            if all_awards[key] == max_val:
                best[key] = all_awards[key]
        return best
            
    def compare_movies(self, attribute, compared_ones=0, out=0):
        all_found = {}
        if attribute == 'MOST_NOMINATIONS':
            all_found = self.find_with_regex('\d+ nomina', compared_ones)
        elif attribute == 'ALL_AWARDS':
            all_found = self.find_with_regex('\d+ win', compared_ones)
        elif attribute == 'OSCARS':
            all_found = self.find_with_regex('on \d+ Osc', compared_ones)
        elif compared_ones:
            self.sort_database({attribute:'DESC'}, compared_ones)
            all_found[self.last_fetch[0][0]] = str(self.last_fetch[0][1])
        else:
            self.sort_database({attribute:'DESC'})
            all_found[self.last_fetch[0][0]] = str(self.last_fetch[0][1])
        return all_found

    def high_scores(self):
        print("| Column | Movie | Value |\n|--------|-------|-------| ")
        x = self.compare_movies('RUNTIME')
        for key in x:
            print("| Runtime | {} | {} |".format(key,x[key]))
        x = self.compare_movies('BOX_OFFICE')
        for key in x:
            print("| Box_ office | {} | {} |".format(key,x[key]))
        x = self.compare_movies('MOST_NOMINATIONS')
        for key in x:
            print("| Nominations | {} | {} |".format(key,x[key]))
        x = self.compare_movies('ALL_AWARDS')
        for key in x:
            print("| Wins | {} | {} |".format(key,x[key]))
        x = self.compare_movies('OSCARS')
        for key in x:
            print("| Oscars | {} | {} |".format(key,x[key]))
        x = self.compare_movies('IMDb_Rating')
        for key in x:
            print("| IMDB Rating | {} | {} |".format(key,x[key]))
Movies = Movies_Info("movies.sqlite")
print(sys.argv)
sys.argv = ['Objective.py', '--compare', 'oscars', 'Memento', 'Fight Club']
if sys.argv[1] == '--sort_by':
    if '--defasc' in sys.argv:
        default = 'ASC'
    else:
        default = 'DESC'
    given_columns = {}
    last = 0
    for argument in sys.argv[2:]:
        argument = argument.upper()
        if argument == 'DESC' or argument == 'ASC':
            if last and last in Movies.all_columns:
                given_columns[last] = argument
                continue
        elif argument in Movies.all_columns:
            given_columns[argument.upper()] = default
            last = argument
    Movies.sort_database(given_columns)
    to_print = "| Title |"
    for column in given_columns:
        to_print += " %s |"
    print(to_print % tuple(given_columns.keys()))
    for movie in Movies.last_fetch:
        to_print = "|"
        data = []
        i = 0
        for column in movie:
            to_print += " %s |"
            data.append(str(column))
            i+=1
        print(to_print % tuple(data))
#        column[0] +"|"+str(column[1]) +"|"+str(column[2]))
elif sys.argv[1] == '--filter_by':
    Movies.filtered_data(sys.argv[2].upper(), str(sys.argv[3]))
    print("| Title | {} |".format(sys.argv[2]))
    for row in Movies.last_fetch:
        print("| {} | {} |".format(row[0], row[1]))
elif sys.argv[1] == '--compare':
    print("| Title | {} |".format(sys.argv[2]))
    x = Movies.compare_movies(sys.argv[2].upper(), sys.argv[3:])
    for movies in x.keys():
        print("| {} | {} |".format(movies, x[movies]))
elif sys.argv[1] == '--add':
    for arg in sys.argv[2:]:
        Movies.add_movie_to_database(arg)
elif sys.argv[1] == '--highscores':
    Movies.high_scores()
elif sys.argv[1] == '--update':
    Movies.update_database()
Movies.database.commit()    