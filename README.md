About
------
This is a basic information service that allows users to archive web sites, capturing sites on a time-based frequency. It implements [Flask](http://flask.pocoo.org/), [Flask-RESTful](http://flask-restful.readthedocs.org/en/latest/), and [JSON-LD](http://json-ld.org/). A user can take the following actions:

-   Add a `<DomainArchive>` resource to the `<DomainList>`
-   Create an `<ArchivePlan>` for a given `<DomainArchive>`, and also update or delete it if needed.
-   View records of any created `<SnapShot>` for a given `<DomainArchive>`

Data Model
-------------
The service is designed with four resource classes (`<DomainList>`, `<DomainArchive>`, `<ArchivePlan>`, and `<SnapShot>`), as defined in `webarch_vocab.ttl`.  A single vocabulary, the [Portland Common Data Model](http://pcdm.org/models#), describes a [Collection](http://pcdm.org/models#Collection/) and an [Object](http://pcdm.org/models#Object/).  The Collection class describes the `<DomainList>` and the `<DomainArchive>`, while the Object class describes the `<ArchivePlan>` and the `<SnapShot>`. See the full data model as a  [Graph Diagram](https://www.lucidchart.com/documents/view/41c50efb-2ce9-4d33-9509-52cdf08eb25c) to view the way these four resources are linked togther through the `rdfs:member` property.

Properties
-----------
The `<DomainList>` is a list resource that has as a `rdfs:member` various archive resource classes. The other three resource classes each have properties as follows:


For a `<DomainArchive>`:
-   URL
-   createdate
-   title
-   description
-   owner
-   @type
-   @id


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
We use assorted schema.org, W3C, and [dcterms](http://purl.org/dc/terms/) vocabularies to express conceptually what the properties of each resource mean.

-   any URL is expressed as `@type: http://schema.org/url`
-   any literal with a datetime datatype is expressed as `@type: https://www.w3.org/TR/xmlschema11-2/#dateTime`
-   any createdate for a new resource is expressed as `@type: http://schema.org/dateCreated`
-   a user that submits a domain to be archived is expressed as `@type: http://schema.org/creator`
-   the title given by a user to a domain is expressed as `@type: http://schema.org/name`
-   the description of a domain, provided by the user, is expressed as `@type: http://schema.org/description`
-   the "runtime" for a snapshot capture is expressed as `@type: http://schema.org/Duration`
-   the "depth" property for an archive plan is expressed as `@type: http://schema.org/depth`
-   the "cycle" or "frequency" of snapshot capturing is expressed as `@type: http://purl.org/dc/terms/accrualPeriodicity`
-   the "filename" for a `.warc` file is expressed as `@type: http://schema.org/name`
-   the "size" for any associated `.warc` file created by a snapshot is expressed as `@type: http://schema.org/fileSize`


Setup and running the service (assuming a bash terminal and GNU/Linux OS)
----------------------------

1. Install required dependencies (`python3.x`, `pip`, `virtualenv`, `Flask`, and `Flask-RESTful`, then create a virtualenv with the command:
    ```
    $ virtualenv venv
    ```

2.  `cd` to the directory where you extracted the webarchivingservice project to, and activate your `virtualenv` with the command 
    ```
    $ . venv/bin/activate
    ```
3. Start the server:   
    ```
    $ python server.py
    ```

That's it!
