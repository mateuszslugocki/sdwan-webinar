import logging

from catalystwan.dataclasses import Device as DeviceOnManager
from catalystwan.session import ManagerSession, create_manager_session
from pyats import aetest
from pyats.topology import Device, Testbed

from utils.api import get_device_from_manager
from utils.connection import disconnect_devices
from utils.testbed import (get_cedges, get_device_by_name,
                           get_interfaces_by_condition)
from utils.wait_utils import countdown

logger = logging.getLogger(__name__)

MANAGER_SESSION = "manager_session"
DUT = "dut"
DUT_ON_MANAGER = "dut_on_manager"
INTERFACE_TO_DISABLE = "interface_to_disable"
WAIT_TIME_BEFORE_CHECK_BFD = 15
COMMON_CLEANUP_SECTION = ["common_cleanup"]


def are_all_bfds_up(
    manager_session: ManagerSession, dut_on_manager: DeviceOnManager
) -> bool:
    devices_health = manager_session.api.dashboard.get_devices_health()
    dut_device_health = devices_health.devices.find(name=dut_on_manager.hostname)
    dut_expected_bfd_sessions = dut_device_health.bfd_sessions
    dut_up_bfd_sessions = dut_device_health.bfd_sessions_up
    if dut_expected_bfd_sessions != dut_up_bfd_sessions:
        msg = (
            f"BFD is still not fully up! Expected: {dut_expected_bfd_sessions}, UP: {dut_up_bfd_sessions}"
            if dut_expected_bfd_sessions
            else f"Connection with controllers is not established yet"
        )
        logger.warning(msg)
        return False
    logger.info(
        f"All BFD sessions are UP. Expected: {dut_expected_bfd_sessions}, UP: {dut_up_bfd_sessions}"
    )
    return True


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def establish_session_with_manager(
        self, testbed: Testbed, manager_name: str = "vmanage"
    ) -> None:
        manager = get_device_by_name(testbed, manager_name)
        manager_ip = str(manager.connections.https.ip)
        manager_username = manager.credentials.default.username
        manager_password = manager.credentials.default.password.plaintext
        manager_session = create_manager_session(
            manager_ip, manager_username, manager_password
        )
        self.parent.parameters[MANAGER_SESSION] = manager_session

    @aetest.subsection
    def get_dut(self, testbed: Testbed, site_name: str) -> None:
        get_cedges(testbed)
        dut = get_device_by_name(testbed, site_name)
        self.parent.parameters[DUT] = dut

    @aetest.subsection
    def get_dut_from_manager(self, dut: Device) -> None:
        dut_on_manager = get_device_from_manager(dut)
        self.parent.parameters[DUT_ON_MANAGER] = dut_on_manager

    @aetest.subsection
    def get_interface_for_outage_simulation(
        self, dut: Device, interface_alias: str
    ) -> None:
        try:
            interface = get_interfaces_by_condition(
                dut, lambda interface: interface.alias == interface_alias
            )[0]
        except IndexError:
            logger.warning(
                f"Interface with alias {interface_alias} was not found!\nPlease verify your testbed yaml"
            )
            self.failed(
                f"Interface with alias {interface_alias} was not found!\nPlease verify your testbed yaml",
                goto=COMMON_CLEANUP_SECTION,
            )
        self.parent.parameters[INTERFACE_TO_DISABLE] = interface.name


class BFDTest(aetest.Testcase):
    @aetest.test
    def check_bfd_sessions_before_failure(
        self, manager_session: ManagerSession, dut_on_manager: DeviceOnManager
    ) -> None:
        if not are_all_bfds_up(manager_session, dut_on_manager):
            self.failed(f"Not all BFD sessions are up!")

    @aetest.test
    def simulate_outage(self, dut: Device, interface_to_disable: str) -> None:
        cmd = f"""
interface {interface_to_disable}
shutdown
"""
        dut.configure(cmd)
        countdown(WAIT_TIME_BEFORE_CHECK_BFD, "Waiting for sessions to go down")

    @aetest.test
    def check_bfd_sessions_with_outage(
        self, manager_session: ManagerSession, dut_on_manager: DeviceOnManager
    ) -> None:
        if are_all_bfds_up(manager_session, dut_on_manager):
            self.failed(f"All BFD sessions still are visible as up!")

    @aetest.test
    def remove_outage_simulation(self, dut: Device, interface_to_disable: str) -> None:
        cmd = f"""
interface {interface_to_disable}
no shutdown
"""
        dut.configure(cmd)
        countdown(WAIT_TIME_BEFORE_CHECK_BFD, "Waiting for sessions to go up")

    @aetest.test
    def check_bfd_sessions_without_outage(
        self, manager_session: ManagerSession, dut_on_manager: DeviceOnManager
    ) -> None:
        if not are_all_bfds_up(manager_session, dut_on_manager):
            self.failed(f"Not all BFD sessions are up!")


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_dut(self, dut: Device) -> None:
        logger.info(f"Disconnecting from dut: {dut.hostname}")
        disconnect_devices([dut])

    @aetest.subsection
    def close_session_with_manager(self, manager_session: ManagerSession) -> None:
        logger.info(f"Closing session with Manager")
        manager_session.close()
