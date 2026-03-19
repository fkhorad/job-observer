### PRE: ensure that python3 with pip ('recent enough' version) + nginx are installed


### FIRST SETUP:
1. clone repo
2. create service dir -- assumed to be /opt/job-observer (if changing, need to update service files + code snippets in this file accordingly):
    > sudo mkdir /opt/job-observer

3. copy needed files to service dir
    > sudo copy -r observer /opt/job-observer/
  
    > sudo copy requirements.txt /opt/job-observer/
    
    > sudo copy -r deploy/config /opt/job-observer/
4. Create venv in service dir
5. create service user 'jobobserver' (special user with no pwd and no login):
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
7. Setup nginx:
   - copy job-observer-reverse-proxy to /etc/nginx/sites-available/
   - enable the reverse proxy
        > ```
        > sudo ln -s /etc/nginx/sites-available/job-monitor /etc/nginx/sites-enabled/
        > sudo nginx -t
        > sudo systemctl restart nginx
        > ```
    - make sure the default nginx site is disabled
    - Be mindful of port settings and possible shadowing if other sites are enabled!
8. Remember that the newly deployed component will have a EMPTY services.json pseduodb, so it won't actually monitor anything! In current version, services.json must be set manually (it's deliberately ignored in the repo).


### DEPLOY -- works both first time and at updates (note: can create mini-script for this)
- pull repo
- stop services (optional)
- sudo rsync observer dir, requirements.txt and config dir from repo to /opt/observer; remember the include a --chown argument (keeps correct ownership) AND to --delete!
- set/update venv in service dir (using service owner of course):
    > sudo -u jobobserver /opt/job-observer/venv/bin/pip install -r /opt/job-observer/requirements.txt
- re-start services


### ON LOGS
- view logs with
  > journalctl -u job-observer-api -f

  ... or similar