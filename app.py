from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import and_, between
import math
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'os.environ['DATABASE_URL']
db = SQLAlchemy(app)


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(30))
    status = db.Column(db.String(7))
    price = db.Column(db.Integer)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    sqft = db.Column(db.Integer)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)


@app.route('/')
def hello_world():
    """to test app is running"""
    return "hello world!"


@app.route('/listings')
def get_listings():
    """return GeoJSON Feature Collection based on url query string"""
    filter_params = create_filter(request.args)
    results = Listing.query.filter(and_(*filter_params)).all()
    if request.args.get('page') or request.args.get('per_page_max'):  #optional pagination arguments
        page = int(request.args.get('page', 1))
        max_per_page = int(request.args.get('per_page_max', 100))
        count = len(results)
        results = results[((page-1)*max_per_page):(page*max_per_page)]
        links = create_links(count, page, max_per_page, request.url)
        return geo_json_feature_collection(results, links)
    else:
        return geo_json_feature_collection(results)


def create_filter(args):
    """creates SQL query parameters based on parsed query string"""
    conditions = []
    conditions.append(create_clause(args.get('min_price'), args.get('max_price'), Listing.price))
    conditions.append(create_clause(args.get('min_bed'), args.get('max_bed'), Listing.bedrooms))
    conditions.append(create_clause(args.get('min_bath'), args.get('max_bath'), Listing.bathrooms))
    if args.get('status'):
        conditions.append(Listing.status == args.get('status'))
    conditions[:] = (c for c in conditions if c is not None)
    return conditions


def create_clause(min_val, max_val, column):
    """returns correct ==, between, <=, >= filter clause based on min_val and max_val"""
    if min_val:
        if min_val == max_val:
            return column == int(min_val)
        elif max_val:
            return between(column, int(min_val), int(max_val), True)
        else:
            return column >= int(min_val)
    elif max_val:
        return column <= int(max_val)
    else:
        return None


def geo_json_feature(listing):
    """returns a jsonable object that conforms to GeoJSON specifications for a single listing"""
    status_colors = {"sold":"FF0000", "pending":"FFFF00", "active":"009900"}
    result = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates":[listing.lng, listing.lat]
        },
        "properties": {
            "id": str(listing.id), #problem description specifies that id is string
            "price": listing.price,
            "street": listing.street,
            "bedrooms": listing.bedrooms,
            "bathrooms": listing.bathrooms,
            "sq_ft": listing.sqft,
            "status": listing.status,
            "marker-color": status_colors[listing.status]
        }
    }
    return result


def geo_json_feature_collection(listings, links=None):
    """turns results of listings query into GeoJSON Feature Collection"""
    features = [geo_json_feature(listing) for listing in listings]
    collection = {"type": "FeatureCollection", "features": features}
    if links:
        collection.update(links)
    return jsonify(**collection)


def create_links(num_results, page, max_per_page, orig_url):
    """helper function for optional pagination arguments
       creates first, last, prev, and last links as specified in
       http://jsonapi.org/format/#fetching-pagination
       returns dict with page and links keys"""

    if "page={0}".format(page) not in orig_url:
        orig_url = orig_url+"&page={0}".format(page)
    link_hash = {'links':{}}
    link_hash['page'] = page
    last_page = int(math.ceil(num_results/float(max_per_page)))
    link_hash['links']['first'] = orig_url.replace("page={0}".format(page), "page=1")
    if last_page > 1:
        link_hash['links']['last'] = (
            orig_url.replace("page={0}".format(page), "page={0}".format(last_page)))
    if page > 1:
        link_hash['links']['prev'] = (
            orig_url.replace("page={0}".format(page), "page={0}".format(page-1)))
    if page < last_page:
        link_hash['links']['next'] = (
            orig_url.replace("page={0}".format(page), "page={0}".format(page+1)))
    return link_hash


if __name__ == '__main__':
    app.run(debug=True)

