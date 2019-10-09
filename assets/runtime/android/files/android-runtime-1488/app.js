/*
In NativeScript, the app.js file is the entry point to your application.
You can use this file to perform app-level initialization, but the primary
purpose of the file is to pass control to the app’s first module.
*/

const application = require("tns-core-modules/application");

var MyWorker = androidx.work.Worker.extend("com.tns.jobs.MyWorker",{
     doWork:function(){
        	   // Do your work here.
        
        	   //
        	   return androidx.work.ListenableWorker.Result.success();
        	},
        
        	onStopped:function() {
        	  // Cleanup because you are being stopped.
        	  console.log("onStopped from MyWorker !!!")
        	}
});
application.run({ moduleName: "app-root" });

/*
Do not place any code after the application has been started as it will not
be executed on iOS.
*/
