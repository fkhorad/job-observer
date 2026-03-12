# Job Observer

A lightweight infrastructure component for observing and tracking asynchronous jobs in distributed systems.

Job Observer monitors long-running or remote jobs by polling service endpoints, maintaining a durable job state, and exposing structured job status information.


## Author

**Francesco Coradeschi**
ORCID: [https://orcid.org/0000-0003-0808-2736](https://orcid.org/0000-0003-0808-2736)


## License

This project is released under the **MIT License**.
See the `LICENSE` file for details.


## Context

This software was originally developed by **Francesco Coradeschi** while working at
***Opera Vocabolario***, part of the National Research Council of Italy (CNR), as a member of the [H2IOSC](https://www.h2iosc.cnr.it/) project.

This repository contains the **generic implementation of the monitoring component** and does not include project- or institute-specific infrastructure, configuration, or data.


## The component

### The problem this solves

Distributed systems frequently execute long-running asynchronous jobs:

* background computations
* batch pipelines
* remote service tasks
* workflow stages

Monitoring these jobs often leads to:

* ad-hoc polling logic scattered across services
* inconsistent job state tracking
* fragile monitoring scripts
* difficulty understanding job failures


### How it solves it

Job Observer centralizes job monitoring into a **small infrastructure component**.

Instead of each service implementing its own monitoring logic, the observer:

1. polls job status endpoints
2. maintains a consistent job state
3. emits structured status information

This keeps job monitoring **decoupled from the services executing the jobs**.


### Architecture overview

* **Observer API** – register observation requests, exposes job status information
* **Scheduler** – maintains durable job state, queries job status endpoints, executes callback to users if requested


### Assumptions

The observer assumes monitored services expose a **status endpoint** that:

* returns job state when queried with a job ID
* responds quickly (typically in less than 2–3 seconds)
* returns (lightly) structured status information

These assumptions keep the monitoring architecture simple and robust.


### Features

* centralized monitoring of asynchronous jobs
* decoupled polling mechanism
* durable job state tracking
* simple integration with existing services
* minimal infrastructure footprint


### Design Principles

Job Observer follows a few simple design principles:

* **Prefer small infrastructure components**
* **Separate job execution from job observation**
* **Use explicit state tracking**
* **Keep operational assumptions simple**


## Status

Prototype / early production component used in infrastructure experiments for job orchestration.


## Citation

If you use this software in research or infrastructure projects, please cite it as:

```
Coradeschi, Francesco (2025). Job Observer.
Software developed for the H2IOSC project.
https://github.com/fkhorad/job-observer
```


## Contributing

This repository currently reflects the original implementation of the system.

Issues and suggestions are welcome via GitHub.

