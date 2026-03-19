### PRE: ensure that python3 (sensible version) with pip and nginx are installed

### FIRST TIME:
1. clone repo
2. make service dirs:
    > sudo mkdir /opt/job-observer

3. copy needed files to service dir
    > sudo copy -r observer /opt/job-observer/
  
    > sudo copy requirements.txt /opt/job-observer/
    
    > sudo copy -r deploy/config /opt/job-observer/
4. Create venv - in /opt/job-observer:
    > python3 -m venv venv
5. create service user (with no login):
    > sudo adduser --system --group jobobserver

    > sudo usermod -s /usr/sbin/nologin jobobserver
    
    - recursively own root service dir:
    
        > sudo chown -R jobobserver:jobobserver /opt/job-observer
6. Enable systemd services
    - copy service files job-observer-api.service, job-observer-scheduler.service to /etc/systemd/system/
    - enable services:
    
        > ```
        > sudo systemctl daemon-reload
        > sudo systemctl enable job-observer-api
        > sudo systemctl enable job-observer-scheduler 
        > ```
    
    - Start services
7. Setup nginx:
   - copy job-observer-reverse-proxy to /etc/nginx/sites-available/
   - enable the reverse proxy
        > ```
        > sudo ln -s /etc/nginx/sites-available/job-monitor /etc/nginx/sites-enabled/
        > sudo nginx -t
        > sudo systemctl restart nginx
        > ```
    - make sure the default nginx site is disabled
8. Remember that the newly deployed component will have a empty service.json, so it won't actually monitor anything! In current version, services.json must be set manually (it's deliberately ignored in the repo).


### THEN (and this could be scriptable)
- pull repo
- stop services
- sudo rsync observer dir, requirements.txt and config dir from repo to /opt/observer; remember the --chown argument (which keeps correct ownership) AND --delete!
- update venv in service dir (with service owner):
    > sudo -u jobobserver /opt/job-observer/venv/bin/pip install -r /opt/job-observer/requirements.txt
- re-start services


### NOTE
- view logs with
  > journalctl -u job-observer-api -f

  ... or similar