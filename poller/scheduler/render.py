def render(v, job_id: str):
    if isinstance(v, str):
        return v.replace("{job_id}", job_id)
    if isinstance(v, dict):
        return {k: render(val, job_id) for k, val in v.items()}
    if isinstance(v, list):
        return [render(x, job_id) for x in v]
    return v
