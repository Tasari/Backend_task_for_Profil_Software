import Movies

testobject = Movies.Movies_Info("movies.sqlite")

def updating(Movie):
    testobject.update_single_movie(Movie)
    testobject.cur.execute('SELECT * FROM MOVIES WHERE TITLE = ?', (Movie,))
    fetch = testobject.cur.fetchall()[0]
    return fetch

def test_update():
    assert None not in updating("Fargo")
    assert None not in updating("Memento")
    assert None not in updating("Fight Club")
    assert None not in updating("The Green Mile")

def test_sort():
    testobject.sort_database({"Year":'DESC'})
    assert testobject.last_fetch[0][1] == 2019
    testobject.sort_database({"IMDb_Rating":'ASC', "Runtime":'DESC'}, ["Room", "Shazam", "Warrior", "Chinatown"])
    assert testobject.last_fetch[0][1] < testobject.last_fetch[3][1]
    assert int(testobject.last_fetch[0][2][:-4]) > int(testobject.last_fetch[3][2][:-4])

def test_filters():
    testobject.filtered_data('Language', 'Spanish')
    for movie in testobject.last_fetch:
        assert "Spanish" in movie[1]
    testobject.filtered_data('NomOsc', "NomOsc")
    for movie in testobject.last_fetch:
        assert "Nominated for " in movie[1]
    testobject.filtered_data("Income", 'Income')
    for movie in testobject.last_fetch:
        string = movie[1].replace(",", "")
        string = string.replace("$", "")  
        assert int(string) > 100000000
    testobject.filtered_data("CAST", "Charles")
    for movie in testobject.last_fetch:
        assert "Charles" in movie[1]
    testobject.filtered_data("Director", 'Kubrick')
    for movie in testobject.last_fetch:
        assert 'Kubrick' in movie[1]
    x = testobject.filtered_data("Ratio", "Ratio")
    for movie in testobject.last_fetch:
        score = x[movie[0]]
        print(score)
        assert score > 0.8

def test_comprasion():
    assert testobject.compare_movies('OSCARS',["Coco", "Moonlight", "Gods"]) == {"Moonlight":3}
    assert testobject.compare_movies('MOST_NOMINATIONS', ["Gods", "La La Land", "Kac Wawa"]) == {"La La Land":254}
    assert testobject.compare_movies('All_awards', ["Gods", "La La Land", "Kac Wawa"]) == {"La La Land":215}
    assert testobject.compare_movies('IMDb_Rating') == {"The Shawshank Redemption" : '9.3'}
    assert testobject.compare_movies("Box_office", ['The Dark Knight', 'Gone with the Wind']) == {'The Dark Knight':"$533,316,061"}
    assert testobject.compare_movies('Runtime', ['The Dark Knight', 'Gone with the Wind']) == {"Gone with the Wind":"238 min"}
def test_adding():
    testobject.add_movie_to_database("Kung Pow: Enter the Fist")
    assert "Kung Pow: Enter the Fist" in testobject.all_titles


