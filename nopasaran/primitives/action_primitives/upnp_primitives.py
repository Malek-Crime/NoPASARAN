import miniupnpc
import nopasaran.utils as utils
from nopasaran.decorators import parsing_decorator

class UpnpPrimitives:
    """
    Class containing UPnP action primitives for the state machine.
    """

    @staticmethod
    @parsing_decorator(input_args=0, output_args=4)
    def discover(inputs, outputs, state_machine):
        """
        Discover UPnP devices on the network and return discovery results.
        
        Number of input arguments: 0
        
        Number of output arguments: 4
            - UPnP object (or None)
            - LAN IP address (or None)
            - External IP address (or None)
            - Number of devices discovered
        """
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200  # milliseconds
        
        try:
            num_devices = upnp.discover()
            print("Devices discovered:", num_devices)

            if num_devices > 0:
                upnp.selectigd()
                lan_ip = upnp.lanaddr
                external_ip = upnp.externalipaddress()
                print("Selected UPnP device:")
                print("  LAN IP address:", lan_ip)
                print("  External IP address:", external_ip)

                state_machine.set_variable_value(outputs[0], upnp)
                state_machine.set_variable_value(outputs[1], lan_ip)
                state_machine.set_variable_value(outputs[2], external_ip)
                state_machine.set_variable_value(outputs[3], num_devices)

            else:
                print("No UPnP devices found.")
                state_machine.set_variable_value(outputs[0], None)
                state_machine.set_variable_value(outputs[1], None)
                state_machine.set_variable_value(outputs[2], None)
                state_machine.set_variable_value(outputs[3], 0)

        except Exception as e:
            print("Error during UPnP discovery:", str(e))
            state_machine.set_variable_value(outputs[0], None)
            state_machine.set_variable_value(outputs[1], None)
            state_machine.set_variable_value(outputs[2], None)
            state_machine.set_variable_value(outputs[3], 0)


    @staticmethod
    @parsing_decorator(input_args=6, output_args=2)
    def add_port_mapping(inputs, outputs, state_machine):
        """
        Add a port mapping using UPnP, using discovered UPnP device info.
        
        Number of input arguments: 6
            - UPnP object (from discover)
            - LAN IP address (from discover)
            - External IP address (from discover)
            - External port to open.
            - Internal port on the local machine.
            - Protocol (e.g., 'TCP' or 'UDP').
        
        Number of output arguments: 2
        """
        upnp = state_machine.get_variable_value(inputs[0])
        lan_addr = state_machine.get_variable_value(inputs[1])
        external_ip = state_machine.get_variable_value(inputs[2])
        external_port = state_machine.get_variable_value(inputs[3])
        internal_port = state_machine.get_variable_value(inputs[4])
        protocol = state_machine.get_variable_value(inputs[5])
        
        if upnp:
            result = upnp.addportmapping(int(external_port), protocol, lan_addr, int(internal_port), 'Nopasaran mapping', '')
            if result:
                print(f"Port mapping added: external port {external_port} -> {lan_addr}:{internal_port} [{protocol}]")
                state_machine.set_variable_value(outputs[0], external_ip)
                state_machine.set_variable_value(outputs[1], external_port)
            else:
                print("Failed to add port mapping.")
        else:
            print("No UPnP device found. Cannot add port mapping.")