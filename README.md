## Required libraries:
* Requests
## Functions:
1. Updating database using titles of movies
   * "python Movies.py --update"
2. Sorting Movies by multiple columns
   * "python Movies.py --sort_by Column1 (ASC/DESC) Column2 (ASC/DESC)"
   ASC sorts ascending, DESC - descending, those arguments are optional
   by default it sorts Columns descending, you can change that by adding optional argument '--defasc'
3. Filtering movies:
    * "python Movies.py --filter_by [filter] [condition]"
    Possible filters are:
    * Director
    * Language
    * Cast (1 letter is enough for it to work)
    * Ratio (Won/Nominated), no condition needed
    * NomOsc (Nominated for oscars, but not winners), no condition 
    * Income (If income was bigger than 100,000,000$), no condition 
4. Comparing multiple movies (Shows only winner in given category) by:
   * "python Movies.py --compare_by [condition]
   * possible conditions are:
   * IMDb_Rating
   * Box_Office
   * All_awards (most wins)
   * Oscars (most wins)
   * Most_nominations (most nominations)
   * Runtime
5. Adding movies to database:
   * "python Movies.py --add "Movie1" "Movie2""
   movies are automatically updated after adding
6. Showing highscores in:
   * "python Movies.py --highscores"
   * Runtime
   * Box Office
   * Most Awards Won
   * Most Oscars Won
   * Highest IMDB Rating
