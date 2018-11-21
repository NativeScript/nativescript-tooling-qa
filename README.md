# NativeScript Tooling Tests

## About

Project with test for NativeScript tooling.

## Install Requirements

Install Python 2.*:
```
brew install python
```

Update `pip` and install project requirements:
```
python -m pip install --upgrade pip
pip install -r requirements.txt --user
```

## Setup Environment

Please see [Setup](SETUP.md) document. 
   
## Run Tests

```
nosetests -v -s --nologcapture --with-xunit --xunit-file out/nosetests.xml --with-html --html-report-template=core/report/template.html --html-file=out/nosetests.html --all-modules tests/cli/build/
```

## Contribute

Run flake8:
```bash
flake8 --max-line-length=120 core core_tests data products tests
```
## Hints, Tips and Tricks

Please see [Hints, Tips and Tricks](HINTS.md) document.
