# pylint: disable=unused-argument
# TODO: Implement it!
import os
import time

from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File


# noinspection PyUnusedLocal
class TnsHelpers(object):

    @staticmethod
    def get_app_path(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(path, app_name)

    @staticmethod
    def get_app_node_modules_path(app_name, path=Settings.TEST_RUN_HOME):
        return os.path.join(TnsHelpers.get_app_path(app_name=app_name, path=path), 'node_modules')

    @staticmethod
    def get_apk(app_name):
        return ''

    @staticmethod
    def get_ipa(app_name):
        return ''

    @staticmethod
    def get_app(app_name):
        return ''

    @staticmethod
    def wait_for_log(log_file, string_list, not_existing_string_list=None, timeout=45, check_interval=3):
        """
        Wait until log file contains list of string.
        :param log_file: Path to log file.
        :param string_list: List of strings.
        :param not_existing_string_list: List of string that should not be in logs.
        :param timeout: Timeout.
        :param check_interval: Check interval.
        """
        end_time = time.time() + timeout
        all_items_found = False
        not_found_list = []
        log = ""
        verified_flag = '[VERIFIED]'
        while time.time() < end_time:
            not_found_list = []
            log = File.read(log_file)
            # Extract the part of the log that hasn't been previously verified
            if verified_flag in log:
                log = File.extract_part_of_text(log, verified_flag)
            for item in string_list:
                if item in log:
                    Log.info("'{0}' found.".format(item))
                else:
                    not_found_list.append(item)
            if not_found_list == []:
                all_items_found = True
                Log.info("Log contains: {0}".format(string_list))
                break
            else:
                Log.info("'{0}' NOT found. Wait...".format(not_found_list))
                time.sleep(check_interval)
            if 'BUILD FAILED' in log:
                Log.error('BUILD FAILED. No need to wait more time!')
                break
            if 'Unable to sync files' in log:
                Log.error('Sync process failed. No need to wait more time!')
                break
            if 'errors were thrown' in log:
                Log.error('Multiple errors were thrown. No need to wait more time!')
                break

        # Mark that part of the log as verified by appending a flag at the end.
        # The second time we read the file we will verify only the text after that flag
        File.append(log_file, verified_flag)

        if all_items_found:
            if not_existing_string_list is None:
                pass
            else:
                for item in not_existing_string_list:
                    assert item not in log, "{0} found! It should not be in logs.\nLog:\n{1}".format(item, log)
        else:
            Log.debug('##### OUTPUT BEGIN #####\n')
            Log.debug(log)
            Log.debug('##### OUTPUT END #####\n')
            assert False, "Output does not contain {0}".format(not_found_list)
