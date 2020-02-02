const Observable = require("tns-core-modules/data/observable").Observable;
const testPlugin = require("mylib");
const applicationModule = require("tns-core-modules/application");
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
        console.log(testPlugin.listClass());
        console.log(testPlugin.arrayListClass());
        console.log(testPlugin.dateClass());
        try{
        console.log(testPlugin.timerClass());
        }
        catch(err) {
            console.log(err.message);
        }
        sleep(2000);
        try{
        console.log(new android.appwidget.AppWidgetHost(applicationModule.context,3));
        }
        catch(err) {
            console.log(err.message);
        }
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
