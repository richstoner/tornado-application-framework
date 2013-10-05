from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import exists

from datetime import datetime
import sys, pprint, time, ConfigParser, os
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('settings.ini')

client_id = parser.get('digitalocean', 'client_id')
api_key = parser.get('digitalocean', 'api_key')

def dostat():

    import digitalocean

    manager = digitalocean.Manager(client_id=client_id, api_key=api_key)
    my_droplets = manager.get_all_droplets()
    for droplet in my_droplets:
        print '%s, %s, %s' % (droplet.name, droplet.ip_address, droplet.image_id)

def dolaunch():

    import digitalocean

    droplet = digitalocean.Droplet(client_id=client_id, api_key=api_key, name='autodrop', region_id=3, image_id=284203,
                                   size_id=66, backup_active=False)
    
    # this configures a 512MB droplet in NYC running 12.04 LTS
    # ... I had to install a ruby gem (tugboat) first to get the list of image ids... 

    print droplet
    droplet.create()
    
    while event.percentage != 100:
        ### Refreshing the event status
        #### Checking the status of the droplet
        event = droplet.get_events()[0]
        event.load()
        #Once it shows 100, droplet is up and running
        print event
        print event.percentage
    
    print droplet.ip_address







def vagrant():
    # change from the default user to 'vagrant'
    env.user = 'vagrant'
    # connect to the port-forwarded ssh
    env.hosts = ['127.0.0.1:2222']
 
    # use vagrant ssh key
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]
     



def sysinfo():
    run('uname -a')
    run('lsb_release -a')


def base():
    '''[create] Basic packages for building, version control'''
    with settings(warn_only=True):
        run("sudo apt-get -y update", pty = True)
        run("sudo apt-get -y upgrade", pty = True)      

        packagelist = ' '.join(['git-core', 'mercurial', 'subversion', 'unzip', 'build-essential', 'g++', 'libav-tools', 'uuid-dev', 'libfreetype6-dev','libpng12-dev', 'redis-server', 'nginx'])       
        run('sudo apt-get -y install %s' % packagelist, pty = True)

        packagelist = ' '.join(['python-setuptools', 'python-pip', 'python-dev', 'python-lxml', 'libxml2-dev', 'python-imaging', 'libncurses5-dev', 'cmake-curses-gui', 'imagemagick'])
        run('sudo apt-get -y install %s' % packagelist, pty = True)
        
        packagelist = ['tornado', 'supervisor', 'virtualenv' ]
        for each_package in packagelist: 
            print each_package
            run('sudo pip install %s' % each_package, pty = True)


def externals():
    '''[create] some external dependencies (be patient, compiles numpy etc)'''
    with settings(warn_only=True):

        run('git clone https://github.com/ipython/ipython.git')

        with cd('ipython'):
            run('python setup.py build')
            sudo('python setup.py install')

        sudo('apt-get build-dep -y python-numpy python-scipy')

        sudo('pip install cython')
        sudo('pip install -U numpy')
        sudo('pip install -U scipy')
        sudo('pip install git+git://github.com/scikit-image/scikit-image.git')

        sudo('pip install requests')
        sudo('pip install rq-dashboard') # also installs rq and redis thankfully


def startnginx():
    '''[start] set nginx config and start'''

    with settings(warn_only=True):

        sudo('rm -vf /etc/nginx/nginx.conf')
        sudo('ln -s /vagrant/config/nginx.conf /etc/nginx/nginx.conf')
        sudo('service nginx restart')

        print 'if all went well, nginx should be running and serving things through port 80 on the vm which redirects to port 8080 on the host.'


def startsupervisor():
    '''[start] sets up supervisor and starts it'''

    with settings(warn_only=True):

        sudo('rm /etc/supervisord.conf')
        sudo('rm /etc/init.d/supervisor')
        sudo('ln -s /vagrant/config/supervisord.conf /etc/supervisord.conf')
    
        sudo('supervisord')
        sudo('chmod +x supervisor.start')
        sudo('chown root:root supervisor.start')
        sudo('cp -v /vagrant/config/supervisor.start /etc/init.d/supervisor')
        sudo('update-rc.d -f supervisor remove')
        sudo('update-rc.d supervisor defaults')
        sudo('supervisorctl restart all')


def startall():
    '''[start] starts or restarts anything that needs to be running'''

    with settings(warn_only=True):
        sudo('service nginx restart')
        sudo('service redis-server restart')
        sudo('supervisorctl restart all')
        sudo('mkdir -p /vagrant/app/static/uploads')































