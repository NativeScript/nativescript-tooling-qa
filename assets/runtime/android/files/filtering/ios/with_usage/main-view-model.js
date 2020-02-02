const Observable = require("tns-core-modules/data/observable").Observable;
const testPlugin = require("mylib");
function getMessage(counter) {
    if (counter <= 0) {
        return "Hoorraaay! You unlocked the NativeScript clicker achievement!";
    } else {
        return `${counter} taps left`;
    }
}

function createViewModel() {
    const viewModel = new Observable();
    viewModel.counter = 42;
    viewModel.message = getMessage(viewModel.counter);
sleep(2000);
        console.log(testPlugin.CFNumberCreate());
        console.log(testPlugin.CFArrayCreate());
        console.log(testPlugin.CFCalendarCopyCurrent());
        sleep(2000);
        try{
            console.log(testPlugin.CFUUIDCreate());
            }
        catch(err) {
            console.log(err.message);
        }
        console.log("CFTimeZoneCreateWithName created! Value: "+CFTimeZoneCreateWithName(null,'null',true));
    viewModel.onTap = () => {
        viewModel.counter--;
        viewModel.set("message", getMessage(viewModel.counter));
    };

    return viewModel;
}
function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}
exports.createViewModel = createViewModel;
