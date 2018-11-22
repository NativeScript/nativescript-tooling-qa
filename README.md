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

### {N} CLI Tests

```bash
python run_ns.py tests/cli
```
### Schematics Tests

```bash
python run_schematics.py tests/code_sharing
```

## Contribute

Run flake8:
```bash
flake8 --max-line-length=120 core core_tests data products tests
```
## Hints, Tips and Tricks

Please see [Hints, Tips and Tricks](HINTS.md) document.
