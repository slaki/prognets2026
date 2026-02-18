# Kathara download
First install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) and then download [Kathará](https://www.kathara.org/).

# Commands

To run the network scenario, open a terminal in the exercise folder that contains the 'lab.conf' file and type:
```bash
kathara lstart 
```

If you do not want to open terminal windows for all hosts and switches, type the following:
```bash
kathara lstart --noterminal
```

To open a terminal window to host h1, type:
```bash
kathara connect h1
```

To get the network interfaces of node r1 and the nodes the interfaces are connected, type:
```bash
kathara linfo -n r1
```

```bash
Network Usage (DL/UL): 0 B / 0 BInterfaces: 0:r1r5, 1:r1r2, 2:r1r3, 3:r1r4
```
In this example, interface 0 of r1 is connected to r5, interface 1 of r1 is connected to r2, etc.

To close the networking scenario, stop containers and free the resources, type:
```bash
kathara lclean
```


# P4 cheat sheet
- [A cheat sheet for P4-16 is available.](https://lakis.web.elte.hu/prognets201920II/Labs/p4-cheat-sheet.pdf) 
- [Documentation of Runtime CLI](https://github.com/p4lang/behavioral-model/blob/adff022fc8679f5436d07e7af73c3300431df785/docs/runtime_CLI.md)

# Week 1
Source: https://gitlab.ethz.ch/nsg/public/adv-net-2022-exercises/-/tree/main

- [Reflector](./01-reflector)
- [Repeater](./02-repeater)
- [Layer 2 Switch - Simple](./03-l2-basic-forwarding)

