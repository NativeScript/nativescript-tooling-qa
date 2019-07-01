const Observable = require("tns-core-modules/data/observable").Observable;

function getMessage() {
    console.log("### TEST START ###");
    console.log("wrapped: " + interop.Pointer(new Number(-1)));
    console.log("wrapped: " + interop.Pointer(new Number(-2)));
    console.log("wrapped: " + interop.Pointer(new Number(Math.pow(2,35))));
    console.log("### TEST END ###");
}

function createViewModel() {
    const viewModel = new Observable();
    viewModel.message = getMessage();

    viewModel.onTap = function() {

    }

    return viewModel;
}

exports.createViewModel = createViewModel;