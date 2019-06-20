# python-opsramp
A Python language binding for the OpsRamp API

OpsRamp is mostly UI-focused but it does provide a REST API that allows external callers to perform
a lot of the same operations programmatically. This package is a minimalist Python binding for that
REST API that makes it easier to consume in Python code because it provides a set of classes that
call the API on your behalf and handle all the conversions to and from JSON and other formats that
the various parts of the API require, and allow you to work with regular Python objects only.

At this time (June 2019) the scope of this binding is very narrow, mostly around the RBA automation
functionality of OpsRamp, but the basic framework is here and the scope will increase incrementally
over time.

Even as it stands however, this binding provides an ApiObject class that can be used to call any
part of the REST API, including parts that are not explicitly covered by wrapper classes here yet.
