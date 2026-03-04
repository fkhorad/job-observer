
const POLLING_REGISTRATION_ENDPOINT = "/api/add_job";
const POLL_ENDPOINT = "/api/job_status";
//
let pollingInterval = null;
let pollingJobs = [];
const preStatusDiv = document.getElementById("status-placeholder");
const pollingColumn = document.getElementById('polling-column');
const callbackColumn = document.getElementById('callback-column');

const pipelineTerminators = [];

// ---- MOCK ENDPOINTS ----
const FIRST_POST_ENDPOINT = "/api/first/job";
const SECOND_POST_ENDPOINT = "/api/second/job";
const services = {
    'mock': {'endpoint': FIRST_POST_ENDPOINT},
    'mock_clone': {'endpoint': SECOND_POST_ENDPOINT, 'callback_url': 'http://localhost:3001/callback'}
};
//
const startBtn1 = document.getElementById("start-btn-1");
const startBtn2 = document.getElementById("start-btn-2");

startBtn1.addEventListener("click", startJob);
startBtn2.addEventListener("click", startJob);


const eventSource = new EventSource("/events"); // Establishes an SSE with the node.js server
eventSource.addEventListener("callback", displayCallback);


function displayCallback(event){
    const data = JSON.parse(event.data);

    console.log("Callback received:", data);

    const jobId = data.job_id;
    const service = data.service;
    const key = [jobId, service].toString();
    if(pipelineTerminators[key]){
        const pipeline = pipelineTerminators[key];
        // Do something here
    }
    else if(service=='mock_clone'){
        const jobDiv = document.getElementById(jobId);
        if(!jobDiv){
        }
        else{
            jobDiv.innerText = `Callback for job ${jobId} received!`
            jobDiv.style.color = "green";
        }
    }
    else{
        preStatusDiv.innerText = `Received callback for unknown job, ID: ${jobId}`
    }
}


async function startJob(event){

    const serviceName = event.target.getAttribute('data-val');
    console.log('Event called service:', serviceName);

    try {
        // ---- POST REQUEST ----
        const response = await fetch(services[serviceName]['endpoint'], {
            method: "POST",
            headers: {
            "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        });
        if (!response.ok) {
            const message = await response.text();
            throw new Error(`HTTP error in calling service: ${response.status} - ${message}`);
        }
        const data = await response.json();

        const jobId = data.job_id;

        // Register with observer service
        const requestBody = {
            job_id: jobId,
            service: serviceName
        };
        const callback_url = services[serviceName]['callback_url'];
        if(callback_url) requestBody['callback_url'] = callback_url;
        //
        const poller_response = await fetch(POLLING_REGISTRATION_ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        });
        if (!poller_response.ok) {
            const message = await poller_response.text();
            throw new Error(`HTTP error in calling observer: ${poller_response.status} - ${message}`);
        }

        preStatusDiv.innerText = 'Checking job(s)';

        // Add div
        const jobElement = document.createElement('div');
        jobElement.id = jobId;
        //
        if(callback_url){
            jobElement.innerText = `Awaiting callback for service ${serviceName}, jobId: ${jobId}`;
            callbackColumn.prepend(jobElement);
        }
        else{
            jobElement.innerText = `Job polling - service: ${serviceName}, jobId: ${jobId}`;
            pollingColumn.prepend(jobElement);
            pollingJobs.push([jobId, serviceName]);
            if(!pollingInterval) startPolling();
        }

    } catch(error) {
        preStatusDiv.innerText = `Problem starting job - ${error}`;
        console.error(error);
    }
}

function startPolling() {

    pollingInterval = setInterval(async () => {

        for(const job of pollingJobs){
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
                    deleteJob(jobId, serviceName);
                }

            } catch (error) {
                const newInnerText = `Error checking ${jobId} status`;
                if(newInnerText!=jobDiv.innerText){
                    jobDiv.innerText = newInnerText;
                }
                console.error(error);
            }
        }

    }, 4000); // every x milliseconds
}


function deleteJob(jobId, serviceName){
    pollingJobs = pollingJobs.filter(el => (el[0]!==jobId || el[1]!==serviceName));
    if(!pollingJobs.length){
        if(pollingInterval){
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
        preStatusDiv.innerText = 'Idle';
    }
}