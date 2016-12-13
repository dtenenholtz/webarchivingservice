About
------
This is a basic information service that allows users to archive web sites, capturing sites on a time-based frequency. It implements [Flask](http://flask.pocoo.org/), [Flask-RESTful](http://flask-restful.readthedocs.org/en/latest/), and [JSON-LD](http://json-ld.org/). A user can take the following actions:

-   Add a `<DomainArchive>` resource to the `<DomainList>`
-   Create an `<ArchivePlan>` for a given `<DomainArchive>`, and also update or delete it if needed.
-   View records of any created `<SnapShot>` for a given `<DomainArchive>`

Data Model
-------------
The service is designed with four resource classes (`<DomainList>`, `<DomainArchive>`, `<ArchivePlan>`, and `<SnapShot>`).  It uses a single vocabulary to describe a [Collection](http://pcdm.org/models#Collection/) and an [Object](http://pcdm.org/models#Object/) as per the [Portland Common Data Model](http://pcdm.org/models#).  See the full data model as a  [Graph Diagram](https://www.lucidchart.com/documents/view/41c50efb-2ce9-4d33-9509-52cdf08eb25c) to view the way these four resources are linked togther through the `rdfs:member` property.

Properties
-----------
The `<DomainList>` is a list resource that has as a `rdfs:member` various archive resource classes. The other three resource classes each have properties as follows:


For a `<DomainArchive>`:
-   URL
-   createdate
-   title
-   description
-   owner
-   @id
-   @type


For an `<ArchivePlan>`:
-   frequency
-   depth
-   @type
-   @id

For a `<SnapShot>`:
-   size
-   runtime
-   date
-   filename
-   @type
-   @id

Vocabularies
------------
We use the schema.org vocabularies to express conceptually what the properties of each resource mean.
- any URL is expressed as `@type: http://schema.org/url`
- any date is expressed as `@type: http://www.w3.org/2001/XMLSchema#`


Setup and running the service (assuming a bash terminal and GNU/Linux OS)
----------------------------

1. Install required dependencies (`python3.x`, `pip`, `virtualenv`, `Flask`, and `Flask-RESTful`, then run this command:
   ```
   $ pip install -r requirements.txt
   ``` 
   
2. `cd` to the directory where you extracted the webarchivingservice project to, and activate your `virtualenv` with the command 
    ```
    . venv/bin/activate
    ```
3. Start the server:
   ```
   $ python server.py
   ```




