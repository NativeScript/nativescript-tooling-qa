/*
In NativeScript, the app.js file is the entry point to your application.
You can use this file to perform app-level initialization, but the primary
purpose of the file is to pass control to the app’s first module.
*/
const app = require("tns-core-modules/application");
const application = require("tns-core-modules/application");
androidx.core.app.JobIntentService.extend("com.nativescript.MyIntentServiceAndroidX", {

    onHandleWork: function () {
        console.log("Intent Handled!");
   }
});
application.run({ moduleName: "app-root" });

/*
Do not place any code after the application has been started as it will not
be executed on iOS.
*/
