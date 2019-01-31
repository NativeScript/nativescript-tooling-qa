# Console Log Samples

## tns run android 
```
/Users/topuzov/Git/nativescript-tooling-qa/node_modules/.bin/tns run android --path TestApp --emulator
====>
[Verify node_modules not watched] Skipping node_modules folder! Use the syncAllFiles option to sync files from this folder.
[Initial prepare] Preparing project...
[Initial prepare] Successfully prepared plugin nativescript-theme-core for android.
[Initial prepare] Successfully prepared plugin tns-core-modules for android.
[Initial prepare] Successfully prepared plugin tns-core-modules-widgets for android.
[Initial prepare] Project successfully prepared (Android)
[Initial build] Building project...
[Initial build] Gradle build...
[Initial build] 	 + setting applicationId
[Initial build] 	 + applying user-defined configuration from /Users/topuzov/Git/nativescript-tooling-qa/TestApp/app/App_Resources/Android/app.gradle
[Initial build] 	 + using support library version 28.0.0
[Initial build] 	 + adding nativescript runtime package dependency: nativescript-optimized-with-inspector
[Initial build] 	 + adding aar plugin dependency: /Users/topuzov/Git/nativescript-tooling-qa/TestApp/node_modules/tns-core-modules-widgets/platforms/android/widgets-release.aar
[Initial build] Project successfully built.
[Initial run] Installing on device emulator-5562...
[Initial run] Successfully installed on device with identifier 'emulator-5562'.
[Initial run] Restarting application on device emulator-5562...
[Initial run] Successfully synced application org.nativescript.TestApp on device emulator-5562.
[Initial run] ActivityManager: Start proc 2746:org.nativescript.TestApp/u0a55 for activity org.nativescript.TestApp/com.tns.NativeScriptActivity
========== Sync JS Change ========================================================================================================
[Prepare with change] Preparing project...
[Prepare with change] Project successfully prepared (Android)
[Sync JS file] Successfully transferred main-view-model.js on device emulator-5562.
[Sync JS file should cause restart] Restarting application on device emulator-5562...
[Sync JS file] Successfully synced application org.nativescript.TestApp on device emulator-5562.
[Sync JS file should cause restart] ActivityManager: Start proc 2888:org.nativescript.TestApp/u0a55 for activity org.nativescript.TestApp/com.tns.NativeScriptActivity
========== Sync XML Change ========================================================================================================
[Prepare with change] Preparing project...
[Prepare with change] Project successfully prepared (Android)
[Sync XML file] Successfully transferred main-page.xml on device emulator-5562.
[Sync XML file] Refreshing application on device emulator-5562...
[Sync XML file] Successfully synced application org.nativescript.TestApp on device emulator-5562.
[Sync XML should NOT cause restart] ActivityManager: Start proc 2888:org.nativescript.TestApp/u0a55 is MISSING!

```

## tns run ios
```
/Users/topuzov/Git/nativescript-tooling-qa/node_modules/.bin/tns run ios --path TestApp --emulator
====>
[Verify node_modules not watched] Skipping node_modules folder! Use the syncAllFiles option to sync files from this folder.
[Initial prepare] Preparing project...
[Initial prepare] Successfully prepared plugin nativescript-theme-core for ios.
[Initial prepare] Successfully prepared plugin tns-core-modules for ios.
[Initial prepare] Successfully prepared plugin tns-core-modules-widgets for ios.
[Initial prepare] Project successfully prepared (iOS)
[Initial build] Building project...
[Initial build] Xcode build...
[Initial build] Project successfully built.
[Initial run] Installing on device 91440777-B175-4E3D-86B5-70830628ECE4...
[Initial run] Successfully installed on device with identifier '91440777-B175-4E3D-86B5-70830628ECE4'.
[Initial run] Successfully transferred all files on device 91440777-B175-4E3D-86B5-70830628ECE4.
[Initial run] Restarting application on device 91440777-B175-4E3D-86B5-70830628ECE4...
[Initial run] Successfully synced application org.nativescript.TestApp on device 91440777-B175-4E3D-86B5-70830628ECE4.
========== Sync JS Change ========================================================================================================
[Prepare with change] Preparing project...
[Prepare with change] Project successfully prepared (iOS)
[Sync JS file] Successfully transferred main-view-model.js on device 91440777-B175-4E3D-86B5-70830628ECE4.
[Sync JS file should cause restart] Restarting application on device 91440777-B175-4E3D-86B5-70830628ECE4...
[Sync JS file] Successfully synced application org.nativescript.TestApp on device 91440777-B175-4E3D-86B5-70830628ECE4.
========== Sync XML Change ========================================================================================================
[Prepare with change] Preparing project...
[Prepare with change] Project successfully prepared (iOS)
[Sync XML file] Successfully transferred main-page.xml on device 91440777-B175-4E3D-86B5-70830628ECE4.
[Sync XML should NOT cause restart] NativeScript debugger has opened inspector socket on port 18183 for org.nativescript.TestApp.
[Sync XML file] Refreshing application on device 91440777-B175-4E3D-86B5-70830628ECE4...
[Sync XML file] Successfully synced application org.nativescript.TestApp on device 91440777-B175-4E3D-86B5-70830628ECE4.
CONSOLE LOG file:///app/tns_modules/tns-core-modules/inspector_modules.js:1:82: Loading inspector modules...
CONSOLE LOG file:///app/tns_modules/tns-core-modules/inspector_modules.js:6:12: Finished loading inspector modules.
NativeScript debugger attached.
[Sync XML should NOT cause restart] Restarting application is MISSING!
```

