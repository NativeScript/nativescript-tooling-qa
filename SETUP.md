# Setup 

## Install Tesseract

In order to get OCR features working you need to install `tesseract`.

**macOS**
```bash
brew install tesseract --all-languages
```

**Linux**

Please refer to [official docs](https://github.com/tesseract-ocr/tesseract/wiki#linux).

**Windows**:

Download [installer](https://github.com/UB-Mannheim/tesseract/wiki) and install it.

Notes:
Installation of python wrapper around `tesseract` is handled in `requirements.txt`.


## (macOS Only) Allow apps to control your computer

Find by text on iOS Simulator is based on macOS Accessibility.
In order to get tests working you should allow program that execute tests to be able to control your computer.
```
System Preferences -> Security & Privacy ->  Privacy -> Accessibility -> 
- Add Terminal to list of apps allowed to control your computer (to be able to run tests via Terminal)
- Add PyCharm to list of apps allowed to control your computer (to be able to run tests via IDE)
```
Note that if your Jenkins instance is started via some other executable it should be also added in the list.

