# 01-Reflector
The packet reflector will be our very first P4 exercise. The main objective
of this exercise is to show you how to create simple topologies with hosts and
p4 switches and how to add links between them. Then you will implement
a very simple p4 program that makes switches bouncing back packets to the interface
the packets came from.

## Implementing the Packet Reflector

To solve this exercise, you only need to fill the gaps in the
`reflector.p4` skeleton. The places where you are supposed to write your own code
are marked with a `TODO`.

In the end, your program should do the following:

1. Parse the `ethernet` header and make a transition to `MyIngress`.
Note that the definition of the `ethernet` header and the `headers` struct is already defined for you.

2. Swap the packet's ethernet addresses. You can use an action or simply write the code directly
   in the control `apply`.
   >Hint: you can define and use local variables to swap the addresses: `bit<48> tmpAddr`;

3. Use the *ingress_port* as *egress_port*. The value of the `ingress_port` will be stored in the packet
metadata, in the variable `standard_metadata.ingress_port`. To set a packet's output port, you need to set
`standard_metadata.egress_spec` metadata field. For more information about the standard metadata fields read: [simple switch documentation](https://github.com/nsg-ethz/p4-learning/wiki/BMv2-Simple-Switch#standard-metadata).

4. Deparse the `ethernet` header.

> Note: The use of tables is possible but not strictly necessary for completing this exercise.

## Network Scenario
It is composed by two devices: one host `h1` and one switch `s1`. 
This is a very simple example in which `s1` bounces back packets received on an interface. 

## Testing the scenario
To run the network scenario, open a terminal in the scenario directory and type: 
```bash
kathara lstart 
```

For testing the P4 program, open a terminal on `h1` and type: 
```bash
python3 send_receive.py 
```

You will see an output like this: 

```bash
root@h1:/# python3 send_receive.py 
Press the return key to send a packet:
Sending on interface eth0 to 10.0.0.2

[!] A packet was reflected from the switch: 
[!] Info: 00:01:02:03:04:05 -> 4a:ca:38:cf:c4:32

```
