const Observable = require("tns-core-modules/data/observable").Observable;
const platformModule = require("tns-core-modules/platform");
const app = require("tns-core-modules/application");

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

    viewModel.onTap = () => {
        viewModel.counter--;
        viewModel.set("message", getMessage(viewModel.counter));
                if (platformModule.device.sdkVersion >= "26") {
            let intent = new android.content.Intent(app.android.context, com.nativescript.location.BackgroundService.class);
            app.android.context.startForegroundService(intent);
        } else {
            let intent = new android.content.Intent(app.android.context, com.nativescript.location.BackgroundService.class);
            app.android.context.startService(intent);
            
        }
    };

    return viewModel;
}

exports.createViewModel = createViewModel;
