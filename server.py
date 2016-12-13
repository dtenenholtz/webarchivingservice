from flask import (Flask, Response, request, render_template, make_response,
                   redirect)
from flask_restful import Api, Resource, reqparse, abort

import json
import string
import random
# from functools import wraps
from datetime import datetime

# parse new archive post request
archives_parser = reqparse.RequestParser()
archives_parser.add_argument("description", type=str, default='')
archives_parser.add_argument("owner", type=str, default='')
archives_parser.add_argument("url", type=str, default='')
archives_parser.add_argument("title", type=str, default='')
archives_parser.add_argument("cycle", type=str, default='')
archives_parser.add_argument("depth", type=str, default='')

#parse new snapshot post request
snapshot_parser = reqparse.RequestParser()
snapshot_parser.add_argument("size", type=str, default='')
snapshot_parser.add_argument("runtime", type=str, default='')
snapshot_parser.add_argument("filename", type=str, default='')

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
def abort_if_archiveplan_not_found(archive_id):
    if 'archiveplan' not in data['webdomains'][archive_id].keys():
        message = "No Archive Plan for archive: {}".format(archive_id)
        abort(404, message=message)

# Filter and sort a list of webdomains.
def filter_and_sort_webdomains(query='', sort_by='title'):

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
def filter_and_sort_archives(query='', sort_by='title'):

    # Returns True if the query string appears in the web archive's
    # title or description.
    def matches_query(item):
        (archives_id, domainarchive) = item
        text = domainarchive['title'] + domainarchive['description']
        return query.lower() in text

    # Returns the web archive's value for the sort property (which by
    # default is the "time" property).
    def get_sort_value(item):
        (domainarchive_id, domainarchive) = item
        return domainarchive[sort_by]

    filtered_archives = filter(matches_query, data['webdomains'].items())

    return sorted(filtered_archives, key=get_sort_value, reverse=True)


# Given the data for an archive, generate an HTML representation
# of that archive.
def render_as_html(pageData, page):
    if page == 'domainlist':
        return render_template(
            'domainList.html',
            webdomains=pageData)
    elif page == 'archive':
        return render_template(
            'archive.html',
            archive=pageData)
    elif page == 'plan':
        return render_template(
            'archivePlan.html',
            archive=pageData)

def render_snapshot_as_html(pageData, id):
    print(pageData['snapshots'][id])
    return render_template(
            'snapshot.html',
            archive=pageData,
            snapshot_id=id)

# Raises an error if the string x is empty (has zero length).
def nonempty_string(x):
    s = str(x)
    if len(x) == 0:
        raise ValueError('string is empty')
    return s


# Specify the data necessary to create a new web archive.
# "owner", "title", and "description" are all required values.
new_archive_parser = reqparse.RequestParser()
for arg in ['owner', 'url', 'title', 'frequency', 'description']:
    new_archive_parser.add_argument(
        arg, type=nonempty_string, required=True,
        help="'{}' is a required value".format(arg))

class DomainList(Resource):

    def get(self):
        #error_if_webdomains_not_found(webdomains_id)
        return make_response(
            render_as_html(
                data, 'domainlist'), 200)

    def post(self):
        newArchiveArgs = archives_parser.parse_args()
        newArchive = {"description": newArchiveArgs['description'], "owner": newArchiveArgs['owner'], "url": newArchiveArgs['url'], "title": newArchiveArgs['title']}
        newArchive_id = generate_id()
        newArchivePlan_id = generate_id()
        newArchive['@id'] = newArchive_id
        newArchive['@type'] = 'webarchive:DomainList'
        newArchive['createdate'] = datetime.isoformat(datetime.now())
        newArchive['archiveplan'] = {"@type": "webarchive:ArchivePlan", "@id": newArchivePlan_id, "depth": newArchiveArgs['depth'], "cycle": newArchiveArgs['cycle']}
        print(newArchive)
        data['webdomains'][newArchive_id] = newArchive
        return make_response(
            render_as_html(
                data, 'domainlist'), 200)




class DomainArchive(Resource):
    def get(self, archive_id):
        return make_response(
            render_as_html(
                data['webdomains'][archive_id], 'archive'), 200)

    def post(self, archive_id):
        newSnapShot = snapshot_parser.parse_args()
        newSnapShot_id = generate_id()
        newSnapShot['@id'] = newSnapShot_id
        newSnapShot['@type'] = 'webarchive:DomainArchive'
        newSnapShot['createdate'] = datetime.isoformat(datetime.now())
        data['webdomains'][archive_id][newSnapShot_id] = newSnapShot
        return '', 201

class DomainArchiveAsJSON(Resource):
    def get(self):
        return data

# define parsers for the 'cycle' and 'depth' inputs that a user supplies
archiveplan_parser = reqparse.RequestParser()
archiveplan_parser.add_argument('depth', type=str, default='')
archiveplan_parser.add_argument('cycle', type=str, default='')

#cycle_parser.add_argument['CYCLE']


class ArchivePlan(Resource):
    def get(self, archive_id):
        #abort_if_archiveplan_not_found(archiveplan_id)
        return make_response(
            render_as_html(
                data['webdomains'][archive_id], 'plan'), 200)

    def put(self, archive_id):

        archiveplan_args = archiveplan_parser.parse_args()

        if archiveplan_args['depth'] == '':
            data['webdomains'][archive_id]['archiveplan']['cycle'] = archiveplan_args['cycle']

        else:
            data['webdomains'][archive_id]['archiveplan']['depth'] = archiveplan_args['depth']

        return make_response(render_as_html(data['webdomains'][archive_id], 'plan'), 200)

    def delete(self, archive_id):
        abort_if_archiveplan_not_found(archive_id)
        del data['webdomains'][archive_id]['archiveplan']
        return '', 204

class SnapShot(Resource):

    def get(self, archive_id, snapshot_id):
        #query = query_parser.parse_args()
        return make_response(
            render_snapshot_as_html(data['webdomains'][archive_id], snapshot_id), 200)

# Assign URL paths to our resources.
app = Flask(__name__)
api = Api(app)

api.add_resource(DomainList, '/domains')
api.add_resource(DomainArchive, '/domains/<string:archive_id>')
api.add_resource(DomainArchiveAsJSON, '/domains/<string:domainarchive_id>.json')
api.add_resource(ArchivePlan, '/plan/<string:archive_id>')
api.add_resource(SnapShot, '/capture/<string:archive_id>/<string:snapshot_id>')

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
