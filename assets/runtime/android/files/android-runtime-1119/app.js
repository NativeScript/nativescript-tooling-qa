const application = require("tns-core-modules/application");

global.__onDiscardedError = function(error){
    console.log(error.message);
    console.log("### Stack Trace Start");
    console.log(error.stackTrace);
    console.log("### Stack Trace End");
    console.log(error.nativeException);
}

application.run({ moduleName: "app-root" });

