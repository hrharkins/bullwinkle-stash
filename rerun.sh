#!/bin/bash

function find_updates
{
    local check="$1"; shift
    if [ -f "$check" ];
    then
        find .  -type f -newer "$check" | 
            egrep -v '\.py[co]$' | 
            grep -v '/\.' | 
            grep -v '^\.[^/]'
    fi 
}

CHECKDIR=${CHECKDIR:-/tmp/}
CHECK=$CHECKDIR/rerun-check.$$
EXEC=$CHECKDIR/rerun-exec.$$
trap "rm -f '$CHECK' '$EXEC'; exit $?" SIGINT SIGTERM EXIT
rm -f "$CHECK"
touch "$EXEC"
while true;
do
    echo "[KKCHEKING..."
    echo -n "[A"

    # If the rerun file changed, re-exec ourselves.
    if [ "$0" -nt "$EXEC" ];
    then
        exec $0 "$@"
    fi

    # Otherwise, look for other updates.  Ignore changes to . or dot files
    # and folders.
    changed=$(find_updates "$CHECK")
    if [ ! -f "$CHECK" -o ! -z "$changed" ];
    then
        eval "clear; clear; $@; echo -n '--- RUN AT: '; date"
        if [ -f "$CHECK" ]
        then
            echo 
            echo Reran due to changes in:
            echo $changed |
            while read filename
            do
                if [ "$filename" ]
                then
                    ls -ltrd "$filename"
                fi
            done
            echo
            echo "While last check was:"
            ls -l "$CHECK"
        fi
        touch "$CHECK"
    else
        echo -n "NO CHANGES FOUND: "; date
        echo -n "[A"
    fi
    sleep 2
done

