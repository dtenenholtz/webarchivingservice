from flask import (Flask, Response, request, render_template, make_response,
                   redirect)
from flask.ext.restful import Api, Resource, reqparse, abort

import json
import string
import random
from functools import wraps
from datetime import datetime

'''
# Define our priority levels.
# These are the values that the "priority" property can take on a help request.
PRIORITIES = ('closed', 'low', 'normal', 'high')
'''

# Load data from disk.
# This simply loads the data from our "database," which is just a JSON file.
with open('data.jsonld') as data:
    data = json.load(data)

'''
# Check that username and password are OK; DON'T DO THIS FOR REAL
def check_auth(username, password):
    return username == 'admin' and password == 'secret'


# Issue an authentication challenge
def authenticate():
    return Response(
        'Please authenticate yourself', 401,
        {'WWW-Authenticate': 'Basic realm="helpdesk"'})


# Decorator for methods that require authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
'''

# Generate a unique ID for each new Archive.
# By default this will consist of six lowercase numbers and letters.
def generate_id(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Respond with 404 Not Found if no help request with the specified ID exists.
def error_if_domainlist_not_found(domainlist_id):
    if domainlist_id not in data['domainlists']:
        message = "No help request with ID: {}".format(domainlist_id)
        abort(404, message=message)


# Filter and sort a list of domainlists.
def filter_and_sort_domainlists(query='', sort_by='time'):

    # Returns True if the query string appears in the help request's
    # title or description.
    def matches_query(item):
        (domainlist_id, domainlist) = item
        text = domainlist['title'] + domainlist['description']
        return query.lower() in text

    # Returns the help request's value for the sort property (which by
    # default is the "time" property).
    def get_sort_value(item):
        (domainlist_id, domainlist) = item
        return domainlist[sort_by]

    filtered_domainlists = filter(matches_query, data['domainlists'].items())

    return sorted(filtered_domainlists, key=get_sort_value, reverse=True)


# Given the data for a help request, generate an HTML representation
# of that help request.
def render_domainlist_as_html(domainlist):
    return render_template(
        'domainlist+microdata+rdfa.html',
        domainlist=domainlist,
        priorities=reversed(list(enumerate(PRIORITIES))))


# Given the data for a list of help requests, generate an HTML representation
# of that list.
def render_domainlist_list_as_html(domainlists):
    return render_template(
        'domainlists+microdata+rdfa.html',
        domainlists=domainlists,
        priorities=PRIORITIES)


# Raises an error if the string x is empty (has zero length).
def nonempty_string(x):
    s = str(x)
    if len(x) == 0:
        raise ValueError('string is empty')
    return s


# Specify the data necessary to create a new help request.
# "from", "title", and "description" are all required values.
new_domainlist_parser = reqparse.RequestParser()
for arg in ['from', 'title', 'description']:
    new_domainlist_parser.add_argument(
        arg, type=nonempty_string, required=True,
        help="'{}' is a required value".format(arg))


# Specify the data necessary to update an existing help request.
# Only the priority and comments can be updated.
update_domainlist_parser = reqparse.RequestParser()
update_domainlist_parser.add_argument(
    'priority', type=int, default=PRIORITIES.index('normal'))
update_domainlist_parser.add_argument(
    'comment', type=str, default='')


# Specify the parameters for filtering and sorting help requests.
# See `filter_and_sort_domainlists` above.
query_parser = reqparse.RequestParser()
query_parser.add_argument(
    'query', type=str, default='')
query_parser.add_argument(
    'sort_by', type=str, choices=('priority', 'time'), default='time')

class DomainList(Resource):

    def get(self, domainlist_id):
        error_if_domainlist_not_found(domainlist_id)
        return make_response(
            render_domainlist_as_html(
                data['domainlist'][domainlist_id]), 200)

    def post(self):
        domainlist = new_domainlist_parser.parse_args()
        domainlist_id = generate_id()
        domainlist['@id'] = 'request/' + domainlist_id
        domainlist['@type'] = 'helpdesk:HelpRequest'
        domainlist['time'] = datetime.isoformat(datetime.now())
        data['domainlists'][domainlist_id] = domainlist
        return make_response(
            render_domainlist_list_as_html(
                filter_and_sort_domainlists()), 201)

class DomainListAsJSON(Resource):

    def get(self, domainlist_id):
        error_if_domainlist_not_found(domainlist_id)
        domainlist = data['domainlists'][domainlist_id]
        domainlist['@context'] = data['@context']
        return domainlist

class DomainArchive(Resource):
    def get(self):
        query = query_parser.parse_args()
        return make_response(
            render_domainlist_list_as_html(
                filter_and_sort_domainlists(**query)), 200)

    def post(self):
        domainarchive = new_domainarchive_parser.parse_args()
        domainarchive_id = generate_id()
        domainarchive['@id'] = 'request/' + domainarchive_id
        domainarchive['@type'] = 'helpdesk:HelpRequest'
        domainarchive['time'] = datetime.isoformat(datetime.now())
        domainarchive['priority'] = PRIORITIES.index('normal')
        data['domainarchives'][domainarchive_id] = domainarchive
        return make_response(
            render_domainlist_list_as_html(
                filter_and_sort_domainlists()), 201)

class DomainArchiveAsJSON(Resource):

    def get(self):
        return data

class ArchivePlan(Resource):

    def get(self, domainlist_id):
        error_if_domainlist_not_found(domainlist_id)
        return make_response(
            render_domainlist_as_html(
                data['domainlist'][domainlist_id]), 200)

    def put(self, ):

    def delete(self, ):


class SnapShot(Resource):

    def get(self):
        query = query_parser.parse_args()
        return make_response(
            render_domainlist_list_as_html(
                filter_and_sort_domainlists(**query)), 200)


'''
class Greeting(Resource):
    def get(self, role):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, default='Akira')
        args = parser.parse_args()
        print(args)
        return make_response(
            render_template('greeting.html', role=role, **args))

roles = set()


class Greetings(Resource):
    def get(self):
        return make_response(
            render_template('greetings.html', roles=roles))

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('role', type=str)
        args = parser.parse_args()
        print(args)
        roles.add(args['role'])
        return make_response(
            render_template('greetings.html', roles=roles), 201)

'''


# Assign URL paths to our resources.
app = Flask(__name__)
api = Api(app)
'''
# api.add_resource(HelpRequestList, '/requests')
api.add_resource(HelpRequestListAsJSON, '/requests.json')
api.add_resource(HelpRequest, '/request/<string:domainlist_id>')
api.add_resource(HelpRequestAsJSON, '/request/<string:domainlist_id>.json')
api.add_resource(Greeting, '/greeting/<string:role>')
api.add_resource(Greetings, '/greetings')
'''
api.add_resource(DomainList, '/domains/<string:domainlist_id>')
api.add_resource(DomainListAsJSON, '/domains/<string:domainlist_id>.json')
api.add_resource(DomainArchive, '/domains/<string:domainarchive_id>')
api.add_resource(HelpRequestAsJSON, '/request/<string:domainlist_id>.json')
api.add_resource(Greeting, '/greeting/<string:role>')
api.add_resource(Greetings, '/greetings')

# Redirect from the index to the list of help requests.
@app.route('/')
def index():
    return redirect(api.url_for(HelpRequestList), code=303)


# This is needed to load JSON from Javascript running in the browser.
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# Start the server.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
