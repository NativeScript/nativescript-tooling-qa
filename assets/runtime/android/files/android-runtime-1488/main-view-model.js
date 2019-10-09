const Observable = require("tns-core-modules/data/observable").Observable;

function getMessage(counter) {
    if (counter <= 0) {
        return "Hoorraaay! You unlocked the NativeScript clicker achievement!";
    } else {
        return `${counter} taps left`;
    }
}


function getJobConstrains() {
        return (new androidx.work.Constraints.Builder())
                    .build();
    }

    function getWorkRequest() {
        let constrains = getJobConstrains();
		return (new androidx.work.OneTimeWorkRequest.Builder(java.lang.Class.forName("com.tns.jobs.MyWorker")))
            .setConstraints(constrains)        
            .build()
    }

    function enqueue() {
        let worker = getWorkRequest();
        
		(androidx.work.WorkManager).getInstance()
          .enqueueUniqueWork("jojoworker", androidx.work.ExistingWorkPolicy.REPLACE , worker); 
             
        let lifecycleowner = androidx.lifecycle.ProcessLifecycleOwner.get();
        
        (androidx.work.WorkManager).getInstance().getWorkInfoByIdLiveData(worker.getId())
            .observe(lifecycleowner, new androidx.lifecycle.Observer({
                onChanged : function(workInfo) {

                    console.log("OnChange 1 : ", workInfo)

				}
			}))
    }
function createViewModel() {
    const viewModel = new Observable();
    viewModel.counter = 42;
    viewModel.message = getMessage(viewModel.counter);

    viewModel.onTap = () => {
        viewModel.counter--;
        viewModel.set("message", getMessage(viewModel.counter));
        enqueue();
    };

    return viewModel;
}

exports.createViewModel = createViewModel;
