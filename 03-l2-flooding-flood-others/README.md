# 03-L2_Flooding_Flood_Others
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

## Network Scenario

This is the network scenario topology: 

![topology](images/l2_topology.png)

It is composed by four hosts `hx` and one switch `s1`. 
The switch act as a repeater. 

## Implementing L2 Flooding

We will solve the flooding exercise in two steps. First we will implement the most basic form of flooding packets to all ports.
Then, we will implement a more realistic l2 flooding application that floods packets everywhere, but the
port from where the packet came from. To keep your solutions separated solve each in a different p4 file (skeletons are provided).

### Flooding to other ports

Now that we know how to define multicast groups, and we saw that it does work its time to implement a more realistic flooding.
For this exercise the switch will need to take into account the packet's input port and only broadcast to the other ports.

Your tasks are:

1. Define a multicast group per port. For each multicast group associate a node that contains all the ports but one.

2. Define a Mac forwarding table like in the previous exercise (you can mainly copy it). Remember to add the cli commands accordingly. This time
your default action does not need to be `broadcast`; it can be an empty action or `NoAction`.

3. Define a new match-action table that matches packet's `ingress_port` and sets the multicast group accordingly. Also define
the action that will be called by the table to set the multicast group.

4. Fill the table entries using the cli file. The entries should match to an ingress port and provide as an action parameter a
multicast group id.

5. Apply the forwarding table, and check if it matched. To do that you can use `table.apply().hit` or `table.apply().action_run` you can
find more information about table hits and misses in the [P4 16 specification](https://p4.org/p4-spec/docs/P4-16-v1.2.2.html#sec-invoke-mau). If there is a
miss (packet needs to be broadcasted) you will have to apply new table defined in `TODO 3` which will set the multicast group.


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
