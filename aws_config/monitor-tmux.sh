#!/bin/bash

# Monitor status of matching crawlers on remote aws machines

INPUT=$1
SESSION="monitor_matching"
BASEPATH="/home/ana/code/tmtext/aws_config"

# kill session if already exists
tmux kill-session -t $SESSION

# create new session
tmux new -d -s $SESSION
tmux split-window -v

# split both panes horizontally => 4 panes
for i in 0 2
do 
	tmux select-pane -t $i
	tmux split-window -h
done

## Note: starting all comands with a space, to avoid recording them in history

# first pane: monitor results
tmux select-pane -t 0
tmux send-keys -t $SESSION " cd $BASEPATH; watch -n 30 ./count_results.sh $INPUT" C-m

# second pane: monitor matches
tmux select-pane -t 1
tmux send-keys -t $SESSION " cd $BASEPATH; watch -n 30 ./count_matches.sh $INPUT" C-m

# third pane: monitor errors
tmux select-pane -t 2
tmux send-keys -t $SESSION " cd $BASEPATH; watch -n 60 ./count_errors.sh $INPUT" C-m


# fourth pane: monitor exceptions
tmux select-pane -t 3
tmux send-keys -t $SESSION " cd $BASEPATH; watch -n 60 ./count_exceptions.sh $INPUT" C-m

# monitor 503 errors
tmux split-window -h
tmux select-pane -t 4
tmux send-keys -t $SESSION " cd $BASEPATH; watch -n 60 ./count_503s.sh $INPUT" C-m

tmux a -t $SESSION