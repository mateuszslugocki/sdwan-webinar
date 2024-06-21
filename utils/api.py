import logging
from typing import Any

from catalystwan.dataclasses import Device
from catalystwan.session import ManagerSession
from retry import retry

logger = logging.getLogger(__name__)


LOOK_FOR_DEVICE_ON_VMANAGE_TRIES = 3
LOOK_FOR_DEVICE_ON_VMANAGE_DELAY = 10


class DeviceOnManagerNotFoundException(Exception):
    """Raised when Device object on vManage was not found"""


@retry(
    exceptions=DeviceOnManagerNotFoundException,
    tries=LOOK_FOR_DEVICE_ON_VMANAGE_TRIES,
    delay=LOOK_FOR_DEVICE_ON_VMANAGE_DELAY,
    logger=logger,
)
def get_device_from_manager(manager: ManagerSession, **kwargs: Any) -> Device:
    """Gets Device dataclass from given Manager. This device can be used
    in Manager api calls, for instance for attaching device templates.

    Args:
        manager (ManagerSession)
        kwargs (Any): You can define by which value you want to filter. For instance,
        you can pass kwargs like: {hostname: pm9001} and then only device with hostname pm9001
        will be provided

    Returns:
        Device (catalystwan.dataclasses.Device)
    """

    all_devices = manager.api.devices.get()
    device = all_devices.filter(**kwargs).single_or_default()
    if not device:
        logger.error(
            f"Device {kwargs} was not found on Manager! Available devices: {all_devices}"
        )
        raise DeviceOnManagerNotFoundException
    return device
