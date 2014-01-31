#!/bin/bash

/usr/bin/nohup /usr/bin/sshfs -d -o ssh_command="ssh -i /home/ubuntu/.ssh/id_rsa" -o StrictHostKeyChecking=no ubuntu@"$1":/home/ubuntu/shared_sshfs /home/ubuntu/shared_sshfs