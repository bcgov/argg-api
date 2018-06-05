from flask import Flask, Response, jsonify, request, redirect, url_for, g
from jinja2 import Template
from . import settings
import bcdc
import emailer
import os
import json
import requests
import logging


app = Flask(__name__)

#setup logging
app.logger.setLevel(getattr(logging, settings.LOG_LEVEL)) #main logger's level

#inject some initial log messages
app.logger.info("Initializing {}".format(__name__))
app.logger.info("Log level is '{}'".format(settings.LOG_LEVEL))
 

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

API_SPEC_FILENAME = os.path.join(app.root_path, "..\\docs\\argg-api.openapi3.json")

#------------------------------------------------------------------------------
# API Endpoints
#------------------------------------------------------------------------------

@app.route('/')
def api():
  """
  Summary information about this API
  """
  with open(API_SPEC_FILENAME) as f:
    s = f.read()
    r = Response(response=s, mimetype='application/json', status=200)
    return r

@app.route('/register', methods=["POST"])
def register():
  """
  Post a new API to be registered
  """

  #headers
  contentType = request.headers.get('Content-Type')

  #check content type of request req_data
  if not contentType or contentType != "application/json":
    return jsonify({"msg": "Invalid Content-Type.  Expecting application/json"}), 400

  #get request req_data
  try:
    req_data = request.get_json()
  except Error as e:
    return jsonify({"msg": "content req_data is not valid json"}), 400

  try:
    req_data = clean_and_validate_req_data(req_data)
  except ValueError as e:
    return jsonify({"msg": "{}".format(e)}), 400

  success_resp = {}

  #create a draft metadata record (if one doesn't exist yet)
  if not req_data.get("existing_metadata_url"):
    package = None
    try:
      package = create_package(req_data)
      if not package:
        raise ValueError("Unknown reason")
      #add info about the new metadata record to the response
      success_resp["new_metadata_record"] = {
        "id": package["id"],
        "web_url": bcdc.package_id_to_web_url(package["id"]),
        "api_url": bcdc.package_id_to_web_url(package["id"])
      }
    except ValueError as e: #perhaps other errors are possible too??  if so, catch those too
      app.logger.error("Unable to create metadata record in the BC Data Catalog. {}".format(e))
      return jsonify({"msg": "Unable to create metadata record in the BC Data Catalog. {}"}), 500
  
    try:
      create_api_root_resource(package["id"], req_data)
    except ValueError as e: #perhaps other errors are possible too??  if so, catch those too
      app.logger.warn("Unable to create API root resource associated with the new metadata record. {}".format(e))
  
    try:
      create_api_spec_resource(package["id"], req_data)
    except ValueError as e: #perhaps other errors are possible too??  if so, catch those too
      app.logger.warn("Unable to create API spec resource associated with the new metadata record. {}".format(e))

    try:
      #TODO: support pre-existing package too.
      send_notification_email(req_data, package["id"])
    except Exception as e: #perhaps other errors are possible too??  if so, catch those too
      app.logger.error("Unable to send notification email. {}".format(e))

  return jsonify(success_resp), 200

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def clean_and_validate_req_data(req_data):

  #ensure req_data folder hierarchy exists
  if not req_data:
    req_data = {}
  if not req_data.get("metadata_details"):
    req_data["metadata_details"] = {}
  if not req_data["metadata_details"].get("owner"):
    req_data["metadata_details"]["owner"] = {}
  if not req_data["metadata_details"].get("security"):
    req_data["metadata_details"]["security"] = {}
  if not req_data["metadata_details"].get("license"):
    req_data["metadata_details"]["license"] = {}
  if not req_data["metadata_details"].get("submitted_by_person"):
    req_data["metadata_details"]["submitted_by_person"] = {}
  if not req_data.get("existing_api"):
    req_data["existing_api"] = {}
  if not req_data.get("gateway"):
    req_data["gateway"] = {}

  #check that required fields are present
  if not req_data["metadata_details"].get("title"):
    raise ValueError("Missing '$.metadata_details.title'")
  if not req_data["metadata_details"].get("description"):
    raise ValueError("Missing '$.metadata_details.description'")

  if not req_data["metadata_details"]["owner"].get("org_id"):
    raise ValueError("Missing '$.metadata_details.owner.org_id'")
  if not req_data["metadata_details"]["owner"].get("sub_org_id"):
    raise ValueError("Missing '$.metadata_details.owner.sub_org_id'")  
  
  if not req_data["metadata_details"]["security"].get("download_audience"):
    raise ValueError("Missing '$.metadata_details.security.download_audience'")
  if not req_data["metadata_details"]["security"].get("view_audience"):
    raise ValueError("Missing '$.metadata_details.security.view_audience'")
  if not req_data["metadata_details"]["security"].get("metadata_visibility"):
    raise ValueError("Missing '$.metadata_details.security.metadata_visibility'")
  if not req_data["metadata_details"]["security"].get("security_class"):
    raise ValueError("Missing '$.metadata_details.security.security_class'")

  if not req_data["metadata_details"]["license"].get("license_id"):
    raise ValueError("Missing '$.metadata_details.license.license_id'")

  if not req_data["metadata_details"]["submitted_by_person"].get("name"):
    raise ValueError("Missing '$.metadata_details.submitted_by_person.name'")
  if not req_data["metadata_details"]["submitted_by_person"].get("org_id"):
    raise ValueError("Missing '$.metadata_details.submitted_by_person.org_id'")
  if not req_data["metadata_details"]["submitted_by_person"].get("sub_org_id"):
    raise ValueError("Missing '$.metadata_details.submitted_by_person.sub_org_id'")
  if not req_data["metadata_details"]["submitted_by_person"].get("business_email"):
    raise ValueError("Missing '$.metadata_details.submitted_by_person.business_email'")

  if not req_data["existing_api"].get("base_url"):
    raise ValueError("Missing '$.existing_api.base_url'")

  if not req_data["gateway"].get("use_gateway"):
    raise ValueError("Missing '$.gateway.use_gateway'")

  #clean fields
  req_data["metadata_details"]["title"] = req_data["metadata_details"]["title"].title()

  return req_data

