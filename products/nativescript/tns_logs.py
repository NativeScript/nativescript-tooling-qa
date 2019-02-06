# pylint: disable=unused-argument
import time

from core.enums.platform_type import Platform
from core.log.log import Log
from core.utils.file_utils import File
from products.nativescript.run_type import RunType


# noinspection PyUnusedLocal
class TnsLogs(object):
    SKIP_NODE_MODULES = ['Skipping node_modules folder!', 'Use the syncAllFiles option to sync files from this folder.']

    @staticmethod
    def prepare_messages(platform, plugins=None):
        """
        Get log messages that should be present when project is prepared (except the case when prepare is skipped!).
        :param platform: Platform.ANDROID or Platform.IOS
        :param plugins: Array of strings: ['nativescript-theme-core', 'tns-core-modules', 'tns-core-modules-widgets']
        :return: Array of strings.
        """
        if plugins is None:
            plugins = []
        logs = ['Preparing project...']
        if platform == Platform.ANDROID:
            logs.append('Project successfully prepared (Android)')
        if platform == Platform.IOS:
            logs.append('Project successfully prepared (iOS)')
        for plugin in plugins:
            logs.append('Successfully prepared plugin {0} for {1}'.format(plugin, str(platform)))
        return logs

    @staticmethod
    def build_messages(platform, run_type=RunType.FULL, plugins=None):
        """
        Get log messages that should be present when project is build.
        :param platform: Platform.ANDROID or Platform.IOS
        :param run_type: RunType enum value.
        :param plugins: Array of plugins available in the project.
        :return: Array of strings.
        """
        if plugins is None:
            plugins = []

        logs = ['Building project...', 'Project successfully built.']
        return logs

    @staticmethod
    def webpack_messages(platform, plugins=None):
        """
        Get log messages that should be present when project is build.
        :param platform: Platform.ANDROID or Platform.IOS
        :param plugins: Array of plugins available in the project.
        :return: Array of strings.
        """
        if plugins is None:
            plugins = []

        logs = ['Webpack compilation complete.', 'Watching for file changes.', 'Webpack build done!']
        return logs

    @staticmethod
    def run_messages(app_name, platform, run_type=RunType.FULL, bundle=False, hmr=False, uglify=False, file_name=None, plugins=None):
        """
        Get log messages that should be present when running a project.
        :param app_name: Name of the app (for example TestApp).
        :param platform: Platform.ANDROID or Platform.IOS.
        :param run_type: RunType enum value.
        :param bundle: True if `--bundle is specified.`
        :param hmr: True if `--hmr is specified.`
        :param file_name: Name of changed file.
        :param plugins: List of plugins.
        :return: Array of strings.
        """
        if plugins is None:
            plugins = []
        logs = []

        if file_name is None:
            if bundle is True or hmr is True:
                logs.append('File change detected.')
                logs.append('Starting incremental webpack compilation...')
                webpack_logs = TnsLogs.webpack_messages(platform=platform, plugins=[])
                logs.extend(webpack_logs)

                prepare_logs = TnsLogs.prepare_messages(platform=platform, plugins=[])
                logs.extend(prepare_logs)

                build_logs = TnsLogs.build_messages(platform=platform, plugins=[])
                logs.extend(build_logs)

                logs.append('Installing on device')
                logs.append('Successfully installed on device with identifier')
                logs.append('Restarting application on device')

                if platform == Platform.IOS:
                    logs.append('Successfully transferred bundle.js on device')
                    logs.append('Successfully transferred package.json on device')
                    logs.append('Successfully transferred starter.js on device')
                    logs.append('Successfully transferred vendor.js on device')
            else:
                logs.append('Installing on device')
                logs.append('Successfully installed on device with identifier')
                logs.append('Restarting application on device')
                if platform ==Platform.IOS:
                    logs.append('Successfully transferred all files on device')

                # TODO
                prepare_logs = TnsLogs.prepare_messages(platform=platform, plugins=['nativescript-theme-core',
                                                                                'tns-core-modules',
                                                                                'tns-core-modules-widgets'])
                logs.extend(prepare_logs)

                build_logs = TnsLogs.build_messages(platform=platform, plugins=[])
                logs.extend(build_logs)

            if hmr is True:
                logs.append('HMR: Hot Module Replacement Enabled.')
                logs.append('Waiting for signal.')



        # Add messages when file is changes (prepare and sync files).
        if file_name is not None:
            if hmr is False:
                if '.js' in file_name or '.ts' in file_name or bundle is True:
                    restart = True
                    prepare_logs = TnsLogs.prepare_messages(platform=platform, plugins=[])
                    logs.extend(prepare_logs)
                    if bundle is False:
                        logs.append('Successfully transferred ' + file_name + ' on device'.replace('.ts', '.js'))
                    if bundle is True:
                        logs.append('Successfully transferred bundle.js on device')
                        if uglify is True:
                            logs.append('Successfully transferred vendor.js on device')
                    logs.append('Restarting application on device')
                    if platform == Platform.ANDROID:
                        logs.append('ActivityManager: Start proc')
                        logs.append('activity org.nativescript.TestApp/com.tns.NativeScriptActivity')
                elif '.js' or '.ts' not in file_name or bundle is False:
                    logs.append('Refreshing application on device')
                    logs.append('Successfully transferred ' + file_name + ' on device')
            if hmr is True:
                logs.append('File change detected.')
                logs.append('Starting incremental webpack compilation...')
                webpack_logs = TnsLogs.webpack_messages(platform=platform, plugins=[])
                logs.extend(webpack_logs)
                logs.append('hot-update.json on device')
                logs.append('The following modules were updated:')
                logs.append('Successfully applied update with hmr hash')
                logs.append('Refreshing application on device')

            # Generate build messages
            # TODO: Check if file is in app resources and require native build
            should_build_native = False
            if should_build_native:
                build_logs = TnsLogs.build_messages(platform=platform, run_type=run_type)
                logs.extend(build_logs)

        # Add message for successful sync
        logs.append('Successfully synced application org.nativescript.{0} on device'.format(app_name))

        # Return logs
        return logs

    @staticmethod
    def wait_for_log(log_file, string_list, not_existing_string_list=None, timeout=45, check_interval=1):
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
            if not not_found_list:
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
