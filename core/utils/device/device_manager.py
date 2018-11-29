import os

from core.base_test.test_context import TestContext
from core.enums.device_type import DeviceType
from core.log.log import Log
from core.utils.device.adb import Adb, ANDROID_HOME
from core.utils.device.device import Device
from core.utils.device.idevice import IDevice
from core.utils.device.simctl import Simctl
from core.utils.process import Run, Process


class DeviceManager(object):
    @staticmethod
    def get_devices(device_type=any):
        device_list = []

        if device_type is DeviceType.ANDROID or device_type is any:
            device_list = Adb.get_devices(include_emulators=False)

        if device_type is DeviceType.IOS or device_type is any:
            device_list = IDevice.get_devices()
        return device_list

    @staticmethod
    def get_device(device_type):
        devices = DeviceManager.get_devices(device_type=device_type)
        if len(devices) > 0:
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
        def start(emulator, wipe_data=True):
            emulator_path = os.path.join(ANDROID_HOME, 'emulator', 'emulator')
            base_options = '-no-snapshot-save -no-boot-anim -no-audio'
            options = '-port {0} {1}'.format(emulator.port, base_options)
            if wipe_data:
                options = '-port {0} -wipe-data {1}'.format(emulator.port, base_options)
            command = '{0} @{1} {2}'.format(emulator_path, emulator.avd, options)
            Log.info('Booting {0} with cmd:'.format(emulator.avd))
            Log.info(command)
            Run.command(cmd=command, wait=False, register_for_cleanup=False)
            booted = Adb.wait_until_boot(id=emulator.id)
            if booted:
                Log.info('{0} is up and running!'.format(emulator.avd))
                device = Device(id=emulator.id, name=emulator.avd, type=DeviceType.EMU, version=emulator.os_version)
                TestContext.STARTED_DEVICES.append(device)
                return device
            else:
                raise Exception('Failed to boot {0}!'.format(emulator.avd))

        @staticmethod
        def is_available(emulator):
            # TODO: Implement it.
            return True

        @staticmethod
        def is_running(emulator):
            """
            Check if device is running
            :param emulator: EmulatorInfo object.
            :return: True if running, False if not running.
            """
            if Adb.is_running(id=emulator.id):
                if str(emulator.os_version) in Adb.get_device_version(id=emulator.id):
                    return True
            return False

        @staticmethod
        def ensure_available(emulator, force_start=False):
            if DeviceManager.Emulator.is_running(emulator=emulator) and not force_start:
                pass
                # TODO: Implement it.
            elif DeviceManager.Emulator.is_available(emulator=emulator):
                return DeviceManager.Emulator.start(emulator)
            else:
                raise Exception('{0} emulator not available! Plase create it.'.format(emulator.avd))

    # noinspection PyShadowingBuiltins
    class Simulator(object):
        @staticmethod
        def create(simulator_info):
            cmd = 'xcrun simctl create {0} "{1}" com.apple.CoreSimulator.SimRuntime.iOS-{2}' \
                .format(simulator_info.name, simulator_info.device_type, str(simulator_info.sdk).replace('.', '-'))
            result = Run.command(cmd=cmd, timeout=60)
            assert result.exit_code == 0, 'Failed to create iOS Simulator with name {0}'.format(simulator_info.name)
            assert '-' in result.output, 'Failed to create iOS Simulator with name {0}'.format(simulator_info.name)
            simulator_info.id = result.output.splitlines()[0]
            return simulator_info

        @staticmethod
        def stop(id='booted'):
            """
            Stop running simulators (by default stop all simulators)
            :param id: Device identifier (Simulator GUID)
            """
            if id == 'booted':
                Log.info('Stop all running simulators.')
                Process.kill('Simulator')
                Process.kill('tail')
                Process.kill('launchd_sim')
                Process.kill_by_commandline('CoreSimulator')
            else:
                print 'Stop simulator with id ' + id
                Run.command(cmd='xcrun simctl shutdown {0}'.format(id), timeout=60)

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
                Run.command(cmd='open -a Simulator')

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
