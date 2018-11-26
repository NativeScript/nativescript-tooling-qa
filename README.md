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

## Before Running Tests

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
flake8 --max-line-length=120 core core_tests data products tests
```

## Hints, Tips and Tricks

Please see [Hints, Tips and Tricks](HINTS.md) document.
