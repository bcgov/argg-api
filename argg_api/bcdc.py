import json
import requests
import re
from . import settings

def package_create(package_dict, api_key=None):
  """
  Creates a new package (dataset) in BCDC
  :param package_dict: a dictionary with all require package properties
  :param user: the username to create the package under
  :param password: the password associated with the user
  """
  url = "{}{}/action/package_create".format(settings.BCDC_BASE_URL, settings.BCDC_API_PATH)
   
  headers = {
    "Content-Type": "application/json",
    "Authorization": api_key
  }
  r = requests.post(url, 
    data=json.dumps(package_dict),
    headers=headers
    )

  if r.status_code >= 400:
    raise ValueError("{} {}".format(r.status_code, r.text))
#  r.raise_for_status()
#  print(r.text)
  
  #get the response object
  response_dict = json.loads(r.text)
  assert response_dict['success'] is True
  created_package = response_dict['result']

  return created_package


def package_delete(package, api_key):
  """
  deletes a package
  """
  url = "{}{}/action/package_delete".format(settings.BCDC_BASE_URL, settings.BCDC_API_PATH)
   
  headers = {
    "Content-Type": "application/json",
    "Authorization": api_key
  }
  data={
    "id": package["id"]
  }
  r = requests.post(url, 
    data=json.dumps(data),
    headers=headers
    )
  
  if r.status_code >= 400:
    raise ValueError("{} {}".format(r.status_code, r.text))

def resource_create(resource_dict, api_key=None):
  """
  Creates a new resource associated with a given package
  :param package_id: the id of the package to associate the resource with
  :param url: the url of the resource
  """
  url = "{}{}/action/resource_create".format(settings.BCDC_BASE_URL, settings.BCDC_API_PATH)
   
  headers = {
    "Content-Type": "application/json",
    "Authorization": api_key
  }
  r = requests.post(url, 
    data=json.dumps(resource_dict),
    headers=headers
    )

  if r.status_code >= 400:
    raise ValueError("{} {}".format(r.status_code, r.text))
#  r.raise_for_status()
#  print(r.text)
  
  #get the response object
  response_dict = json.loads(r.text)
  assert response_dict['success'] is True
  created_package = response_dict['result']

  return created_package

def package_id_to_web_url(package_id):
  """
  the web url needed to access a given package
  """
  return "{}/dataset/{}".format(settings.BCDC_BASE_URL, package_id)

def package_id_to_api_url(package_id):
  """
  the web url needed to access a given package
  """
  return "{}{}/action/package_show?id={}".format(settings.BCDC_BASE_URL, settings.BCDC_API_PATH, package_id)

def prepare_package_name(s):
  s = s.lower()
  s = re.sub('[\W\s]+', '-', s)
  return s