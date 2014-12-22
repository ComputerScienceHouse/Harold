HAROLD
======

Computer Science House - Rochester Institute of Technology

A Python rewrite of the CSH house system HAROLD (Heralding Arrivals Rather Obnoxiously Loud Device), which is currently being run on a Raspberry Pi B+. HAROLD receives the iButton input from the user and then plays either a set song or random song from a playlist defined by the user for thirty seconds over the speakers in the elevator lobby. HAROLD's purpose is to provide entertainment while either waiting for an elevator or a member's arrival on-floor. 

To run Harold run the file using the following command.
```
$ python Harold/main.py
```

Alternatively, (as configured on the actual machine) you can add Harold to init.d and instead run:
```
$ service harold (start|stop)
```


Make sure the user running the script has permissions to read from /dev/ or run the script as root.
