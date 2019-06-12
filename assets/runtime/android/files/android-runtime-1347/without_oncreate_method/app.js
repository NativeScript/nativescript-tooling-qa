/*
In NativeScript, the app.js file is the entry point to your application.
You can use this file to perform app-level initialization, but the primary
purpose of the file is to pass control to the app’s first module.
*/
const app = require("tns-core-modules/application");
const application = require("tns-core-modules/application");
(android.app.Service).extend("com.nativescript.location.BackgroundService", {
    onStartCommand: function (intent, flags, startId) {
        this.super.onStartCommand(intent, flags, startId);
                console.log("Create Foreground Service!");
    const b = new androidx.core.app.NotificationCompat.Builder(app.android.context)
      .setOngoing(true)
      .setContentTitle("test")
      .setContentText("test")
      .setSmallIcon(android.R.drawable.stat_sys_warning);

                        this.startForeground(2, b.build());
        return android.app.Service.START_NOT_STICKY;
    }
});
application.run({ moduleName: "app-root" });

/*
Do not place any code after the application has been started as it will not
be executed on iOS.
*/
