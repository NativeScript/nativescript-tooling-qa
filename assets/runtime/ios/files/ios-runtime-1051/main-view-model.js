const Observable = require("tns-core-modules/data/observable").Observable;

function getMessage(counter) {
    console.log("### TEST START ###");
    var fileManager = NSFileManager.defaultManager;
    fileManager.contentsOfDirectoryAtPathError('/not-existing-path');
    console.log("### TEST SHOULD NOT CRASH ###");
    console.log("### TEST END ###");
}

function createViewModel() {
    const viewModel = new Observable();
    viewModel.counter = 42;
    viewModel.message = getMessage(viewModel.counter);

    viewModel.onTap = () => {
        viewModel.counter--;
        viewModel.set("message", getMessage(viewModel.counter));
    };

    return viewModel;
}

exports.createViewModel = createViewModel;
