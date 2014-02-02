#!/bin/bash

function find_newer
{
    local check="$1"; shift
    find "$@" -newer "$CHECK" |
    grep -v '.py[cod]'
}

CHECKDIR=${CHECKDIR:-/tmp/}
CHECK=$CHECKDIR/rerun-check.$$
trap "rm -f '$CHECK'; exit $?" SIGINT SIGTERM EXIT
rm -f "$CHECK"
while true;
do
    echo "[KKCHEKING..."
    echo -n "[A"

    # If the rerun file changed, re-exec ourselves.
    if [ -f "$CHECK" -a -s "$(find_newer "$CHECK" "$@")" ];
    then
        exec $0 "$@"
    fi

    # Otherwise, look for other updates.
    changed=$(find . -name '.?*' -prune \
                     -o \( -type f -newer "$CHECK" -print \) )
    if [ ! -f "$CHECK" -o "$changed" ];
    then
        eval "clear; clear; $@; echo -n '--- RUN AT: '; date"
        if [ -f "$CHECK" ]
        then
            echo 
            echo Reran due to changes in:
            for filename in $changed
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

