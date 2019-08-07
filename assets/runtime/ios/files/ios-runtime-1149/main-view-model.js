const Observable = require("tns-core-modules/data/observable").Observable;

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

    const url = NSURL.URLWithString("https://www.google.com/");

    const downloadPhotoTask = NSURLSession.sharedSession.downloadTaskWithURLCompletionHandler(url, () => {
        console.log("response1: ", downloadPhotoTask.performSelector("response"));
        console.log("response2: ", downloadPhotoTask.response);
    });
    downloadPhotoTask.resume();

    viewModel.onTap = () => {
        viewModel.counter--;
        viewModel.set("message", getMessage(viewModel.counter));
    };

    return viewModel;
}

exports.createViewModel = createViewModel;
