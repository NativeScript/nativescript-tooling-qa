const Observable = require("tns-core-modules/data/observable").Observable;

function getMessage() {
    console.log("### TEST START ###");
    console.log(new interop.Pointer(-1));
    console.log(new interop.Pointer(-2));
    console.log(new interop.Pointer(34359738368));
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