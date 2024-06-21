import concurrent.futures
import logging
from typing import List

from pyats.topology import Device

logger = logging.getLogger(__name__)


def connect(device: Device) -> None:
    logger.info(f"Connecting with device: {device.name}")
    device.connect()


def connect_with_devices(devices: List[Device]) -> None:
    logger.info(f"Connecting with devices: {devices}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(devices)) as executor:
        futures = [executor.submit(connect, device) for device in devices]
        [future.result() for future in futures]


def disconnect(device: Device) -> None:
    logger.info(f"Disconnecting from device: {device.name}")
    device.disconnect()


def disconnect_devices(devices: List[Device]) -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(devices)) as executor:
        futures = [executor.submit(disconnect, device) for device in devices]
        [future.result() for future in futures]
