import os

from livedepartureboards import DepartureBoard

darwin_token = os.environ.get('DARWIN_TOKEN', None)

if not darwin_token:
    raise Exception("DARWIN_TOKEN environmental variable must be set")

d = DepartureBoard(token=darwin_token)
print d.tabulate_all("TRO")
