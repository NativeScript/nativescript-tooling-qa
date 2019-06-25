var application = require("application");

global.__onDiscardedError = function(error){
    console.log(error.message);
    console.log("### Stack Trace Start");
    console.log(error.stackTrace);
    console.log("### Stack Trace End");
    console.log(error.nativeException);
}

application.start({ moduleName: "main-page" });

