#/usr/bin/env bash

bert bert.cfg all
pytripatch.py -S -o result.pdf -d resistivity.vector meshParaDomain.bms
bert bert.cfg save

SAVEPATH=`ls -trd result10* | tail -n1`
echo $SAVEPATH
cp result.pdf $SAVEPATH.pdf
okular $SAVEPATH.pdf
