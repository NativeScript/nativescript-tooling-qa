var Observable = require("data/observable").Observable;

function getMessage(counter) {
    if (counter <= 0) {
        return "Hoorraaay! You unlocked the NativeScript clicker achievement!";
    } else {
        return counter + " taps left";
    }
}

function createViewModel() {
    var viewModel = new Observable();
    viewModel.counter = 42;
    viewModel.message = getMessage(viewModel.counter);

    viewModel.onTap = function() {
        console.log("### TEST START ###");
         try {
           throw new Error("New Error!");
      } catch (error) {
                        console.log("### CAUGHT MESSAGE:", error.message);
                        console.log("### Stack Trace Start");
                        console.log("### CAUGHT STACKTRACE:", error.stackTrace);
                        console.log("### Stack Trace End");
                        console.log("### CAUGHT Native Exception:", error.nativeException);
                        console.log("### CAUGHT STACK:", error.stack);;
      }
       throw new Error("New Error!");
        sleep(2000);
        console.log("### TEST SHOULD NOT CRASH ###");
        console.log("### TEST END ###");
    }

    return viewModel;
}

exports.createViewModel = createViewModel;

function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}