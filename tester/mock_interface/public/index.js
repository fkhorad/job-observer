

// ---- MOCK ENDPOINT URLs ----
const FIRST_POST_ENDPOINT = "/api/first/job";
const FIRST_SECOND_ENDPOINT = "/api/second/job";
const POLLING_REGISTRATION_ENDPOINT = "/api/add_job";
const POLL_ENDPOINT = "/api/job_status";
//
let pollingInterval = null;
const runningJobs = [];
const startBtn1 = document.getElementById("start-btn-1");
// const startBtn2 = document.getElementById("startBtn-2");
const statusContainer = document.getElementById("status-container");
const preStatusDiv = document.getElementById("status-placeholder");


startBtn1.addEventListener("click", startJob);


async function startJob(){

    try {
        // ---- POST REQUEST ----
        const response = await fetch(FIRST_POST_ENDPOINT, {
            method: "POST",
            headers: {
            "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        });

        const data = await response.json();

        const jobId = data.job_id;
        runningJobs.push(jobId);

        const jobElement = document.createElement('div');
        jobElement.id = jobId;
        jobElement.innerText = "Job started with jobID: " + jobId;
        preStatusDiv.after(jobElement);

        if(!pollingInterval) startPolling();

        // Register to polling service
        const requestBody = {
            job_id: jobId,
            service: "mock"
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

        for(const jobId of runningJobs){
            const jobDiv = document.getElementById(jobId);

            try {
                // ---- STATUS REQUEST ----
                const response = await fetch(`${POLL_ENDPOINT}?job_id=${jobId}`);

                // ---- MOCK STATUS RESPONSE ----
                const response_data = await response.json();
                console.log('Check status data', response_data);
                const data_list = response_data['jobs']
                console.log('Check status data', data_list);
                const data = data_list.length ? data_list[0] : {'observed_state': 'unknown'};

                const newInnerText = `Job ${jobId} status: ${data.observed_state}`;
                if(newInnerText!=jobDiv.innerText){
                    jobDiv.innerText = newInnerText;
                }

                if (data.is_terminal) {
                    jobDiv.innerText += " ✅ Done!";
                    const index = runningJobs.indexOf(jobId);
                    if(index !== -1) runningJobs.splice(index, 1);
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