def create_package(req_data):
  """
  Registers a new package with BCDC
  :param req_data: the req_data of the http request to the /register resource
  """
  package_dict = {
    "title": req_data["metadata_details"].get("title"),
    "name": bcdc.prepare_package_name(req_data["metadata_details"].get("title")),
    "org": req_data["metadata_details"]["owner"].get("org_id"),
    "sub_org": req_data["metadata_details"]["owner"].get("sub_org_id"),
    "owner_org": req_data["metadata_details"]["owner"].get("sub_org_id"),
    "notes": req_data["metadata_details"].get("description"),
    "groups": [{"id" : settings.BCDC_GROUP_ID}],
    "state": "active",
    "resource_status": req_data["metadata_details"].get("status", "completed"),
    "type": "WebService",
    "tag_string": "API",
    "tags": [{"name": "API"}],
    "sector": "Service",
    "edc_state": "DRAFT",
    "download_audience": req_data["metadata_details"]["security"].get("download_audience"),
    "view_audience":  req_data["metadata_details"]["security"].get("view_audience"),
    "metadata_visibility": req_data["metadata_details"]["security"].get("metadata_visibility"),
    "security_class": req_data["metadata_details"]["security"].get("security_class"),
    "license_id": req_data["metadata_details"]["license"].get("license_id"),
#    "license_title": req_data["metadata_details"]["license"].get("license_title"), #auto added if license_id is specified
#    "license_url": "http://www2.gov.bc.ca/gov/content/home/copyright", #auto added if license_id is specified
    "contacts": [
      {
        "name": req_data["metadata_details"]["submitted_by_person"].get("name"),
        "organization": req_data["metadata_details"]["submitted_by_person"].get("org_id"),
        "branch": req_data["metadata_details"]["submitted_by_person"].get("sub_org_id"),
        "email": req_data["metadata_details"]["submitted_by_person"].get("business_email"),
        "role": req_data["metadata_details"]["submitted_by_person"].get("role", "pointOfContact"),
        "private": req_data["metadata_details"]["submitted_by_person"].get("private", "Display")
      }
    ]
  }

  package = bcdc.package_create(package_dict, api_key=settings.BCDC_API_KEY)
  app.logger.debug("Created metadata record: {}".format(settings.TARGET_EMAIL_ADDRESSES))
  return package

def create_api_root_resource(package_id, req_data):
  """
  Adds a new resource to the given package.  The new resource represents the base URL of the API.
  :param package_id: the id of the package to add the resource to.
  :param req_data: the req_data of the request to /register as a dictionary
  :return: the new resource
  """
  
  #download api base url and check its content type (so we can create a 'resource' 
  #with the appropriate content type)
  r = requests.get(req_data["existing_api"]["base_url"])
  format = "text"
  if r.status_code < 400:
    resource_content_type = r.headers['content-type']
    format = content_type_to_format(resource_content_type, "text")

  #add the "API root" resource to the package
  resource_dict = {
    "package_id": package_id, 
    "url": req_data["existing_api"]["base_url"],
    "format": format, 
    "name": "API root"
  }
  resource = bcdc.resource_create(resource_dict, api_key=settings.BCDC_API_KEY)
  return resource

