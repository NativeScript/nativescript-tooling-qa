const application = require("tns-core-modules/application");

global.__onDiscardedError = function(error){
    console.log("### UNCAUGHT MESSAGE:", error.message);
    console.log("### Stack Trace Start");
    console.log("### UNCAUGHT STACKTRACE:", error.stackTrace);
    console.log("### Stack Trace End");
    console.log("### UNCAUGHT Native Exception:", error.nativeException);
    console.log("### UNCAUGHT STACK:", error.stack);
}

application.run({ moduleName: "app-root" });