## tns run android --bundle

```
/Users/topuzov/Git/nativescript-tooling-qa/node_modules/.bin/tns run android --path TestApp --emulator --bundle
====>
Skipping node_modules folder! Use the syncAllFiles option to sync files from this folder.
Searching for devices...
Running webpack for Android...
clean-webpack-plugin: /Users/topuzov/Git/nativescript-tooling-qa/TestApp/platforms/android/app/src/main/assets/app/**/* has been removed.
File change detected. Starting incremental webpack compilation...
...
webpack is watching the files…
...
Webpack compilation complete. Watching for file changes.
Webpack build done!
Preparing project...
Project successfully prepared (Android)
Building project...
Gradle build...
...
Project successfully built.
Installing on device emulator-5562...
Successfully installed on device with identifier 'emulator-5562'.
Restarting application on device emulator-5562...
Successfully synced application org.nativescript.TestApp on device emulator-5562.
ActivityManager: Start proc 3905:org.nativescript.TestApp/u0a57 for activity org.nativescript.TestApp/com.tns.NativeScriptActivity
========== Sync JS Change ========================================================================================================
File change detected. Starting incremental webpack compilation...
[./main-view-model.js] 627 bytes {bundle} [built]
Webpack compilation complete. Watching for file changes.
Webpack build done!
Preparing project...
Project successfully prepared (Android)
Successfully transferred bundle.js on device emulator-5562.
Restarting application on device emulator-5562...
Successfully synced application org.nativescript.TestApp on device emulator-5562.
ActivityManager: Start proc 4046:org.nativescript.TestApp/u0a57 for activity org.nativescript.TestApp/com.tns.NativeScriptActivity
========== Sync XML Change ========================================================================================================
File change detected. Starting incremental webpack compilation...
[./main-page.xml] 1.87 KiB {bundle} [optional] [built]
Webpack compilation complete. Watching for file changes.
Webpack build done!
Preparing project...
Project successfully prepared (Android)
Successfully transferred bundle.js on device emulator-5562.
Restarting application on device emulator-5562...
Successfully synced application org.nativescript.TestApp on device emulator-5562.
ActivityManager: Start proc 4164:org.nativescript.TestApp/u0a57 for activity org.nativescript.TestApp/com.tns.NativeScriptActivity
```

## tns run android --hmr

```
/Users/topuzov/Git/nativescript-tooling-qa/node_modules/.bin/tns run android --path TestApp --emulator --hmr
====>
Skipping node_modules folder! Use the syncAllFiles option to sync files from this folder.
Searching for devices...
Hot Module Replacement (HMR) is currently in Beta. For more information about the current development state and any known issues, please check the relevant GitHub issue: https://github.com/NativeScript/NativeScript/issues/6398
Running webpack for Android...
Webpack compilation complete. Watching for file changes.
Webpack build done!
Preparing project...
Project successfully prepared (Android)
Building project...
Gradle build...
Project successfully built.
Installing on device emulator-5562...
Successfully installed on device with identifier 'emulator-5562'.
Restarting application on device emulator-5562...
Successfully synced application org.nativescript.TestApp on device emulator-5562.
ActivityManager: Start proc 5475:org.nativescript.TestApp/u0a60 for activity org.nativescript.TestApp/com.tns.NativeScriptActivity
JS: HMR: Hot Module Replacement Enabled. Waiting for signal.
========== Sync JS Change ========================================================================================================
File change detected. Starting incremental webpack compilation...
[./main-view-model.js] 627 bytes {bundle} [built]
Webpack compilation complete. Watching for file changes.
Webpack build done!
Successfully transferred bundle.646fc8f847dc610ce4e7.hot-update.js on device emulator-5562.
Successfully transferred 646fc8f847dc610ce4e7.hot-update.json on device emulator-5562.
JS: HMR: Checking for updates to the bundle with hmr hash 646fc8f847dc610ce4e7.
JS: HMR: The following modules were updated:
JS: HMR:          ↻ ./main-view-model.js
JS: HMR:          ↻ ./main-page.js
JS: HMR: Successfully applied update with hmr hash 646fc8f847dc610ce4e7. App is up to date.
Refreshing application on device emulator-5562...
Successfully synced application org.nativescript.TestApp on device emulator-5562.
========== Sync XML Change ========================================================================================================
File change detected. Starting incremental webpack compilation...
[./main-page.xml] 1.87 KiB {bundle} [optional] [built]
Webpack compilation complete. Watching for file changes.
Webpack build done!
Successfully transferred bundle.ec1b9f154401eb5d2a50.hot-update.js on device emulator-5562.
Successfully transferred ec1b9f154401eb5d2a50.hot-update.json on device emulator-5562.
JS: HMR: Checking for updates to the bundle with hmr hash ec1b9f154401eb5d2a50.
JS: HMR: The following modules were updated:
JS: HMR:          ↻ ./main-page.xml
JS: HMR: Successfully applied update with hmr hash ec1b9f154401eb5d2a50. App is up to date.
Refreshing application on device emulator-5562...
Successfully synced application org.nativescript.TestApp on device emulator-5562.
[Sync XML should NOT cause restart] ActivityManager: Start proc 2888:org.nativescript.TestApp/u0a55 is MISSING!
[Sync XML should NOT cause restart] Restarting application is MISSING!
```