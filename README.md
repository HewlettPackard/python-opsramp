<!---
(c) Copyright 2019 Hewlett Packard Enterprise Development LP

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
# python-opsramp
A Python language binding for the OpsRamp API

## About
This directory tree contains a Python module that provides a convenient way to
access the OpsRamp REST API programmatically. The OpsRamp API documentation is
somewhat opaque and this binding hides some of the details for exactly that reason.
I have also added "assert" statements in various places to guard against pitfalls
that I ran into that are not obvious from the API docs.

### Scope
At this time (June 2019) the scope of this binding is very narrow, mostly around the RBA automation
functionality of OpsRamp, but the basic framework is here and the scope will increase incrementally
over time.

Note however that all of our wrapper objects provide an `api()` callable that
returns an object that can be used to access REST URLs further down the API tree
where we have not written a specific wrapper class here yet.

While you can use these api objects to work directly with OpsRamp at a REST level,
please consider taking the small amount of time needed to add a proper wrapper class
here instead, for your own benefit and that of future users.

### Return values
All functions in this binding return regular Python objects (not JSON strings).
In general you will need to look at the OpsRamp API docs to see exactly what
sort of object and/fields the response will contain; typically we return exactly
what the API gave us, or an equivalent Python object if it returned JSON.

### Runtime Environment
This module is primarily designed for use on Python 3.

We also run the unit tests against Python 2.7 and it *should* work correctly there
too. Note however that Python 2 is going end-of-life in late 2019 and we reserve
the right to drop support for it in a future version of this module.

## Examples
The file examples.py gives a series of examples of how to use this binding and
illustrates most of the major areas of the API that we cover.

`python3 -m opsramp.examples`

It depends on the existence of some environment variables to tell it which OpsRamp
endpoint to use and the relevant creds. You can see those at the top of examples.py
and you must set them appropriately in your environment before running it.

```
export OPSRAMP_URL='https://my-org.api.try.opsramp.com'
export OPSRAMP_TENANT_ID='client_1234'
export OPSRAMP_KEY='whatever'
export OPSRAMP_SECRET='whatever'
```

The client id, key and secret are obtained from an "integration" in the OpsRamp UI.
You need to go to "setup", "integrations" and look for (or create) a row containing
a custom integration that uses OAUTH2. It doesn't matter what it's called, you just
need its id and creds to call the REST API.

On the list of integrations, click on the integration name in the appropriate row
and a screen appears with the "Tenant Id", "Key" and "Secret" fields that you need.
The UI even gives sample curl commands at the bottom and you can cut the URL value
out of those if it's not obvious. It's just the bit as far as opsramp.com like the
example above.

It's not obvious, but the creds you're getting here are for the entire *Tenant*
(aka client) and will be the same for all integrations on that Tenant. Be careful
with them, don't put them in logs or post them online by accident.

If there isn't a suitable integration already (or you want your own) then create a new
one by selecting the "other" tab in the Available Integrations section at the bottom
of the page and then "custom". Give it a name and leave the image file field blank.
The name will appear in access logs but otherwise has no real meaning. Select OAUTH2
as the authentication type and hit Save. This will bring you to the screen with keys
and curl commands etc as described above.

### Simple CLI prototype
I wrote a simple Python program that uses this binding to perform some simple
read-only operations on OpsRamp. Uses the same environment variables as above.
```
$ python3 -m opsramp.cli tenant rba categories | jq -S .
[
  {
    "id": 346,
    "name": "Day to day actions"
  },
  {
    "id": 698,
    "name": "DR procedures"
  }
]
$ python3 -m opsramp.cli tenant monitoring templates
538 monitoring templates found
$ python3 -m opsramp.cli tenant agent script | wc -l
763
$
```

## Public Object Tree

Following is a summary of the object tree currently available in this OpsRamp language binding. See `examples.py`
for an illustration of how to use them. You start by creating a single OpsRamp object to represent the entire REST API
instance that you want to access, and make a series of calls that return progressively lower level objects to access
lower level information from OpsRamp. For clarity in these end-user instructions I have omitted several Python
classes that are internal implementation detail in the module and not intended for direct use by external callers.

- def connect(url, key, secret) _returns an instance of the class Opsramp that is connected to the specified API endpoint_
  This function posts a login request to the specified endpoint URL using the key and secret given. This post
  returns an access token, which the function uses to construct an Opsramp object and returns that.

