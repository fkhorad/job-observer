PRE: ensure that python3 (sensible version) with pip and nginx are installed

FIRST TIME:
- clone repo
- > sudo mkdir /opt/observer
- > sudo mkdir /opt/observer/data
- > sudo copy -r observer/* /opt/observer
- in /opt/observer:
  > python3 -m venv venv
- create service user:
  > sudo adduser --system --group jobobserver
  > sudo usermod -s /usr/sbin/nologin jobobserver
- own dir:
  > sudo chown -R jobmonitor:jobmonitor /opt/job-monitor
- copy service files job-observer-api.service, job-observer-scheduler.service to /etc/systemd/system/
- enable services:
> ```
> sudo systemctl daemon-reload
> sudo systemctl enable job-monitor-api
> sudo systemctl enable job-monitor-scheduler 
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
- > pip install -r requirements.txt inside opt/observer
- re-own dir
- restart services

NOTE
- view logs with
  > journalctl -u job-monitor-api -f
  
  ... or similar