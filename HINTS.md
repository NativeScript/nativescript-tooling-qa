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

## Chrome

Chrome browser need to be in consistent state for debugger tests.
You can achieve it by starting it with custom user profile:
```
"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --user-data-dir=c:\temp-user-data
```
