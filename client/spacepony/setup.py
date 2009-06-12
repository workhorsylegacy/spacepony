#!/usr/bin/env python

from distutils.core import setup

setup (name = 'spacepony', 
    version = '0.1.0', 
    description = 'Desktop settings syncing client', 
    long_description = 'Space Pony makes it easy to sync your Linux desktop settings to the web and other machines.', 
    author = 'Matthew Brennan Jones', 
    author_email = 'mattjones@workhorsy.org', 
    url = 'http://launchpad.net/spacepony', 
    platforms = 'linux', 

    scripts = ['src/spacepony-client'], 

    license = 'AGPLv3+', 

    packages=['spacepony'],
    package_dir={'spacepony': 'src'},

)

