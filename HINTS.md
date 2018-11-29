# Hints, Tips & Tricks

## PyCharm IDE

### Make `nose` default test runner

```
Preference -> Tools -> Python integrated Tools - Choose Nosetests as Default test runner
```

## Android Commandline Tools

### Emulator Quick Boot

Start emulator with no snapshot:
```
$ANDROID_HOME/emulator/emulator -avd Emulator-Api23-Default -wipe-data -no-snapshot-load -no-boot-anim
```
When stop emulator it will save its state and next boot with this command will be very fast:
```
$ANDROID_HOME/emulator/emulator -avd Emulator-Api23-Default -no-snapshot-save -no-boot-anim
```

### Faster Screenshots

See [this article](https://stackoverflow.com/questions/13984017/how-to-capture-the-screen-as-fast-as-possible-through-adb)

### Measure UI Performance

See [this article](https://developer.android.com/training/testing/performance) 

See [this blog](https://hackernoon.com/gfxinfo-ui-automator-kotlin-automated-jank-tests-fc43995c7a06)

### Python wrappers around Android tools

- [uiautomator](https://github.com/xiaocong/uiautomator)

## Chrome

Chrome browser need to be in consistent state for debugger tests.
You can achieve it by starting it with custom user profile:
```
"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --user-data-dir=c:\temp-user-data
```

## OCR and Image Recognition

- [tesserocr](https://github.com/sirfz/tesserocr)

- [opencv-ocr-and-text-recognition-with-tesseract](https://www.pyimagesearch.com/2018/09/17/opencv-ocr-and-text-recognition-with-tesseract/)
