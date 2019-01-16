# Setup 

## Install Xcode Build Tool

```bash
xcode-select --install
```

## Install Tesseract

In order to get OCR features working you need to install `tesseract`.

**macOS**
```bash
brew install tesseract --with-all-languages
```

**Linux**

Please refer to [official docs](https://github.com/tesseract-ocr/tesseract/wiki#linux).

**Windows**:

Download [installer](https://github.com/UB-Mannheim/tesseract/wiki) and install it.

Notes:
Installation of python wrapper around `tesseract` is handled in `requirements.txt`.

## OpenCV

OpenCV has some known installation issues on Windows when Python 3.7 is used.

Please read those articles:
- [import-cv2-doesnt-give-error-on-command-prompt-but-error-on-idle-on-windows-10ó](https://stackoverflow.com/questions/49516989/import-cv2-doesnt-give-error-on-command-prompt-but-error-on-idle-on-windows-10)
- [opencv-for-python-3-x-under-windows](https://stackoverflow.com/questions/26489867/opencv-for-python-3-x-under-windows)
- [pythonlibs](https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv)

## (macOS Only) Allow apps to control your computer

Find by text on iOS Simulator is based on macOS Accessibility.
In order to get tests working you should allow program that execute tests to be able to control your computer.
```
System Preferences -> Security & Privacy ->  Privacy -> Accessibility -> 
- Add Terminal to list of apps allowed to control your computer (to be able to run tests via Terminal)
- Add PyCharm to list of apps allowed to control your computer (to be able to run tests via IDE)
```
Note that if your Jenkins instance is started via some other executable it should be also added in the list.