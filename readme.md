# Listings API

API endpoint written in Flask with PostgreSQL that returns a GeoJSON FeatureCollection of real estate listings based on the query string of the request.  [Hosted on Heroku](http://open-the-door.herokuapp.com/listings?min_price=100000&max_price=200000&min_bed=2&max_bed=2&min_bath=2&max_bath=2).


#### Possible query fields (all are optional):

- min_price: minimum listing price in dollars
- max_price: maximum listing price in dollars
- min_bed: minimum # of bedrooms
- max_bed: maximum # of bedrooms
- min_bath: minimum # of bathrooms
- max_bath: maximum # of bathrooms
- status: active, pending or sold
- page: page number of listing results, defaults to 1 if per_page_max given without page
- per_page_max: maximum # of results per page, defaults to 100 if page number given without per_page_max

#### Example queries:

[http://open-the-door.herokuapp.com/listings?min_price=100000&max_price=200000&min_bed=2&max_bed=2&min_bath=2&max_bath=2](http://open-the-door.herokuapp.com/listings?min_price=100000&max_price=200000&min_bed=2&max_bed=2&min_bath=2&max_bath=2)
will produce all listings with price between $100,000 and $200,000 (inclusive), 2 bedrooms, and 2 bathrooms. [View on map](https://gist.github.com/anonymous/9fe9e236f8ad5bac6d5c).

[http://open-the-door.herokuapp.com/listings?min_price=100000&max_price=200000&min_bed=2&max_bed=2&min_bath=2&max_bath=2&status=active](http://open-the-door.herokuapp.com/listings?min_price=100000&max_price=200000&min_bed=2&max_bed=2&min_bath=2&max_bath=2&status=active)
will produce all listings with price between $100,000 and $200,000 (inclusive), 2 bedrooms, 2 bathrooms, and a status of active. [View on map](https://gist.github.com/anonymous/98a225b4b376da661b91).

[http://open-the-door.herokuapp.com/listings?min_price=100000&max_price=200000&min_bed=2&max_bed=2&min_bath=2&max_bath=2&per_page_max=50](http://open-the-door.herokuapp.com/listings?min_price=100000&max_price=200000&min_bed=2&max_bed=2&min_bath=2&max_bath=2&per_page_max=50)
will produce the first 50 listings with price between $100,000 and $200,000 (inclusive), 2 bedrooms, and 2 bathrooms with links to the rest of the results. [View on map](https://gist.github.com/anonymous/31f80ed7677472a7914b).

#### Pagination

If either page or per_page_max is specified in the query string, the results will be limited to the per_page_max value and pagination links will be added to the result following the [JSON API specification for pagination](http://jsonapi.org/format/#fetching-pagination).

#### Color

Results also have a "marker-color" property set according to the listing status (active = green, pending = yellow, sold = red) which will set the marker color on certain GeoJSON mapping sites, including [geojson.io](http://geojson.io).

#### Tests

The test suite tests validity of GeoJSON by sending the results of various queries to the [GeoJSONLint](http://www.geojsonlint) validation endpoint.  It tests for correctness of queries by verifying counts against the results of direct SQL queries.  Presence and correctness of pagination links, and correctness of status and color information is also tested.

#### Areas for Improvement / Next Steps

- Add other CRUD functions
- Add authorization tokens (necessary before implementing Create, Update, and Delete)
- Add more info about each listing to database (pictures, taxes, etc.) and add capability to access each listing individually:  /listings/id
- Improve Tests
- Nitpick:  Figure out if Listing.id is supposed to be an int or a string and make code consistent.  The id values in the CSV seemed to be integers, the problem description specified id as a string.  My code currently stores the id as an int and then casts to a string in the GeoJSON feature.  

#### Notes

I had a lot of fun doing this.  It's the first Flask app I've written (other than HelloWorld -- I've used Ruby for all previous web stuff) and once I got Flask to play nicely with Postgres and figured out the SQLAlchemy syntax, it went very smoothly....except for the scary moment when I got my points to display on a map for the first time and saw that they were all in Antarctica!  












