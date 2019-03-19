const createViewModel = require("./main-view-model").createViewModel;

function onNavigatingTo(args) {
    const page = args.object;
    console.log("### TEST START ###");
    console.log("### TEST END ###");
    page.bindingContext = createViewModel();
}
exports.onNavigatingTo = onNavigatingTo;
