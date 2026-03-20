

// Schema: service 1; [extractor1, injector1]; service 2; [extractor2, injector2]; ... service N
// input is input of service 1, output is output of service N. Use 2-steps for the mediators because... It's clear & general. Forget JSONpath for now. Can use falsy values for mediators for identity.
// Callback is standard for pipelines here: every pipeline "breakpoint" (everytime a service is 'marked' as async) calls the polling registration with a standard endpoint.