def create_api_spec_resource(package_id, req_data):
  """
  Adds a new resource to the given package.  The new resource represents the API spec.
  This function fails does nothing and returns None if $.existing_api.openapi_spec_url is not
  present in req_data.
  :param package_id: the id of the package to add the resource to.
  :param req_data: the body of the request to /register as a dictionary
  :return: the new resource
  """

  if req_data["existing_api"].get("openapi_spec_url"):
    resource_dict = {
      "package_id": package_id, 
      "url": req_data["existing_api"]["openapi_spec_url"],
      "format": "openapi-json",
      "name": "API specification"
    }
    resource = bcdc.resource_create(resource_dict, api_key=settings.BCDC_API_KEY)
    return resource

  return None

def send_notification_email(req_data, package_id):
  """
  Sends a notification email
  """

  emailer.send_email(
    settings.TARGET_EMAIL_ADDRESSES, \
    email_subject="New API Registered - {}".format(req_data["metadata_details"]["title"]), \
    email_body=prepare_email_body(req_data, package_id), \
    smtp_server=settings.SMTP_SERVER, \
    smtp_port=settings.SMTP_PORT, \
    from_email_address=settings.FROM_EMAIL_ADDRESS, \
    from_password=settings.FROM_EMAIL_PASSWORD)
  app.logger.debug("Sent notification email to: {}".format(settings.TARGET_EMAIL_ADDRESSES))


def prepare_email_body(req_data, package_id):
  """
  Creates the body of the notification email
  :param req_data: the body of the request to /register as a dictionary
  :param package_id: a BCDC metadata package id
  """

  css_filename = "css/bootstrap.min.css"

  with open(css_filename, 'r') as css_file:
    css=css_file.read().replace('\n', '')  

  template = Template("""
  <html>
  <head>
  <style>
  """
  +css+
  """
  .table-condensed {font-size: 12px;}
  </style>
  </head>
  <title>A new API has been registered</title>
  <body>
  <div class="container">
  <h2>A new API has been registered</h2>

  <table class="table table-condensed">
    <tr>
      <th>Title</th>
      <td>{{req_data["metadata_details"]["title"]}}</td>
    </tr>
    <tr>
      <th>Description</th>
      <td>{{req_data["metadata_details"]["description"]}}</td>
    </tr>
    <tr>
      <th>Metadata record</th>
      <td><a href="{{metadata["web_url"]}}">{{metadata["id"]}}</a></td>
    </tr>
    <tr>
      <th>Submitted by</th>
      <td>
        {{req_data["metadata_details"]["submitted_by_person"]["name"]}}<br/>
        {{req_data["metadata_details"]["submitted_by_person"]["business_email"]}}<br/>
        {{req_data["metadata_details"]["submitted_by_person"]["business_phone"]}}<br/>
        Role: {{req_data["metadata_details"]["submitted_by_person"]["role"]}}
      </td>
    </tr>
    <tr>
      <th>API root</th>
      <td><a href="{{req_data["existing_api"]["base_url"]}}">{{req_data["existing_api"]["base_url"]}}</a></td>
    </tr>
    <tr>
      <th>OpenAPI specification</th>
      <td>
        {% if req_data["existing_api"]["openapi_spec_url"] %}
          <a href="{{req_data["existing_api"]["openapi_spec_url"]}}">{{req_data["existing_api"]["openapi_spec_url"]}}</a>
        {% else %}
          None
        {% endif %}
      </td>
    </tr>
    <tr>
      <th>Use API gateway?</th>
      <td>
        {% if req_data["gateway"]["use_gateway"] %}
          Yes
        {% else %}
          No
        {% endif %}
      </td>
    </tr>
  </table>

  </div>
  </body>
  </html>
  """
  )

  params = {
    "req_data": req_data,
    "metadata": {
      "id": package_id,
      "web_url": bcdc.package_id_to_web_url(package_id)
    }
  }
  html = template.render(params)
  return html

def content_type_to_format(content_type, default=None):
  """
  Converts a content type (aka mine type, as would appear in the Content-Type header 
  of an HTTP request or response) into corresponding ckan resource string (html, json, xml, etc.)
  """
  if content_type.startswith("text/html"):
    return "html"
  if content_type.startswith("application/json"):
    return "json"
  if "xml" in content_type:
    return "xml"
  return default