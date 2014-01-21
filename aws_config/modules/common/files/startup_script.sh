#!/bin/bash

/etc/init.d/networking restart

cd tmtext; git pull origin master; cd

