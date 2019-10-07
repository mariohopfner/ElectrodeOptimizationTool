#!/usr/bin/env bash

calc() {
    path=$1
    cfg=$2
    oldpath=$PWD
    cd $path
        echo -e "test: " $path: $cfg "-- \c" | tee -a $oldpath/testAll.log
        bert $cfg all > _test.log 2> _test.errlog

        if [ -f bert.log ]; then
            echo `cat bert.log | grep ": chi^2" | tail -n 1` | tee -a $oldpath/testAll.log
            bert $cfg save
            bert $cfg mrproper
        else
            echo "preparation failed!" | tee -a $oldpath/testAll.log
        fi
    cd $oldpath
}

echo "############ start: " `date` "git:" `git log --pretty=format:"%h - %an, %ar" | head -n1` | tee -a testAll.log

calc 2dflat/gallery gallery.cfg
calc 2dflat/gallery galleryGrid.cfg
calc 2dstruct bedrock.cfg
calc 2dtopo/slagdump slagdump.cfg
calc 2dxh 2dxh.cfg # fail

calc bhsch bert.cfg
calc circle/human human.cfg
calc circle/tree hollow_limetree.cfg
calc 3dflat/gallery gallery.cfg
calc 3dflat/gallery galleryGrid.cfg
calc 3dtopo/burialMound burialMound.cfg
calc 3dtopo/acucar acucar.cfg # not really working nice now
calc 3dtopo/slagdump slagdump.cfg
calc 3dxh 3dxh.cfg

echo "############ end" `date` | tee -a testAll.log
