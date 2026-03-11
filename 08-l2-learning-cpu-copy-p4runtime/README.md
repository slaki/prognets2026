# 04-L2_Learning_CPU_Copy
This is the last exercise of our Basic L2 Switch series. In the first exercise we implemented a very basic l2 forwarding switch, then in the second exercise we made the switch a bit more realistic and added the feature of forwarding packets for unknown and broadcast destinations.

In this exercise we will add the cherry on the cake. We will make the switch a bit smarter and add to it the
capability of learning MAC addresses to port mappings autonomously, as a regular L2 switch would do. Thus,
we will not need to add manually the `mac_address` to `output_port` mapping as we were doing in the previous
exercises. Instead, now we will leave that table empty, and will let the switch (with the help of a controller)
fill it automatically.

L2 learning works as follows:

1. For every packet the switch receives, it checks if it has seen the `src_mac` address before. If its a new mac address,
it sends to the controller a tuple with (mac_address, ingress_port). The controller receives the packet and adds two rules
into the switch's tables. First it tells the switch that `src_mac` is known. Then, in another table it adds an entry to map
the mac address to a port (this table would be the same we used in the previous exercises).

2. The switch also checks if the `dst_mac` is known (using a normal forwarding table), if known the switch forwards
the packet normally, otherwise it broadcasts it. This second part of the algorithm has been already implemented in the previous
exercise.

In this exercise we will implement a learning switch. For that we need a controller code, and instruct the switch
to send the (mac, port) tuple to the controller. For the sake of learning, we will show you two different
ways of transmitting information to the controller: cloning packets to the controller (`cpu`) or sending digest messages.


## Network Scenario

This is the network scenario topology: 

![topology](images/l2_topology.png)

It is composed by four hosts `hx` and one switch `s1`. 
The switch is a bit smarter and has the capability of learning MAC 
addresses to port mappings autonomously, as a regular L2 switch would do.

L2 learning works as follows:

1. For every packet the switch receives, it checks if it has seen the `src_mac` address before. If its a new mac address,
it sends to the controller a tuple with (mac_address, ingress_port). The controller receives the packet and adds two rules
into the switch's tables. First it tells the switch that `src_mac` is known. Then, in another table it adds an entry to map
the mac address to a port (this table would be the same we used in the previous exercises).

2. The switch also checks if the `dst_mac` is known (using a normal forwarding table), if known the switch forwards
the packet normally, otherwise it broadcasts it. This second part of the algorithm has been already implemented in the previous
exercise.

For that we need a controller code, and instruct the switch to send the (mac, port) tuple to the controller.

In this exercise packets are sent to the controller after cloning them. 


## Implementing L2 Learning

For this exercise we will also use two different techniques, as described above. Since the learning switch also need to
flood unknown packets you will be able to reuse code from the previous exercise (however, all the steps will be listed in the
`TODOS`).

#### Learning Switch: cloning packets to the controller

For the first part of this exercise, use the files `p4app_cpu.json` and adapt the program skeleton in `l2_learning_copy_to_cpu.p4`.
To complete this exercise we will need to clone packets. When a learning packet needs to be sent to the controller the switch
will have to make a copy of the packet, send it to the controller, and then continue the pipeline normally with the original packet.
In order to help you with the cloning part, a section in the new `Simple Switch` documentation explains how to clone packets
using the simple switch target.

Your tasks are:

