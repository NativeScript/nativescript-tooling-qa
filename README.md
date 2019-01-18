# NativeScript Tooling Tests

## About

Project with test for NativeScript tooling.

## Requirements

**Posix:**
- Python 2.7 or Python 3.2+

**Windows**
- Python 3.2+


## Before Running Tests

**Install Required Packages**

Update `pip` and install project requirements:
```
python -m pip install --upgrade pip
```

Install packages on macOS:
```bash
pip install --upgrade -r requirements_darwin.txt --user 
```
Install packages on Windows on Linux:
```bash
pip install --upgrade -r requirements.txt --user
```

Set `PYTHONUNBUFFERED` and `PYTHONIOENCODING` environment variables:
```bash
export PYTHONUNBUFFERED=1
export PYTHONIOENCODING=utf-8
```
Notes: 
- `PYTHONUNBUFFERED` is required to get logging on Jenkins CI working properly.
- `PYTHONIOENCODING` helps to get command execution more stable.

**Setup Machine**
 
Please setup your system as per [Setup](SETUP.md) document. 

**Test Setting via Environment Variables**

Test run is controlled by set of environment variables.

Please read [Settings](SETTINGS.md) document. 

## Run Tests

**{N} CLI Tests**

```bash
python run_ns.py tests/cli
```

**Schematics Tests**

```bash
python run_schematics.py tests/code_sharing
```

## Contribute

Contributions are welcome.

If you wonder how you can contribute, just grab some of the open issues.

Once you are ready with our changes, please run flake8:
```bash
python -m flake8 --max-line-length=120 core core_tests data products tests
```

Notes:
We plan to adopt `pylint`, but we are still in process of defining rules and fixing lint errors.
```bash
python -m pylint core data product --rcfile=c:\Git\nativescript-tooling-qa\.pylintrc
```

## Hints, Tips and Tricks

Please see [Hints, Tips and Tricks](HINTS.md) document.
