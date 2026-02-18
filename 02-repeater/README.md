# 02-Repeater
In the second introductory exercise we will use our first table and conditional
statements in a control block. In this exercise you will make a two-port
switch act as a packet repeater, in other words, when a packet enters `port 1`
it has to be leave from `port 2` and vice versa.

<p align="center">
<img src="images/topology.png" title="Repeater Topology">
<p/>

## Network Scenario
It is composed by three devices: two host `h1` and `h2`, and one switch `s1`. 
This is a very simple example in which `s1` act as a repeater. 
In other words, when a packet enters `port 1` it has to be leave from `port 2` and vice versa.

## Implementing the Packet Repeater

To solve this exercise you only need to fill the gaps you will find in the
`repeater.p4` skeleton. The places where you are supposed to write your own code
are marked with a `TODO`. You will have to solve this exercise using two
different approaches (for the sake of learning). First, and since the switch
only has 2 ports you will have to solve the exercise by just using conditional statements
and fixed logic. For the second solution, you will have to use a match-action table and
populate it using the CLI.

### Using Conditional Statements

1. Using conditional statements, write (in the `MyIngress` Control Block) the logic
needed to make the switch act as a repeater. (only `TODO 3`)

### Using a Table

> If for the second solution you want to use a different program name and
> and topology file you can just define a new `p4` file and a different `.json`
> topology configuration, then you can run `sudo p4run --config <json file name>`.

1. Define a table of size 2, that matches packet's ingress_port and uses that
to figure out which output port needs to be used (following the definition of repeater).

2. Define the action that will be called from the table. This action needs to set the output port. The
type of `ingress_port` is `bit<9>`. For more info about the `standard_metadata` fields see:
the [`v1model.p4`](https://github.com/p4lang/p4c/blob/master/p4include/v1model.p4) interface.

3. Call (by using `apply`), the table you defined above.

4. Populate the table (using the Thrift client command file `s1-commands.txt`). For more information
about table population check the following [documentation](https://github.com/nsg-ethz/p4-learning/wiki/Control-Plane), [documentation 2](https://nsg-ethz.github.io/p4-utils/usage.html#control-plane-configuration), [advanced docs](https://nsg-ethz.github.io/p4-utils/advanced_usage.html#control-plane-configuration).

## Testing the scenario
1. To run the network scenario, open a terminal in the scenario directory and type: 
```bash
kathara lstart 
```

2. For testing the P4 program, open a terminal on `h2` and run receive.py: 
```bash
python3 receive.py
```

3. Then, open a terminal on `h1` and run receive.py: 
```bash
python3 send.py 10.0.0.2 "Hello H2"
```

You will see an output like this on `h2`: 

```bash 
Packet Received:
###[ Ethernet ]### 
  dst       = 06:07:08:09:0a:0b
  src       = 00:01:02:03:04:05
  type      = IPv4
###[ IP ]### 
     version   = 4
     ihl       = 5
     tos       = 0x0
     len       = 28
     id        = 1
     flags     = 
     frag      = 0
     ttl       = 64
     proto     = hopopt
     chksum    = 0x66df
     src       = 10.0.0.1
     dst       = 10.0.0.2
     \options   \
###[ Raw ]### 
        load      = 'Hello H2'
```
