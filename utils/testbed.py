import logging
from typing import Callable, List

from pyats.topology import Device, Interface, Testbed

from utils.enums import DeviceOS

logger = logging.getLogger(__name__)


def get_iosxe_routers(testbed: Testbed) -> List[Device]:
    return [
        device
        for device in testbed.devices.values()
        if device.os == DeviceOS.IOSXE.value
    ]


def get_interfaces_by_condition(
    device: Device, condition: Callable[[Interface], bool]
) -> List[Interface]:
    return [
        interface for interface in device.interfaces.values() if condition(interface)
    ]


def get_device_by_name(
    testbed: Testbed, name: str, testcase: Optional[aetest.Testcase] = None
) -> Device:
    try:
        return testbed.devices[name]
    except KeyError:
        fail_msg = f"Device with given name: {name} doesn't exist!"
        logger.error(fail_msg)
        if not testcase:
            raise KeyError
        testcase.errored(fail_msg)


def get_devices_by_condition(
    devices: List[Device], condition: Callable[[Device], bool]
) -> List[Device]:
    """Finds device in testbed based on provided condition.
    Args:
        devices (List[Device]): List of Device objects
        condition (Callable[..., bool]): An anonymous function specifying the condition.
    Raises:
        Exception: Raised when device cannot be found based on condition.
    Returns:
        List of PyATS/Genie devices
    """
    return [device for device in devices if condition(device)]


def get_cedges(testbed: Testbed, sdwan: bool = True) -> List[Device]:
    return [
        device
        for device in testbed.devices.values()
        if device.os == DeviceOS.IOSXE.value
        and (device.platform == "sdwan" if sdwan else True)
    ]
