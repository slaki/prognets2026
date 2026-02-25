# 03-L2_Flooding_Flood_All
In the previous exercise we implemented a very basic l2 forwarding switch that
only knows how to forward packets for which it knows the MAC destination
address. In this exercise we will move one step forward towards our more
realistic l2 switch. When an l2 switch does not know to which port to forward a
frame or the MAC destination address is `ff:ff:ff:ff:ff:ff` the switch sends
the packet to all the ports but the one it came from.

In this exercise, first you will have to implement a simplified version in
which packets get forwarded to all ports, once that works, you will have to
implement the real l2 flooding, in which packets do not get sent to the port
they came from.

## Implementing L2 Flooding

We will solve the flooding exercise in two steps. First we will implement the most basic form of flooding packets to all ports.
Then, we will implement a more realistic l2 flooding application that floods packets everywhere, but the
port from where the packet came from. To keep your solutions separated solve each in a different p4 file (skeletons are provided).

### Flooding to all ports

To complete this exercise we will need to define multicast groups, a feature provided
by the `simple_switch` target. Multicast enables us to forward packets to multiple ports. You can find
some documentation on how to set multicast groups in the [simple switch](https://github.com/nsg-ethz/p4-learning/wiki/BMv2-Simple-Switch#creating-multicast-groups) documentation.

Your tasks are:

1. Read the documentation section that talks about multi cast.

2. Define a multicast group with `id=1`.
Create a multicast node that contains all the ports and associate it with the multicast group.

3. Define a `broadcast` action. This action has to set the `standard_metadata.mcast_grp` to the multicast group id
we want to use (in our case 1).

4. Define a match-action table to make switch behave as an l2 packet forwarder. The destination
mac address of each packet should tell the switch witch output port use.

   **Hint**: you can directly copy the table you defined in the previous exercise, and populate it
   with the same mac to port entries.

5. Add the `broadcast` action to the table. This action should be called when there is no hit in the forwarding table
(unknown Mac or `ff:ff:ff:ff:ff:ff`). You can set it as a default action either directly in the table description or
using the `table_set_default` cli command.

6. Apply the table.


## Network Scenario

This is the network scenario topology: 

![topology](images/l2_topology.png)

It is composed by four hosts `hx` and one switch `s1`. 
The switch forwards received packets to all the ports. 

## Testing the scenario
1. To run the network scenario, open a terminal in the scenario directory and type: 
```bash
kathara lstart 
```

2. For testing the P4 program, open a terminal on one host and ping the others: 
```bash
root@h2:/# ping 10.0.0.1 
```

3. If all the hosts can reach the others, the switch is working. 
