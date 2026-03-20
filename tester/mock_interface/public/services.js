// ---- SERVICES ENDPOINTS (including mocks) ----

const FIRST_POST_ENDPOINT = "/api/first/job";
const SECOND_POST_ENDPOINT = "/api/second/job";

export const services = {
    'mock': {'endpoint': FIRST_POST_ENDPOINT},
    'mock_clone': {'endpoint': SECOND_POST_ENDPOINT, 'callback_url': 'http://localhost:3001/callback'}
};