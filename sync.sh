#/usr/bin/env bash

echo "Trying to sync..."

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
DATAPATH="data"
FNAME="sync.json"

DATAFILE="$SCRIPTPATH/$DATAPATH/$FNAME"
BAKFILE="$SCRIPTPATH/$DATAPATH/$FNAME.bak"
SECRETS="$SCRIPTPATH/secrets.py"
LOGFILE="$SCRIPTPATH/$DATAPATH/logs"

sync_data(){
    echo "Syncing to $1 using secrets from $2"
    python3 -m pockexport.export --secrets "$2" > $1
}

log_sync(){
    date=$(date '+%Y-%m-%d:%H:%M:%S')
    echo "logging to $1"
    echo $date > $1
}

if test -f "$DATAFILE"; then
    echo "$DATAFILE exists."
    echo "Creating backup to $BAKFILE"
    cp $DATAFILE  $BAKFILE
fi

sync_data $DATAFILE $SECRETS
log_sync $LOGFILE

