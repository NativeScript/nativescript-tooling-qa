import json
import os
import time

from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.image_utils import ImageUtils
from core.utils.process import Run
from core.utils.wait import Wait


# noinspection PyShadowingBuiltins
class Simctl(object):

    @staticmethod
    def __run_simctl_command(command, wait=True, timeout=30):
        command = '{0} {1}'.format('xcrun simctl', command)
        return Run.command(cmd=command, wait=wait, timeout=timeout)

    @staticmethod
    def __get_simulators():
        logs = Simctl.__run_simctl_command(command='list --json devices', wait=False).log_file
        found = Wait.until(lambda: 'iPhone' in File.read(logs), time=30)
        if found:
            return json.loads(File.read(logs))
        else:
            Log.error(File.read(logs))
            raise Exception('Failed to list iOS Devices!')

    @staticmethod
    def start(simulator_info):
        if simulator_info.id is not None:
            Simctl.__run_simctl_command(command='boot {0}'.format(simulator_info.id))
            Simctl.wait_until_boot(simulator_info)
            return simulator_info
        else:
            raise Exception('Can not boot iOS simulator if udid is not specified!')

    @staticmethod
    def is_running(simulator_info):
        sims = Simctl.__get_simulators()['devices']['iOS {0}'.format(simulator_info.sdk)]
        for sim in sims:
            if sim['name'] == simulator_info.name and sim['state'] == 'Booted':
                # simctl returns Booted too early, so we will wait some untill service is started
                simulator_info.id = sim['udid']
                command = 'spawn {0} launchctl print system | grep com.apple.springboard.services'.format(
                    simulator_info.id)
                service_state = Simctl.__run_simctl_command(command=command)
                if "M   A   com.apple.springboard.services" in service_state.output:
                    Log.info('Simulator "{0}" booted.'.format(simulator_info.name))
                    return simulator_info
        return False

    @staticmethod
    def wait_until_boot(simulator_info, timeout=180):
        """
        Wait until iOS Simulator is up and running.
        :param simulator_info: SimulatorInfo object.
        :param timeout: Timeout until device is ready (in seconds).
        :return: SimulatorInfo object with defined id, otherwise - False.
        """
        booted = False
        start_time = time.time()
        end_time = start_time + timeout
        while not booted:
            time.sleep(2)
            booted = Simctl.is_running(simulator_info)
            if booted or time.time() > end_time:
                return booted
        return booted

    @staticmethod
    def is_available(simulator_info):
        sims = Simctl.__get_simulators()['devices']['iOS {0}'.format(simulator_info.sdk)]
        for sim in sims:
            if sim['name'] == simulator_info.name:
                simulator_info.id = sim['udid']
                return simulator_info
        return False

    @staticmethod
    def stop_application(simulator_info, app_id):
        return Simctl.__run_simctl_command('terminate {0} {1}'.format(simulator_info.id, app_id))

    @staticmethod
    def install(simulator_info, path):
        result = Simctl.__run_simctl_command('install {0} {1}'.format(simulator_info.id, path))
        assert result.exit_code == 0, 'Failed to install {0} on {1}'.format(path, simulator_info.name)
        assert 'Failed to install the requested application' not in result.output, \
            'Failed to install {0} on {1}'.format(path, simulator_info.name)

    @staticmethod
    def uninstall(simulator_info, app_id):
        result = Simctl.__run_simctl_command('uninstall {0} {1}'.format(simulator_info.id, app_id))
        assert result.exit_code == 0, 'Failed to uninstall {0} on {1}'.format(app_id, simulator_info.name)
        assert 'Failed to uninstall the requested application' not in result.output, \
            'Failed to uninstall {0} on {1}'.format(app_id, simulator_info.name)

    @staticmethod
    def get_screen(id, file_path):
        File.clean(file_path)
        result = Simctl.__run_simctl_command('io {0} screenshot {1}'.format(id, file_path))
        assert result.exit_code == 0, 'Failed to get screenshot of {0}'.format(id)
        assert File.exists(file_path), 'Failed to get screenshot of {0}'.format(id)

    @staticmethod
    def get_screen_text(id):
        img_name = "actual_{0}_{1}.png".format(id, time.time())
        actual_image_path = os.path.join(Settings.TEST_OUT_IMAGES, img_name)
        File.clean(actual_image_path)
        Simctl.get_screen(id=id, file_path=actual_image_path)
        return ImageUtils.get_text(image_path=actual_image_path)

    @staticmethod
    def is_text_visible(id, text, case_sensitive=False):
        if case_sensitive:
            if text in Simctl.get_screen_text(id=id):
                return True
            else:
                return False
        else:
            if text.lower() in Simctl.get_screen_text(id=id).lower():
                return True
            else:
                return False
