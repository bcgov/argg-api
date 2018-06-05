"""
Purpose: load app settings from environment variables
"""
import os

# Logging
# -----------------------------------------------------------------------------

if not "LOG_LEVEL" in os.environ:
  LOG_LEVEL = "WARN"
else:
  LOG_LEVEL = os.environ['LOG_LEVEL']

# BC Data Catalog
# -----------------------------------------------------------------------------
if not "BCDC_BASE_URL" in os.environ:
  raise ValueError("Missing 'BCDC_BASE_URL' environment variable.")
else:
  BCDC_BASE_URL = os.environ['BCDC_BASE_URL']

if not "BCDC_API_PATH" in os.environ:
  raise ValueError("Missing 'BCDC_API_PATH' environment variable.")
else:
  BCDC_API_PATH = os.environ['BCDC_API_PATH']

if not "BCDC_API_KEY" in os.environ:
  raise ValueError("Missing 'BCDC_API_KEY' environment variable.")
else:
  BCDC_API_KEY = os.environ['BCDC_API_KEY']

if not "BCDC_GROUP_ID" in os.environ:
  raise ValueError("Missing 'BCDC_GROUP_ID' environment variable.")
else:
  BCDC_GROUP_ID = os.environ['BCDC_GROUP_ID']


# Email
# -----------------------------------------------------------------------------

if not "SMTP_SERVER" in os.environ:
  raise ValueError("Missing 'SMTP_SERVER' environment variable.  Must specify which server to use for sending emails.")
else:
  SMTP_SERVER = os.environ['SMTP_SERVER']

if not "SMTP_PORT" in os.environ:
  raise ValueError("Missing 'SMTP_PORT' environment variable.  Must specify the port to send emails through the SMTP server.")
else:
  SMTP_PORT = os.environ['SMTP_PORT']

if not "FROM_EMAIL_ADDRESS" in os.environ:
  raise ValueError("Missing 'FROM_EMAIL_ADDRESS' environment variable.")
else:
  FROM_EMAIL_ADDRESS = os.environ['FROM_EMAIL_ADDRESS']

if not "FROM_EMAIL_PASSWORD" in os.environ:
  raise ValueError("Missing 'FROM_EMAIL_PASSWORD' environment variable.")
else:
  FROM_EMAIL_PASSWORD = os.environ['FROM_EMAIL_PASSWORD']

if not "TARGET_EMAIL_ADDRESSES" in os.environ:
  raise ValueError("Missing 'TARGET_EMAIL_ADDRESSES' environment variable. Must specify a csv list of email addresses.")
else:
  TARGET_EMAIL_ADDRESSES = os.environ['TARGET_EMAIL_ADDRESSES']