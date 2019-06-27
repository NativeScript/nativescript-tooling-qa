/*
In NativeScript, the app.js file is the entry point to your application.
You can use this file to perform app-level initialization, but the primary
purpose of the file is to pass control to the app’s first module.
*/

const application = require("tns-core-modules/application");

global.__onDiscardedError = function(error){
    console.log(error.message);
    console.log(error.stackTrace);
    console.log(error.nativeException);
}

application.run({ moduleName: "app-root" });

/*
Do not place any code after the application has been started as it will not
be executed on iOS.
*/
