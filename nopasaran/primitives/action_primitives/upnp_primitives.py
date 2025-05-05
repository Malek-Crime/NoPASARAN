import miniupnpc
import nopasaran.utils as utils
from nopasaran.decorators import parsing_decorator

class UpnpPrimitives:
    """
    Class containing UPnP action primitives for the state machine.
    """

    @staticmethod
    @parsing_decorator(input_args=0, output_args=3)
    def upnp_discover(inputs, outputs, state_machine):
        """
        Discover UPnP devices on the network and return discovery results.

        Outputs:
            - UPnP object or None
            - LAN IP address or None
            - External IP address or None
        """
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200

        # Default to None
        state_machine.set_variable_value(outputs[0], None)
        state_machine.set_variable_value(outputs[1], None)
        state_machine.set_variable_value(outputs[2], None)

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
            else:
                print("No UPnP devices found.")

        except Exception as e:
            print("Error during UPnP discovery:", e)


    @staticmethod
    @parsing_decorator(input_args=6, output_args=2)
    def upnp_add_port_mapping(inputs, outputs, state_machine):
        """
        Add a port mapping using UPnP.

        Outputs:
            - External IP or None
            - External port or None
        """
        upnp = state_machine.get_variable_value(inputs[0])
        lan_addr = state_machine.get_variable_value(inputs[1])
        external_ip = state_machine.get_variable_value(inputs[2])
        external_port = state_machine.get_variable_value(inputs[3])
        internal_port = state_machine.get_variable_value(inputs[4])
        protocol = state_machine.get_variable_value(inputs[5])

        # Default to None
        state_machine.set_variable_value(outputs[0], None)
        state_machine.set_variable_value(outputs[1], None)

        if upnp:
            try:
                result = upnp.addportmapping(
                    int(external_port),
                    protocol,
                    lan_addr,
                    int(internal_port),
                    'Nopasaran mapping',
                    ''
                )
                if result:
                    print(f"Port mapping added: {external_port} -> {lan_addr}:{internal_port} [{protocol}]")
                    state_machine.set_variable_value(outputs[0], external_ip)
                    state_machine.set_variable_value(outputs[1], external_port)
                else:
                    print("Failed to add port mapping.")
            except Exception as e:
                print("Error adding port mapping:", e)
        else:
            print("No UPnP device found.")



    @staticmethod
    @parsing_decorator(input_args=3, output_args=1)
    def upnp_delete_port_mapping(inputs, outputs, state_machine):
        """
        Delete a port mapping using UPnP.

        Output:
            - Success flag (True/False) or None
        """
        upnp = state_machine.get_variable_value(inputs[0])
        external_port = int(state_machine.get_variable_value(inputs[1]))
        protocol = state_machine.get_variable_value(inputs[2])

        # Default to None
        state_machine.set_variable_value(outputs[0], None)

        if upnp:
            try:
                result = upnp.deleteportmapping(external_port, protocol)
                print(f"Delete port mapping result for {external_port}/{protocol}: {result}")
                state_machine.set_variable_value(outputs[0], result)
            except Exception as e:
                print(f"Error deleting port mapping: {e}")
        else:
            print("No UPnP device found.")


    @staticmethod
    @parsing_decorator(input_args=3, output_args=1)
    def upnp_add_multiple_port_mappings(inputs, outputs, state_machine):
        """
        Add multiple port mappings to the current host (like `upnpc -r`).

        Dynamic number of inputs:
            - UPnP object
            - Internal IP
            - For each mapping: internal_port, [external_port], protocol

        Output:
            - List of successfully added mappings (dicts), or None if failure
        """
        outputs[0] = None  # Ensure output is always initialized
        upnp = state_machine.get_variable_value(inputs[0])
        internal_ip = state_machine.get_variable_value(inputs[1])
        results = []

        if upnp:
            try:
                args = inputs[2:]
                i = 0
                while i < len(args):
                    internal_port = int(state_machine.get_variable_value(args[i]))
                    i += 1
                    if i < len(args) and isinstance(state_machine.get_variable_value(args[i]), int):
                        external_port = int(state_machine.get_variable_value(args[i]))
                        i += 1
                    else:
                        external_port = internal_port  # default to same as internal

                    protocol = state_machine.get_variable_value(args[i])
                    i += 1

                    success = upnp.addportmapping(
                        external_port,
                        protocol,
                        internal_ip,
                        internal_port,
                        'NoPASARAN bulk mapping',
                        ''
                    )

                    results.append({
                        'internal_port': internal_port,
                        'external_port': external_port,
                        'protocol': protocol,
                        'success': success
                    })

                print(f"Added {len(results)} mappings.")
                state_machine.set_variable_value(outputs[0], results)
            except Exception as e:
                print("Error adding multiple port mappings:", e)
        else:
            print("No UPnP device found.")


    @staticmethod
    @parsing_decorator(input_args=1, output_args=2)
    def upnp_get_status(inputs, outputs, state_machine):
        """
        Get status of the current UPnP connection.

        Input:
        - UPnP object

        Outputs:
        - External IP address
        - Connection status (dict: {'status': int, 'uptime': int, 'last_connection_error': str})
        """
        outputs[0] = None
        outputs[1] = None

        upnp = state_machine.get_variable_value(inputs[0])
        if upnp:
            try:
                status = upnp.statusinfo()
                external_ip = upnp.externalipaddress()
                print("UPnP connection status:", status)
                state_machine.set_variable_value(outputs[0], external_ip)
                state_machine.set_variable_value(outputs[1], {
                    'status': status[0],
                    'uptime': status[1],
                    'last_connection_error': status[2]
                })
            except Exception as e:
                print("Error getting UPnP status:", e)
        else:
            print("No UPnP device found.")



    @staticmethod
    @parsing_decorator(input_args=1, output_args=1)
    def upnp_list_port_mappings(inputs, outputs, state_machine):
        """
        List current port mappings (upnpc -l style).

        Input:
            - UPnP object

        Output:
            - List of port mappings (tuples)
        """
        outputs[0] = None
        upnp = state_machine.get_variable_value(inputs[0])
        mappings = []

        if upnp:
            i = 0
            while True:
                try:
                    mapping = upnp.getgenericportmapping(i)
                    if mapping is None:
                        break
                    mappings.append(mapping)
                    i += 1
                except Exception:
                    break

            print(f"Found {len(mappings)} port mappings.")
            state_machine.set_variable_value(outputs[0], mappings)
        else:
            print("No UPnP device found.")


    @staticmethod
    @parsing_decorator(input_args=6, output_args=1)
    def upnp_add_any_port_mapping(inputs, outputs, state_machine):
        """
        Add any port mapping (allow IGD to use an alternative external port).
        Equivalent to: upnpc -n

        Inputs:
            - UPnP object
            - Internal IP
            - Internal port
            - Suggested external port
            - Protocol (TCP/UDP)
            - Duration (0 = permanent)

        Output:
            - Actual external port assigned
        """
        outputs[0] = None
        upnp = state_machine.get_variable_value(inputs[0])
        internal_ip = state_machine.get_variable_value(inputs[1])
        internal_port = int(state_machine.get_variable_value(inputs[2]))
        suggested_external_port = int(state_machine.get_variable_value(inputs[3]))
        protocol = state_machine.get_variable_value(inputs[4])
        duration = int(state_machine.get_variable_value(inputs[5]))

        if upnp:
            try:
                actual_port = upnp.addanyportmapping(
                    suggested_external_port,
                    protocol,
                    internal_ip,
                    internal_port,
                    'NoPASARAN any mapping',
                    '',
                    duration
                )
                print(f"Requested external port: {suggested_external_port}, Actual assigned: {actual_port}")
                state_machine.set_variable_value(outputs[0], actual_port)
            except Exception as e:
                print(f"Failed to add any port mapping: {e}")
        else:
            print("No UPnP device found.")


    @staticmethod
    @parsing_decorator(input_args=4, output_args=1)
    def upnp_delete_port_range(inputs, outputs, state_machine):
        """
        Delete a range of port mappings (IGD:2 only).
        Inputs:
            - UPnP object
            - Start port
            - End port
            - Protocol
        Output:
            - List of ports successfully deleted
        """
        outputs[0] = None
        upnp = state_machine.get_variable_value(inputs[0])
        port_start = int(state_machine.get_variable_value(inputs[1]))
        port_end = int(state_machine.get_variable_value(inputs[2]))
        protocol = state_machine.get_variable_value(inputs[3])
        deleted = []

        if upnp:
            for port in range(port_start, port_end + 1):
                try:
                    if upnp.deleteportmapping(port, protocol):
                        deleted.append(port)
                except Exception as e:
                    print(f"Failed to delete port {port}/{protocol}: {e}")
            print(f"Deleted ports: {deleted}")
            state_machine.set_variable_value(outputs[0], deleted)
        else:
            print("No UPnP device found.")



    @staticmethod
    @parsing_decorator(input_args=7, output_args=1)
    def upnp_add_pinhole(inputs, outputs, state_machine):
        """
        Add a pinhole rule (IGD:2 only).

        Inputs:
            - UPnP object
            - Remote IP
            - Remote port
            - Internal IP
            - Internal port
            - Protocol
            - Lease time (in seconds)

        Output:
            - Unique ID of the pinhole
        """
        outputs[0] = None
        upnp = state_machine.get_variable_value(inputs[0])
        remote_ip = state_machine.get_variable_value(inputs[1])
        remote_port = int(state_machine.get_variable_value(inputs[2]))
        internal_ip = state_machine.get_variable_value(inputs[3])
        internal_port = int(state_machine.get_variable_value(inputs[4]))
        protocol = state_machine.get_variable_value(inputs[5])
        lease_time = int(state_machine.get_variable_value(inputs[6]))

        if upnp:
            try:
                uid = upnp.AddPinhole(remote_ip, remote_port, internal_ip, internal_port, protocol, lease_time)
                print(f"Pinhole created. Unique ID: {uid}")
                state_machine.set_variable_value(outputs[0], uid)
            except Exception as e:
                print(f"Failed to add pinhole: {e}")
        else:
            print("No UPnP device found.")


    @staticmethod
    @parsing_decorator(input_args=3, output_args=1)
    def upnp_update_pinhole(inputs, outputs, state_machine):
        """
        Update the lease time of an existing pinhole.

        Inputs:
            - UPnP object
            - Unique ID
            - New lease time (seconds)

        Output:
            - Success flag (True/False)
        """
        outputs[0] = None
        upnp = state_machine.get_variable_value(inputs[0])
        uid = state_machine.get_variable_value(inputs[1])
        new_lease_time = int(state_machine.get_variable_value(inputs[2]))

        if upnp:
            try:
                result = upnp.UpdatePinhole(uid, new_lease_time)
                print(f"Update pinhole lease time result: {result}")
                state_machine.set_variable_value(outputs[0], result)
            except Exception as e:
                print(f"Failed to update pinhole: {e}")
        else:
            print("No UPnP device found.")





    @staticmethod
    @parsing_decorator(input_args=2, output_args=1)
    def upnp_get_pinhole_packet_count(inputs, outputs, state_machine):
        """
        Get number of packets that have passed through the pinhole (IGD:2 only).

        Inputs:
            - UPnP object
            - Unique ID

        Output:
            - Packet count (integer)
        """
        outputs[0] = None
        upnp = state_machine.get_variable_value(inputs[0])
        uid = state_machine.get_variable_value(inputs[1])

        if upnp:
            try:
                count = upnp.GetPinholePackets(uid)
                print(f"Pinhole {uid} packet count: {count}")
                state_machine.set_variable_value(outputs[0], count)
            except Exception as e:
                print(f"Failed to get packet count: {e}")
        else:
            print("No UPnP device found.")

    @staticmethod
    @parsing_decorator(input_args=2, output_args=1)
    def upnp_delete_pinhole(inputs, outputs, state_machine):
        """
        Delete a pinhole rule by unique ID (IGD:2 only).

        Inputs:
            - UPnP object
            - Unique ID

        Output:
            - True if deletion successful, False otherwise
        """
        outputs[0] = None
        upnp = state_machine.get_variable_value(inputs[0])
        uid = state_machine.get_variable_value(inputs[1])

        if upnp:
            try:
                result = upnp.DeletePinhole(uid)
                print(f"Pinhole {uid} deleted: {bool(result)}")
                state_machine.set_variable_value(outputs[0], bool(result))
            except Exception as e:
                print(f"Failed to delete pinhole: {e}")
        else:
            print("No UPnP device found.")