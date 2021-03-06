# Setup for production
Getting things setup for production take a little bit of effort but here are all the steps that are required for a Linux host.

## Get the code
Copy to home directory as rendezvous

    git clone https://github.com/corytodd/rendezvous.git

We can't do anything else until we get the server and service handlers setup so let us proceed.

## Database prep
We don't keep the db in the code repo so securely copy the database to the server

    scp -i .ssh\<my_key> rendezvous.sqlite3 <name>@<host>:/home/<name>/rendezvous

If you'd like, you can install sqlite3 from your package manager and poke around in the database. There is nothing sensitive in there
so have fun.

## Server prep
This assumes you have a function server stack using nginx. Create file named after your host, e.g. tiger.corytodd.us.conf in /etc/nginx/sites-available

    server {
        listen 80;
        server_name     example.com;
        location / {
                try_files       $uri    @app;
        }

        location @app {
                include         uwsgi_params;
                uwsgi_pass      unix:/home/user/rendezvous/rendezvous.sock;
        }

        location ~ /\. {
                deny all;
        }
    }
    server {
        listen 443;
        server_name     example.com;
        location / {
                try_files       $uri    @app;
        }

        location @app {
                include         uwsgi_params;
                uwsgi_pass      unix:/home/user/rendezvous/rendezvous.sock;
        }

        location ~ /\. {
                deny all;
        }
    }

Then test for typos

    sudo nginx -t

If no problems, restart the server

    sudo service nginx restart


## Setup Python 3.6 (and other stuff we'll need)
We need Python 3.6 so add the ppa that has this pre-build for us

    sudo add-apt-repository ppa:jonathonf/python-3.6
    sudo apt-get update
    
We need a bunch of stuff for the uwsgi plugin so let's just do it all at once

    sudo apt-get install build-essential python3.6 python3.6-dev uwsgi uwsgi-src uuid-dev libcap-dev libpcre3-dev libssl-dev
    python36 -m venv ~/rendezvous/venv
    source ~/rendezvous/venv
    pip install -r requirements.txt
    python -m textblob.download_corpora

    cd ~
    PYTHON=python3.6 uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python36"
    sudo mv python36_plugin.so /usr/lib/uwsgi/plugins/python36_plugin.so
    sudo chmod 644 /usr/lib/uwsgi/plugins/python36_plugin.so

We should now have python36, the python36 uwsgi plugin, and a shiny venv. If so, we're ready to serve.


## Serving
This is the easy part!

    uwsgi config.ini

The server should now be running. 



