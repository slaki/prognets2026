# 03-L2_Basic_forwarding
In today's first exercise we will implement a very basic layer 2 forwarding switch. In order to
tell the switch how to forward frames, the switch needs to know in which port it can find a given MAC
address (hosts). Real life switches automatically learn this mapping by using the l2 learning algorithm (we will see
this later today). In order to familiarize ourselves with tables and how to map ethernet addresses to a given host (port)
we will implement a very basic l2 forwarding that statically maps mac addresses to ports.

<p align="center">
<img src="images/l2_topology.png" title="L2 Star Topology">
<p/>


## Network Scenario
It is composed by four hosts `hx` and one switch `s1`. 
In order to familiarize with tables and how to map ethernet addresses to a given host (port), 
the switch implement a very basic l2 forwarding that statically maps mac addresses to ports.

## Implementing the L2 Basic Forwarding

To solve this exercise you only need to fill the gaps that you will find in the
`l2_basic_forwarding.p4` skeleton. The places where you are supposed to write your own code
are marked with a `TODO`. Furthermore, you will need to create a file called `s1-commands.txt`
with commands to fill your tables.

In summary, your tasks are:

1. Define the ethernet header, an empty `struct` for the `metadata`, and the
   `struct` called `headers` listing the ethernet header.

2. Parse the ethernet header.

3. Define a match-action table to make switch behave as a l2 packet forwarder. The destination
Mac address of each packet should tell the switch which output port use. You can use your last exercise
as a reminder, or check the [documentation](https://github.com/nsg-ethz/p4-learning/wiki/Control-Plane).

4. Define the action the table will call for matching entries. The action should get
the output port index as a parameter and set it to the `egress_spec` switch's metadata field.

5. Apply the table you defined.

6. Deparse the ethernet header to add it back to the wire.

7. Write the `s1-commands.txt` file. This file should contain all the `cli` commands needed to fill
the forwarding table you defined in 3. For more information about adding entries to the table check the
[control plane documentation](https://github.com/nsg-ethz/p4-learning/wiki/Control-Plane).

   **Important Note**: In order to fill the table you will need two things:

     1. Host's MAC addresses: by default hosts get assigned MAC addresses using the following pattern: `00:00:<IP address to hex>`. For example
     if `h1` IP's address were `10.0.1.5` the Mac address would be: `00:00:0a:00:01:05`. Alternatively, you can use `iconfig`/`ip` directly in a
     host's terminal.

     2. Switch port index each host is connected to. There are several ways to figure out the `port_index` to interface mapping. By default
     p4-utils add ports in the same order they are found in the `links` list in the `p4app.json` conf file. Thus, with the current configuration
     the port assignment would be: {h1->1, h2->2, h3->3, h4->4}. However, this basic port assignment might not hold for more complex topologies. Another
     way of finding out port mappings is checking the messages printed by when running the `p4run` command:

         ```
         Switch port mapping:
         s1:  1:h1       2:h2    3:h3    4:h4
         ```

        In future exercises we will see an extra way to get topology information.


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
