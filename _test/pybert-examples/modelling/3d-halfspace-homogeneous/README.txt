The simplest case of all: One four-electrode-measurement on a homogeneous half-space with 1 S/m conductivity.

We provide 2 ways to achieve this goal.

    The shell script way: calc.sh

        Hint. If your are not common to shell script please consult a newbie guide.
        In german: http://wiki.ubuntuusers.de/Shell/Bash-Skripting-Guide_für_Anfänger

    The python script way: calc.py

For booth approaches we need a modeling mesh that will be created by: mkmesh.sh which is also extensively commented.

The shell script example contains a lot of repeating dcmod calls, maybe it is better read it step by step and execute the commands manually by copy and paste.

Please note, most of the commands used in the shell script have a command switch -h .. this is your friend.

Files:
    calc.sh -- main calculation script

    mkmesh.sh -- Script that will generate the geometry and the mesh

    dipdip.shm -- configuration for Dipole-Dipole measurement