1. Read the [documentation section](https://github.com/nsg-ethz/p4-learning/wiki/BMv2-Simple-Switch#cloning-packets) that talks about packet cloning.

2. Define a `cpu_t` header that will be added to our original packet. This header needs two fields, one for the source mac address,
and one for the input port (48 and 16 bits respectively). Remember to cast the `standard_metadata.ingress_port` before assigning it to this header field (the
standard metadata field is 9 bits, but we need to send a multiple of 8 to the controller, and thus we use 16 bits).

3. Cloned packets get all the metadata reset. If we want to be able to know the `ingress_port` for our cloned packet we will need to put
that in a metadata field.

4. Add the new header to the headers struct.

5. Define a normal forwarding table, and call it `dmac`. The table should match to the packet's destination mac address, and
call a function `forward` that sets the output port. Set `NoAction` as default. Copy this from the previous exercise.

**Note:** The naming of these tables and actions needs to match the names you use in the controller code *precisely*.

6. Define a table named `broadcast` that matches to `ingress_port` and calls the action `set_mcast_grp` which sets the
multicast group for the packet, if needed. Define also the `set_mcast_grp` action. Copy this from the previous exercise.

7. Define a third and new table (and name it `smac`). This new table will be used to match source mac addresses. If there
is a match nothing should happen, if there is a miss, an action `mac_learn` should be called. The `mac_learn` action should
set the metadata field you defined in 3 to `standard_metadata.ingress_port` and call `clone3` with `CloneType.I2E` and  mirroring ID = 100.

**Note:** when using `clone3` with a non empty third parameter the compiler will complain with the following warning
`[--Wwarn=unsupported] warning: clone3: clone with non-empty argument not supported`. This is due to a bug in the implementation of
the software switch that they could not fix yet, however even if they say that it is not supported, the clone operation will work as intended.

8. Write the apply logic. First apply the `smac` table. Then the `dmac` and if it does not have a hit, apply the `broadcast` table.

9. When you call `clone3` the packet gets copied to the egress pipeline. Here you have to do several things.

   * First check that the `instance_type` is equal to 1 (which means that the packet is an ingress clone).
   * Now you will use the `cpu` header you defined in 2 to add the learning information we want to send to the controller. To
    enable the header you need to set it valid using `setValid()`.  Fill the `cpu` headers fields with the mac source port and
    ingress_port.
   * Finally set the `hdr.ethernet.etherType` to `0x1234`. The controller uses to filter packets.

10. Emit the new header you created (only valid headers are put back to the packet).

11. Implement the controllers learning function:

    At this point you will have your P4 program ready. Now is time to implement the controller.  However, since we did not explain
    how to write controller code using the P4 utils library we will provide you an almost complete solution. You will only need to implement
    a function called `learn`. The controller will handle automatically for you the following:

    1. Reset the switch state.
    2. Add Broadcast groups automatically.
    3. Add the mirror session ID and map it to the `CPU_PORT`.
    4. It will listen for `learning` packets and will parse them.

    Look for the `learn` function in the controller program `l2_learning_controller.py`. The function learn will be automatically called
    by the controller when the switch sends a packet to it. As a parameter it receives a list of tuples with (src_macs, ingress_ports). Use the
    method `self.controller.table_add()` to populate the `smac` and `dmac` tables accordingly. The `table_add` does the same than the CLI `table_add`
    command line.



## Testing the scenario
1. To run the network scenario, open a terminal in the scenario directory and type: 
```bash
kathara lstart 
```

2. For testing the P4 program, open a terminal on the switch and type:
```bash
python3 l2_learning_controller.py s1 cpu
```

3. Open a terminal on one host and ping the others
```bash
root@h2:/# ping 10.0.0.1 
```

3. If all the hosts can reach the others, the switch is working. 

4. Verify that the switch table was populated: 

```bash
simple_switch_CLI
Obtaining JSON from switch...
Done
Control utility for runtime P4 table manipulation
RuntimeCmd: table_dump dmac_forward
```
You will see an output like this: 

```bash
==========
TABLE ENTRIES
**********
Dumping entry 0x0
Match key:
* ethernet.dstAddr    : EXACT     56d591e9ef57
Action entry: MyIngress.forward_to_port - 01
**********
Dumping entry 0x1
Match key:
* ethernet.dstAddr    : EXACT     00000a000001
Action entry: MyIngress.forward_to_port - 01
**********
Dumping entry 0x2
Match key:
* ethernet.dstAddr    : EXACT     00000a000003
Action entry: MyIngress.forward_to_port - 03
**********
Dumping entry 0x3
Match key:
* ethernet.dstAddr    : EXACT     aaa069235413
Action entry: MyIngress.forward_to_port - 01
**********
Dumping entry 0x4
Match key:
* ethernet.dstAddr    : EXACT     ae216761d5b9
Action entry: MyIngress.forward_to_port - 04
**********
Dumping entry 0x5
Match key:
* ethernet.dstAddr    : EXACT     36552b7beee0
Action entry: MyIngress.forward_to_port - 02
**********
Dumping entry 0x6
Match key:
* ethernet.dstAddr    : EXACT     0aa1ec57b3e0
Action entry: MyIngress.forward_to_port - 03
**********
Dumping entry 0x7
Match key:
* ethernet.dstAddr    : EXACT     426904966112
Action entry: MyIngress.forward_to_port - 04
**********
Dumping entry 0x8
Match key:
* ethernet.dstAddr    : EXACT     327445290855
Action entry: MyIngress.forward_to_port - 03
==========
Dumping default entry
Action entry: NoAction - 
==========

```

