/*
In NativeScript, the app.js file is the entry point to your application.
You can use this file to perform app-level initialization, but the primary
purpose of the file is to pass control to the app’s first module.
*/
const app = require("tns-core-modules/application");
const application = require("tns-core-modules/application");
const platformModule = require("tns-core-modules/platform");
if (platformModule.device.sdkVersion >= "26") {
    global.channelId = "22";
}
(android.app.Service).extend("com.nativescript.location.BackgroundService", {
    onStartCommand: function (intent, flags, startId) {
        this.super.onStartCommand(intent, flags, startId);
        return android.app.Service.START_STICKY;
    },
    onCreate: function () {
        console.log("Create Foreground Service!");

        let b;
        if(global.channelId){
            b = new androidx.core.app.NotificationCompat.Builder(app.android.context, global.channelId)
            .setOngoing(true)
            .setContentTitle("test")
            .setContentText("test")
            .setSmallIcon(android.R.drawable.stat_sys_warning);
            }
            else{
            b = new androidx.core.app.NotificationCompat.Builder(app.android.context)
            .setOngoing(true)
            .setContentTitle("test")
            .setContentText("test")
            .setSmallIcon(android.R.drawable.stat_sys_warning);
            }
            this.startForeground(2, b.build());
    },
    onBind: function (intent) {
    },
    onUnbind: function (intent) {
    },
    onDestroy: function () {
    }
});
application.run({ moduleName: "app-root" });

/*
Do not place any code after the application has been started as it will not
be executed on iOS.
*/
