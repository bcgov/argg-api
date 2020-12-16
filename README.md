# argg-api

<img src="https://github.com/bcgov/argg-ui/workflows/Package%20for%20Dev/badge.svg"></img>
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=argg-ui&metric=alert_status)](https://sonarcloud.io/dashboard?id=argg-ui)
[![img](https://img.shields.io/badge/Lifecycle-Dormant-ff7f2a)](https://github.com/bcgov/repomountie/blob/master/doc/lifecycle-badges.md)

The REST API for the API Registration Generator (ARGG) application.

This API supports one REST endpoint: POST /register_api, which accepts
details about an API to be registered.  The endpoint then creates a new metadata
record in the BC Data Catalog and sends a notification email to alert DataBC to
coordinate with the API owner to perform any setup needed for the newly-registered
API.

## Run in docker

  docker build -t argg-api .
  docker run -p8000:8000 --rm --env-file .env argg-api

### Application environment

The application reads all its application settings from environment variables.  
The following environment variables are supported:

```
#Values: ERROR, WARN, INFO, DEBUG
LOG_LEVEL 

#Base url of the BC Data Catalog.  e.g. "https://cad.data.gov.bc.ca"
BCDC_BASE_URL
#Relative path of BC Data Catalog API.  e.g. "/api/3"
BCDC_API_PATH
#The BC Data Catalog API Key to be used for creating new metadata records
BCDC_API_KEY
#The ID of the group to add all new metadata records to
BCDC_GROUP_ID

#The organization to that new metadata records will be initially associated with
BCDC_PACKAGE_OWNER_ORG_ID
#The sub-organization to that new metadata records will be initially associated with
BCDC_PACKAGE_OWNER_SUB_ORG_ID

#The SMTP server to send notification emails through.  e.g. apps.smtp.gov.bc.ca
SMTP_SERVER
#The SMTP server port to use.  e.g. 587
SMTP_PORT
#The "sender" email address from notification emails. e.g. data@gov.bc.ca
FROM_EMAIL_ADDRESS
#The password for the FROM_EMAIL_ADDRESS account.
FROM_EMAIL_PASSWORD
#A csv list of recipient email addresses for notification emails.
TARGET_EMAIL_ADDRESSES
```

If the application is run in a docker container, the above environment variables
must be injected into the container on startup.

# License
```
Copyright 2018 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
