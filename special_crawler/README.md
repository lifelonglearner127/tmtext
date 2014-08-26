This directory contains a python module for a REST service that extracts and provides info on walmart.com products media - video, PDFs and product reviews.

The service is implemented in python 2.7.

## Dependencies (python packages):

- Flask
- lxml
- requests (only needed for tests)

The list of dependencies can be found in the `requirements.txt` file.

To install the dependencies (using pip), run:

    pip install -r requirements.txt

The service can be run with

    sudo ./crawler_service.py


## Documentation

More details in the [wiki page](https://bitbucket.org/dfeinleib/tmtext/wiki/Special%20crawler).
