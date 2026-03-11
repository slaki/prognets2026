#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

# Execute: python3 mycontroller.py --p4info l2_learning_copy_to_cpu.p4info.txt --bmv2-json l2_learning_copy_to_cpu.json

import argparse
import os
import sys
from time import sleep

import grpc
import p4runtime_lib.bmv2
import p4runtime_lib.helper
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import shlex
import subprocess
from scapy.all import sniff, Packet, BitField
from scapy.layers.l2 import Ether

from threading import Lock

class CpuHeader(Packet):
    name = 'CpuPacket'
    fields_desc = [BitField('macAddr', 0, 48), BitField('ingress_port', 0, 16)]

def writeIgressMatch(p4info_helper, sw, port, mcastgrp):
    
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.igress_match",
        match_fields={
            "standard_metadata.ingress_port": port
        },
        action_name="MyIngress.multicast_group",
        action_params={"mcast_group": mcastgrp})    
    sw.WriteTableEntry(table_entry)
    print("Installed igress_match rule on %s" % sw.name)

def writeMacAddresses(p4info_helper, sw, port, eth_addr):
    
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.smac",
        match_fields={
            "hdr.ethernet.srcAddr": eth_addr
        },
        action_name="NoAction",
        action_params={})
    sw.WriteTableEntry(table_entry)
    print("Installed smac rule on %s" % sw.name)

    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.dmac_forward",
        match_fields={
            "hdr.ethernet.dstAddr": eth_addr
        },
        action_name="MyIngress.forward_to_port",
        action_params={
            "egress_port": port
        })
    sw.WriteTableEntry(table_entry)
    print("Installed dmac_forward rule on %s" % sw.name)


def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print('\n----- Reading tables rules for %s -----' % sw.name)
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs in the entry to names
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print('%s: ' % table_name, end=' ')
            for m in entry.match:
                print(p4info_helper.get_match_field_name(table_name, m.field_id), end=' ')
                print('%r' % (p4info_helper.get_match_field_value(m),), end=' ')
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print('->', action_name, end=' ')
            for p in action.params:
                print(p4info_helper.get_action_param_name(action_name, p.param_id), end=' ')
                print('%r' % p.value, end=' ')
            print()

def printCounter(p4info_helper, sw, counter_name, index):
    """
    Reads the specified counter at the specified index from the switch. In our
    program, the index is the tunnel ID. If the index is 0, it will return all
    values from the counter.

    :param p4info_helper: the P4Info helper
    :param sw:  the switch connection
    :param counter_name: the name of the counter from the P4 program
    :param index: the counter index (in our case, the tunnel ID)
    """
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            print("%s %s %d: %d packets (%d bytes)" % (
                sw.name, counter_name, index,
                counter.data.packet_count, counter.data.byte_count
            ))

def printGrpcError(e):
    print("gRPC Error:", e.details(), end=' ')
    status_code = e.code()
    print("(%s)" % status_code.name, end=' ')
    traceback = sys.exc_info()[2]
    print("[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno))

def AddMulticastGroup(p4info_helper, sw, mcast_group_id, ports):
    """
    Adds a multicast group entry to the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    :param mcast_group_id: the multicast group ID
    :param ports: the list of output ports for this multicast group
    """
    mc = p4info_helper.buildMulticastGroupEntry(
    multicast_group_id=mcast_group_id,
    replicas=[{'egress_port': port, 'instance': 0} for port in ports]
    )
    sw.WritePREEntry(mc)
    print("Added multicast group %d with ports %s on %s" % (mcast_group_id, ports, sw.name))

class L2Controller(object):
    def __init__(self, p4info_helper, sw):
        self.p4info_helper = p4info_helper
        self.sw = sw
        self.mutex = Lock()

    def learn(self, learning_data):
        for mac_addr, ingress_port in learning_data:
            print("mac: %012X ingress_port: %s " % (mac_addr, ingress_port))
            mac_in_string = ':'.join(format(s, '02x') for s in bytes.fromhex('%012X' % mac_addr))
            writeMacAddresses(self.p4info_helper, self.sw, port=ingress_port, eth_addr=mac_in_string)

    def recv_msg_cpu(self, packet):
        if packet.type == 0x1234:
            cpu_header = CpuHeader(bytes(packet.payload))
            with self.mutex:
                try:
                    self.learn([(cpu_header.macAddr, cpu_header.ingress_port)])
                except grpc.RpcError as e:
                    printGrpcError(e)
                    
    def run_cpu_port_loop(self):
        sniff(iface="cpu", prn=self.recv_msg_cpu)
        sleep(1)


def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1 and s2;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:9559',
            device_id=0,
            proto_dump_file='logs.txt')

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()

        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s1")
        
        # Setup multicasting
        AddMulticastGroup(p4info_helper, s1, mcast_group_id=1, ports=[2,3,4])
        AddMulticastGroup(p4info_helper, s1, mcast_group_id=2, ports=[1,3,4])
        AddMulticastGroup(p4info_helper, s1, mcast_group_id=3, ports=[1,2,4])
        AddMulticastGroup(p4info_helper, s1, mcast_group_id=4, ports=[1,2,3])

        #Setup mirroring
        clone_entry = p4info_helper.buildCloneSessionEntry(100, [{'egress_port': 5, 'instance': 1}] )
        s1.WritePREEntry(clone_entry)

        # Setup ingress table entries for multicast
        writeIgressMatch(p4info_helper, s1, port=1, mcastgrp=1)
        writeIgressMatch(p4info_helper, s1, port=2, mcastgrp=2)
        writeIgressMatch(p4info_helper, s1, port=3, mcastgrp=3)
        writeIgressMatch(p4info_helper, s1, port=4, mcastgrp=4)

        # An example of how to write a forwarding rule to the switch. The rule says:
        writeMacAddresses(p4info_helper, s1, port=2, eth_addr="00:00:0a:00:00:02")  


        # TODO Uncomment the following two lines to read table entries from s1 and s2
        readTableRules(p4info_helper, s1)

        controller = L2Controller(p4info_helper, s1)
        controller.run_cpu_port_loop()

        # Print the tunnel counters every 2 seconds
        # while True:
        #    sleep(2)
        #    print('\n----- Reading tunnel counters -----')
        #    printCounter(p4info_helper, s1, "MyIngress.ingressTunnelCounter", 100)
        #    printCounter(p4info_helper, s2, "MyIngress.egressTunnelCounter", 100)
        #    printCounter(p4info_helper, s2, "MyIngress.ingressTunnelCounter", 200)
        #    printCounter(p4info_helper, s1, "MyIngress.egressTunnelCounter", 200)

    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/advanced_tunnel.p4.p4info.txtpb')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/advanced_tunnel.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)
    main(args.p4info, args.bmv2_json)
