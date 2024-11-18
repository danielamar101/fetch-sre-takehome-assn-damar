
# Fetch Take-Home Excersize SRE (Daniel Amar)

This is a short and basic program to check the health of a set of HTTP endpoints(provided in yaml format and specified as an input parameter) and logs the cumulative availabilty percentage for each domain. This is repeatedly done until a keyboard interrupt is given manually by the user.


# Installation

1. Create a virtual environment:
```
python -m venv ./sre-fetch-assignment-env
```
2. Activate virtual env
```
source ./sre-fetch-assignment-env/bin/activate
```
3. Install dependencies:
```
pip install -r requirements.txt
```

# Syntax:
```
python fetch.py input_data/sample.yml
```
If you are unsure of the given syntax at any given time:
```
python fetch.py --help
usage: fetch.py [-h] config

HTTP Endpoint Health Monitor

positional arguments:
  config      Path to the YAML configuration file

options:
  -h, --help  show this help message and exit
```

# Input Yaml File specifications

** Note: This program assumes the contents of the yaml input file are in a valid yaml format. No validation is done within the program. ** 

Each HTTP endpoint element in the YAML list has the following schema:
- name (string, required) — A free-text name to describe the HTTP endpoint.
- url (string, required) — The URL of the HTTP endpoint.
You may assume that the URL is always a valid HTTP or HTTPS address.
- method (string, optional) — The HTTP method of the endpoint.
    - If this field is present, you may assume it’s a valid HTTP method (e.g. GET, POST, etc.).
    - If this field is omitted, the default is GET.
- headers (dictionary, optional) — The HTTP headers to include in the request.
    - If this field is present, you may assume that the keys and values of this dictionary are strings that are valid HTTP header names and values.
    -   If this field is omitted, no headers need to be added to or modified in the HTTP request.
- body (string, optional) — The HTTP body to include in the request.
    - If this field is present, you should assume it's a valid JSON-encoded string. You
    do not need to account for non-JSON request bodies.
     -If this field is omitted, no body is sent in the request.

## Sentry Instrumentation (Optional)

1. Install [direnv](https://direnv.net/docs/installation.html) for managing environment variables on a per-project basis
2. Rename .envrc.sample to .envrc
3. Add a valid sentry dsn:

```
export SENTRY_DSN="some sentry dsn value here"
``
4. Get this environment variable into the current environment with direnv:
```
direnv allow
```
4. Uncomment this block of code from fetch.py:
```
# import sentry_sdk
# import os
# sentry_sdk.init(
#     dsn=os.environ.get("SENTRY_DSN"),
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for tracing.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )
```

After this, if there is ever an error or exception in fetch.py, or if the availability of a domain is <20%, a span will be generated and sent to sentry, where it can reviewed and investigated. 