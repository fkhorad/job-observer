

const POLLING_REGISTRATION_ENDPOINT = "/api/add_job";
const POLL_ENDPOINT = "/api/job_status";
//
let pollingInterval = null;
let runningJobs = [];
const statusContainer = document.getElementById("status-container");
const preStatusDiv = document.getElementById("status-placeholder");

// ---- MOCK ENDPOINTS ----
const FIRST_POST_ENDPOINT = "/api/first/job";
const SECOND_POST_ENDPOINT = "/api/second/job";
const endpoints = {
    'mock': FIRST_POST_ENDPOINT,
    'mock_clone': SECOND_POST_ENDPOINT
};
//
const startBtn1 = document.getElementById("start-btn-1");
const startBtn2 = document.getElementById("start-btn-2");


startBtn1.addEventListener("click", startJob);
startBtn2.addEventListener("click", startJob);


async function startJob(event){

    const serviceName = event.target.getAttribute('data-val');
    console.log('Event called service:', serviceName);

    try {
        // ---- POST REQUEST ----
        const response = await fetch(endpoints[serviceName], {
            method: "POST",
            headers: {
            "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        });

        const data = await response.json();

        const jobId = data.job_id;
        runningJobs.push([jobId, serviceName]);

        const jobElement = document.createElement('div');
        jobElement.id = jobId;
        jobElement.innerText = `Job started in service ${serviceName} with jobID: ${jobId}`;
        preStatusDiv.after(jobElement);

        if(!pollingInterval) startPolling();

        // Register to polling service
        const requestBody = {
            job_id: jobId,
            service: serviceName
        };
        //
        await fetch(POLLING_REGISTRATION_ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

    } catch (error) {
        preStatusDiv.innerText = "Error starting job";
        console.error(error);
    }
}

function startPolling() {

    preStatusDiv.innerText = 'Checking job(s)';

    pollingInterval = setInterval(async () => {

        for(const job of runningJobs){
            const jobId = job[0];
            const serviceName = job[1]
            const jobDiv = document.getElementById(jobId);

            try {
                // ---- STATUS REQUEST ----
                const response = await fetch(`${POLL_ENDPOINT}?job_id=${jobId}&service=${serviceName}`);

                // ---- MOCK STATUS RESPONSE ----
                const response_data = await response.json();
                console.log('Check status data', response_data);
                const data_list = response_data['jobs']
                console.log('Check status data', data_list);
                const data = data_list.length ? data_list[0] : {'observed_state': 'unknown'};

                const newInnerText = `Job ${jobId} (${serviceName}) status: ${data.observed_state}`;
                if(newInnerText!=jobDiv.innerText){
                    jobDiv.innerText = newInnerText;
                }

                if (data.is_terminal) {
                    jobDiv.innerText += " ✅ Done!";
                    runningJobs = runningJobs.filter(el => (el[0]!==jobId || el[1]!==serviceName));
                }

            } catch (error) {
                const newInnerText = `Error checking ${jobId} status`;
                if(newInnerText!=jobDiv.innerText){
                    jobDiv.innerText = newInnerText;
                }
                console.error(error);
            }
        }

        if(!runningJobs.length){
            clearInterval(pollingInterval);
            pollingInterval = null;
            preStatusDiv.innerText = 'Idle';
        }

    }, 4000); // every x milliseconds
}
