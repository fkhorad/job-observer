PRE: ensure that python3 (sensible version) with pip and nginx are installed

FIRST TIME:
- clone repo
- make service dirs:
  > sudo mkdir /opt/job-observer
  > sudo mkdir /opt/job-observer/data
- copy files
  > sudo copy -r observer /opt/job-observer/
  > sudo copy requirements.txt /opt/job-observer/
  > sudo copy -r deploy/config /opt/job-observer/
- in /opt/job-observer:
  > python3 -m venv venv
- create service user:
  > sudo adduser --system --group jobobserver
- recursively own root service dir:
  > sudo chown -R jobobserver:jobobserver /opt/job-observer
- copy service files job-observer-api.service, job-observer-scheduler.service to /etc/systemd/system/
- enable services:
> ```
> sudo systemctl daemon-reload
> sudo systemctl enable job-observer-api
> sudo systemctl enable job-observer-scheduler 
> ```
- copy job-observer-reverse-proxy to /etc/nginx/sites-available/
- enable the reverse proxy
> ```
> sudo ln -s /etc/nginx/sites-available/job-monitor /etc/nginx/sites-enabled/
> sudo nginx -t
> sudo systemctl restart nginx
> ```

THEN
- update repo
- rsync observer dir from repo to /opt/observer
- re-own dir
- work as user:
  > sudo -u jobobserver -i
- > pip install -r requirements.txt
  
  inside opt/observer
- back to standard user, restart services

NOTE
- view logs with
  > journalctl -u job-observer-api -f

  ... or similar