- class Opsramp(url, token) _an object representing the complete API tree of one OpsRamp instance_
  - get\_alert\_types() -> returns a list of the global alert types that are defined on this OpsRamp instance.
  - tenant(uuid) -> returns a Tenant object representing the API subtree for one specific tenant.

- class Tenant(uuid) _the API subtree for one specific tenant_
  - get\_alert\_script() -> Returns a string containing the appropriate Python script to run on a Linux node
  to install the OpsRamp agent there and connect it to this Tenant. This text contains the tenant's access keys
  so think twice before printing it to the screen or logs.
  - get\_alerts(pattern) -> Returns a list of alert instances on this Tenant that match the specified pattern.
  See the OpsRamp API docs for details on the format of the pattern string.
  - monitoring() -> returns a Monitoring object representing all monitoring information for this Tenant.
  - rba() -> returns an Rba object representing all runbook automation information for this Tenant.

- class Monitoring() _the monitoring information subtree for one specific Tenant_
  - templates() -> returns a Templates object representing the set of monitoring templates on this Tenant.

- class Templates() _the set of monitoring templates for one Tenant_
  - search(pattern) -> returns a list of templates that match the pattern. See the OpsRamp API docs for details
  on the format of the pattern string.
- class Rba() _the runbook automation subtree of one specific Tenant_
  - get\_categories() -> Return a list of all the script categories in this subtree.
  - category(uuid) -> returns a Category object representing one specific script category on this Tenant.
  - create\_category(name, optional parent\_uuid) -> creates a new script category on this Tenant and
  returns its uuid. Optionally takes the uuid of a pre-existing category under which to nest the new one.

- class Category() _the subtree for one RBA category_
  - get\_scripts() -> returns a list of the scripts in this category.
  - script(uuid) -> returns a Script object representing the API subtree for one specific script.
  - create\_script(definition) -> creates a new script in this category. "definition" is a Python dict
  specifying details of the script to be created. Helper functions for creating these dicts are provided
  in the Script class and documented there.

- class Script() _a single RBA script_
  - get() -> returns the definition of this script as a Python dict. See the OpsRamp API docs for detailed contents.
  - @staticmethod mkparameter(name, description, datatype, optional, default) -> helper function that returns a
  Python dict describing one parameter of a proposed new script.
  - @staticmethod mkscript(name, description, platforms, execution\_type, payload, parameters=[], script\_name=None, install\_timeout=0, registry\_path=None, registry\_value=None, process\_name=None, service\_name=None, output\_directory=None, output\_file=None) -> helper function that returns
  a Python dict describing a proposed new script. Some of the parameters are only applicable on Linux,
  some only on Windows, and the function contains `assert` statements to flag violations of those rules.

## The API objects and direct REST calls

If we don't have a class that exposes the piece of the API that you want to use, then you can use the `ApiObject` base
class to make REST calls to that part directly while still using the correct wrapper classes for everything else.
The general idea would be to navigate to the nearest object for which we do have a wrapper and call its `api()` method
to get an instance of the `ApiObject` class that you can then use to make direct REST calls to the tree below that point.

For example:
```
capi = ormp.tenant('client_9234').monitoring().api()
result = capi.get('/templates')
print(result)
```
This uses a REST get() to retrieve the list of templates directly from OpsRamp, by starting from the api object
of a Monitoring object. The Monitoring object will have already done all the work to set up the correct tenant,
credentials and other context for that call so it's still much easier than making httplib, requests or curlxi
calls yourself.

- ApiObject() _an object representing some subtree of a REST API_
  - get(suffix='', headers={}) -> performs a GET to the specified REST endpoint and returns the body of the
  server's reply. "headers" is an optional dict containing any additional HTTP headers that you want to send
  with the GET.
  - post(suffix='', headers={}, data=None, json=None) -> performs a POST to the specified REST endpoint and
  returns the body of the server's reply. "headers" is an optional dict containing any additional HTTP headers
  that you want to send, "data" is the text body, or "json" is a Python struct to be converted to a JSON
  string and sent as a body. Specifying both "data" and "json" in the same call results in undefined behavior
  and should be avoided.
  - _we will add other http actions if/when a specific need for them arises_
