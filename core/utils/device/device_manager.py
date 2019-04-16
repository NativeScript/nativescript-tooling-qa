import os

from core.base_test.test_context import TestContext
from core.enums.device_type import DeviceType
from core.log.log import Log
from core.utils.device.adb import Adb, ANDROID_HOME
from core.utils.device.device import Device
from core.utils.device.idevice import IDevice
from core.utils.device.simctl import Simctl
from core.utils.file_utils import Folder
from core.utils.java import Java
from core.utils.process import Process
from core.utils.run import run


class DeviceManager(object):
    @staticmethod
    def get_devices(device_type=any):
        devices = []
        # Get Android devices
        if device_type is DeviceType.ANDROID or device_type is any:
            for device_id in Adb.get_ids(include_emulators=False):
                version = Adb.get_version(device_id=device_id)
                device = Device(id=device_id, name=device_id, type=DeviceType.ANDROID, version=version)
                devices.append(device)
        # Get iOS devices
        if device_type is DeviceType.IOS or device_type is any:
            for device_id in IDevice.get_devices():
                device = Device(id=device_id, name=device_id, type=DeviceType.IOS, version=None)
                devices.append(device)

        for device in devices:
            TestContext.STARTED_DEVICES.append(device)
        return devices

    @staticmethod
    def get_device(device_type):
        devices = DeviceManager.get_devices(device_type=device_type)
        if devices:
            return devices[0]
        else:
            raise Exception('Failed to find {0} device.'.format(device_type))

    class Emulator(object):
        # noinspection SpellCheckingInspection
        @staticmethod
        def stop():
            """
            Stop all running emulators.
            """
            Log.info('Stop all running emulators...')
            Process.kill_by_commandline('qemu')
            Process.kill_by_commandline('emulator64')

            Process.kill('emulator64-arm')
            Process.kill('emulator64-x86')
            Process.kill('emulator-arm')
            Process.kill('emulator-x86')
            Process.kill('qemu-system-arm')
            Process.kill('qemu-system-i386')
            Process.kill('qemu-system-i38')

        @staticmethod
        def start(emulator):
            # Define emulator start options and command
            emulator_path = os.path.join(ANDROID_HOME, 'emulator', 'emulator')
            options = '-port {0} -wipe-data -no-snapshot-save -no-boot-anim -no-audio -netspeed lte'.format(
                emulator.port)

            # Check if clean snapshot is available and use it
            snapshot_name = 'clean_boot'
            home = os.path.expanduser("~")
            snapshot = os.path.join(home, '.android', 'avd', '{0}.avd'.format(emulator.avd), 'snapshots', snapshot_name)
            if Folder.exists(snapshot):
                Log.info('{0} has clean boot snapshot! Will user it.'.format(emulator.avd))
                options = '-port {0} -no-snapshot-save -no-boot-anim -no-audio -snapshot {1}'.format(emulator.port,
                                                                                                     snapshot_name)

            command = '{0} @{1} {2}'.format(emulator_path, emulator.avd, options)
            Log.info('Booting {0} with cmd:'.format(emulator.avd))
            Log.info(command)
            run(cmd=command, wait=False, register=False)
            booted = Adb.wait_until_boot(device_id=emulator.emu_id)
            if booted:
                Log.info('{0} is up and running!'.format(emulator.avd))
                device = Device(id=emulator.emu_id, name=emulator.avd, type=DeviceType.EMU, version=emulator.os_version)
                TestContext.STARTED_DEVICES.append(device)
                return device
            else:
                raise Exception('Failed to boot {0}!'.format(emulator.avd))

        @staticmethod
        def is_available(avd_name):
            if Java.version() > 1.8:
                Log.warning('Can not check if {0} is available, because avdmanager is not compatible with java {1}.'
                            .format(avd_name, Java.version()))
                return True
            else:
                avd_manager = os.path.join(ANDROID_HOME, 'tools', 'bin', 'avdmanager')
                result = run(cmd='{0} list avd'.format(avd_manager))
                avds = result.output.splitlines()
                for avd in avds:
                    if avd_name in avd:
                        return True
                return False

        @staticmethod
        def is_running(emulator):
            """
            Check if device is running
            :param emulator: EmulatorInfo object.
            :return: True if running, False if not running.
            """
            if Adb.is_running(device_id=emulator.emu_id):
                if str(emulator.os_version) in Adb.get_device_version(device_id=emulator.emu_id):
                    return True
            return False

        @staticmethod
        def ensure_available(emulator, force_start=False):
            if DeviceManager.Emulator.is_running(emulator=emulator) and not force_start:
                return emulator
            elif DeviceManager.Emulator.is_available(avd_name=emulator.avd):
                return DeviceManager.Emulator.start(emulator)
            else:
                raise Exception('{0} emulator not available! Plase create it.'.format(emulator.avd))

    # noinspection PyShadowingBuiltins
    class Simulator(object):
        @staticmethod
        def create(simulator_info):
            cmd = 'xcrun simctl create {0} "{1}" com.apple.CoreSimulator.SimRuntime.iOS-{2}' \
                .format(simulator_info.name, simulator_info.device_type, str(simulator_info.sdk).replace('.', '-'))
            result = run(cmd=cmd, timeout=60)
            assert result.exit_code == 0, 'Failed to create iOS Simulator with name {0}'.format(simulator_info.name)
            assert '-' in result.output, 'Failed to create iOS Simulator with name {0}'.format(simulator_info.name)
            simulator_info.id = result.output.splitlines()[0]
            return simulator_info

        @staticmethod
        def stop(sim_id='booted'):
            """
            Stop running simulators (by default stop all simulators)
            :param sim_id: Device identifier (Simulator ID)
            """
            if sim_id == 'booted':
                Log.info('Stop all running simulators.')
                Process.kill('Simulator')
                Process.kill('tail')
                Process.kill('launchd_sim')
                Process.kill_by_commandline('CoreSimulator')
            else:
                Log.info('Stop simulator with id ' + sim_id)
                run(cmd='xcrun simctl shutdown {0}'.format(sim_id), timeout=60)

        @staticmethod
        def start(simulator_info):
            # Start iOS Simulator
            Log.info('Booting {0} ...'.format(simulator_info.name))
            simulator_info = Simctl.start(simulator_info=simulator_info)

            # Start GUI
            if Process.get_proc_by_commandline('Simulator.app') is not None:
                Log.debug('Simulator GUI is already running.')
            else:
                Log.info('Start simulator GUI.')
                run(cmd='open -a Simulator')

            # Return result
            device = Device(id=simulator_info.id, name=simulator_info.name, type=DeviceType.SIM,
                            version=simulator_info.sdk)
            TestContext.STARTED_DEVICES.append(device)
            return device

        @staticmethod
        def is_available(simulator_info):
            return Simctl.is_available(simulator_info=simulator_info)

        @staticmethod
        def is_running(simulator_info):
            return Simctl.is_running(simulator_info=simulator_info)

        @staticmethod
        def ensure_available(simulator_info):
            if DeviceManager.Simulator.is_running(simulator_info=simulator_info):
                return Device(id=simulator_info.id,
                              name=simulator_info.name,
                              type=DeviceType.SIM,
                              version=simulator_info.sdk)
            elif DeviceManager.Simulator.is_available(simulator_info=simulator_info):
                return DeviceManager.Simulator.start(simulator_info)
            else:
                simulator_info = DeviceManager.Simulator.create(simulator_info=simulator_info)
                return DeviceManager.Simulator.start(simulator_info)
