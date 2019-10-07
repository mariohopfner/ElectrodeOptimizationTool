createParaMesh -v -d 2 -S -E -z 20 -b 300 -p 5 -l 0.25 -a 0 -q 33.4 -o mesh/mesh feldungel.ohm
grep -w 99$ mesh/mesh.poly > el.node
line1=`head -n2 el.node |tail -n1`
line2=`tail -n2 el.node |head -n1`
eins=${line## *}
zwei=${line# *}
echo $eins $zwei
