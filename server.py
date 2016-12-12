from flask import (Flask, Response, request, render_template, make_response,
                   redirect)
from flask_restful import Api, Resource, reqparse, abort

import json
import string
import random
# from functools import wraps
from datetime import datetime

'''
# Define our capture frequency.
# These are the values that the "cycle" property can take on an archive plan.
CYCLE = ('daily', 'weekly', 'bi-weekly', 'monthly', 'quarterly')

#Define depth of capture (number of jumps within the site's domain from the origin page)
# The
DEPTH = int('0:4')
'''

# Load data from disk.
# This simply loads the data from our "database," which is just a JSON file.
with open('archive_data.jsonld') as data:
    data = json.load(data)

# Generate a unique ID for each new instance of an Archive Plan, Domain, or Snapshot.
# By default this will consist of six lowercase numbers and letters.
def generate_id(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Respond with 404 Not Found if no Domain with the specified ID exists.
def error_if_webdomains_not_found(webdomains_id):
    if webdomains_id not in data['webdomains']:
        message = "No URL Archive with ID: {}".format(webdomains_id)
        abort(404, message=message)

def error_if_archives_not_found(archives_id):
    if archives_id not in data['archives']:
        message = "No Archive Item with ID: {}".format(archives_id)
        abort(404, message=message)

# Respond with 404 Not Found if no archive plan with specified ID exists.
def abort_if_archiveplan_not_found(archiveplan_id):
    if archiveplan_id not in data['archiveplan']:
        message = "No Archive Plan with ID: {}".format(archiveplan_id)
        abort(404, message=message)

# Filter and sort a list of webdomains.
def filter_and_sort_webdomains(query='', sort_by='time'):

    # Returns True if the query string appears
    # title or description.
    def matches_query(item):
        (webdomains_id, webdomains) = item
        text = webdomains['title'] + webdomains['description']
        return query.lower() in text

    # Returns the domain's value for the sort property (which by
    # default is the "time" property).
    def get_sort_value(item):
        (webdomains_id, webdomains) = item
        return webdomains[sort_by]

    filtered_webdomains = filter(matches_query, data['webdomains'].items())

    return sorted(filtered_webdomains, key=get_sort_value, reverse=True)

# Filter and sort a list of Archive Items.
def filter_and_sort_archives(query='', sort_by='time'):

    # Returns True if the query string appears in the help request's
    # title or description.
    def matches_query(item):
        (archives_id, domainarchive) = item
        text = domainarchive['title'] + domainarchive['description']
        return query.lower() in text

    # Returns the help request's value for the sort property (which by
    # default is the "time" property).
    def get_sort_value(item):
        (domainarchive_id, domainarchive) = item
        return domainarchive[sort_by]

    filtered_archives = filter(matches_query, data['webdomains'].items())

    return sorted(filtered_archives, key=get_sort_value, reverse=True)


# Given the data for an archive, generate an HTML representation
# of that help request.
def render_webdomains_as_html(webdomains):
    return render_template(
        'webdomains+microdata+rdfa.html',
        webdomains=webdomains,
        priorities=reversed(list(enumerate(CYCLE))))


# Given the data for a list of help requests, generate an HTML representation
# of that list.
def render_webdomains_list_as_html(webdomains):
    return render_template(
        'webdomains+microdata+rdfa.html',
        webdomains=webdomains,
        # priorities=PRIORITIES)


# Raises an error if the string x is empty (has zero length).
def nonempty_string(x):
    s = str(x)
    if len(x) == 0:
        raise ValueError('string is empty')
    return s


# Specify the data necessary to create a new help request.
# "from", "title", and "description" are all required values.
new_webdomains_parser = reqparse.RequestParser()
for arg in ['owner', 'title', 'description']:
    new_webdomains_parser.add_argument(
        arg, type=nonempty_string, required=True,
        help="'{}' is a required value".format(arg))


# Specify the data necessary to update an existing archives plan.
# Only the cycle and depth can be updated.
update_archivesplan_parser = reqparse.RequestParser()
update_archivesplan_parser.add_argument(
    'cycle', type=int, default=CYCLE.index('weekly'))
update_archivesplan_parser.add_argument(
    'depth', type=int, default=1)

'''
# Specify the parameters for filtering and sorting .
# See `filter_and_sort_archives` above.
query_parser = reqparse.RequestParser()
query_parser.add_argument(
    'query', type=str, default='')
query_parser.add_argument(
    # edit to parse archives
    # 'sort_by', type=str, choices=('depth', 'time'), default='time')
)
'''




class DomainList(Resource):

    def get(self, webdomains_id):
        error_if_webdomains_not_found(webdomains_id)
        return make_response(
            render_webdomains_as_html(
                data['webdomains'][webdomains_id]), 200)

    def post(self):
        webdomains = new_webdomains_parser.parse_args()
        webdomains_id = generate_id()
        webdomains['@id'] = 'domains/' + webdomains_id
        webdomains['@type'] = 'webarchive:DomainList'
        webdomains['time'] = datetime.isoformat(datetime.now())
        data['DomainList'][webdomains_id] = webdomains
        return make_response(
            render_webdomains_list_as_html(
                filter_and_sort_webdomains()), 201)

class DomainListAsJSON(Resource):

    def get(self, webdomains_id):
        error_if_webdomains_not_found(webdomains_id)
        webdomains = data['webdomains'][webdomains_id]
        webdomains['@context'] = data['@context']
        return webdomains

class DomainArchive(Resource):
    def get(self):
        query = query_parser.parse_args()
        return make_response(
            render_webdomains_list_as_html(
                filter_and_sort_webdomains(**query)), 200)

    def post(self):
        domainarchive = new_webdomains_parser.parse_args()
        domainarchive_id = generate_id()
        domainarchive['@id'] = 'domain/' + domainarchive_id
        domainarchive['@type'] = 'webarchive:DomainArchive'
        domainarchive['time'] = datetime.isoformat(datetime.now())
        # domainarchive['plan'] = ""
        data['domainarchives'][domailist_id] = domainarchive
        return make_response(
            render_webdomains_list_as_html(
                filter_and_sort_webdomains()), 201)

class DomainArchiveAsJSON(Resource):
    def get(self):
        return data

# define parsers for the 'cycle' and 'depth' inputs that a user supplies
depth_parser.reqparse.RequestParser()
depth_parser.add_argument['depth']

cycle_parser.reqparse.RequestParser()
cycle_parser.add_argument['cycle']


class ArchivePlan(Resource):
    def get(self, archiveplan_id):
        error_if_archiveplan_not_found(archiveplan_id)
        return make_response(
            render_archiveplan_as_html(
                data['archiveplan'][archiveplan_id], 200)
            )
        )

    def put():
        depth_args = depth_parser.parse_args()
        cycle_args = cycle_parser.parse_args()

        plan_cycle = {'cycle': cycle_args['cycle']}
        plan_depth = {'depth': depth_args['depth']}

        depth_to_update = data['archiveplan'][archiveplan_id].depth
        cycle_to_update = data['archiveplan'][archiveplan_id].cycle

    def delete(self, archiveplan_id):
        abort_if_archiveplan_not_found(archiveplan_id)
        del data['archiveplan'][archiveplan_id]
        return '', 204

class SnapShot(Resource):

    def get(self):
        query = query_parser.parse_args()
        return make_response(
            render_webdomains_list_as_html(
                filter_and_sort_webdomains(**query)), 200)


# Assign URL paths to our resources.
app = Flask(__name__)
api = Api(app)

api.add_resource(DomainList, '/domains/<string:webdomains_id>')
api.add_resource(DomainListAsJSON, '/domains/<string:webdomains_id>.json')
api.add_resource(DomainArchive, '/domains/<string:domainarchive_id>')
api.add_resource(DomainArchiveAsJSON, '/domains/<string:domainarchive_id>.json')
api.add_resource(ArchivePlan, '/plan/<string:plan_id>')
api.add_resource(SnapShotAsJson, '/capture/<string:snapshot_id>.json’)


# Redirect from the index to the list of domains.
@app.route('/')
def index():
    return redirect(api.url_for(DomainList), code=303)


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
