# pylint: disable=unused-argument
import time

from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from products.nativescript.run_type import RunType
from products.nativescript.tns_paths import TnsPaths


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
        logs = []
        if run_type in [RunType.FIRST_TIME, RunType.FULL]:
            logs = ['Building project...', 'Project successfully built.']
            if platform == Platform.ANDROID:
                logs.append('Gradle build...')
            if platform == Platform.IOS:
                logs.append('Xcode build...')
        return logs

    @staticmethod
    def run_messages(app_name, platform, run_type=RunType.FULL, bundle=False, hmr=False, uglify=False,
                     file_name=None, instrumented=False, sync_all_file=False, plugins=None):
        """
        Get log messages that should be present when running a project.
        :param app_name: Name of the app (for example TestApp).
        :param platform: Platform.ANDROID or Platform.IOS.
        :param run_type: RunType enum value.
        :param bundle: True if `--bundle is specified.`
        :param hmr: True if `--hmr is specified.`
        :param uglify: True if `--env.uglify is specified.`
        :param file_name: Name of changed file.
        :param instrumented: If true it will return logs we place inside app (see files in assets/logs).
        :param sync_all_file: If false will check for logs that syncAllFiles is skipped.
        :param plugins: List of plugins.
        :return: Array of strings.
        """
        if plugins is None:
            plugins = []
        logs = []
        if hmr:
            bundle = True

        # Generate prepare messages
        if run_type in [RunType.FIRST_TIME, RunType.FULL]:
            logs.extend(TnsLogs.prepare_messages(platform=platform, plugins=plugins))

        # Generate build messages
        # TODO: Check if file is in app resources and require native build
        logs.extend(TnsLogs.build_messages(platform=platform, run_type=run_type))

        # App install messages
        if run_type in [RunType.FIRST_TIME, RunType.FULL]:
            logs.append('Installing on device')
            logs.append('Successfully installed')

        # File transfer messages
        logs.extend(TnsLogs.__file_changed_messages(run_type=run_type, file_name=file_name, platform=platform,
                                                    bundle=bundle, hmr=hmr, uglify=uglify))

        # App restart messages:
        if TnsLogs.__should_restart(run_type=run_type, bundle=bundle, hmr=hmr, file_name=file_name):
            logs.extend(TnsLogs.__app_restart_messages(app_name=app_name, platform=platform, instrumented=instrumented))
        else:
            logs.extend(TnsLogs.__app_refresh_messages(instrumented=instrumented))

        # Add message for successful sync
        logs.append('Successfully synced application org.nativescript.{0} on device'.format(app_name))

        # Return logs
        return logs

    @staticmethod
    def __file_changed_messages(run_type, file_name, platform, bundle, hmr, uglify):
        logs = []
        if file_name is None:
            if run_type not in [RunType.FIRST_TIME, RunType.FULL]:
                logs.append('Skipping prepare.')
        else:
            if not hmr:
                logs.extend(TnsLogs.prepare_messages(platform=platform, plugins=None))
            if bundle:
                logs.append('File change detected.')
                logs.append('Starting incremental webpack compilation...')
                logs.append(file_name)
                logs.append('Webpack compilation complete.')
                logs.append('Webpack build done!')
                if hmr:
                    logs.append('Successfully transferred bundle.')
                    logs.append('hot-update.json')
                    logs.append('HMR: Checking for updates to the bundle with hmr hash')
                    logs.append('HMR: The following modules were updated:')
                    logs.append('HMR: Successfully applied update with hmr hash')
                else:
                    logs.append('Successfully transferred bundle.js')
                    if uglify:
                        logs.append('Successfully transferred vendor.js')
            else:
                # If bundle is not used then TS files are transpiled and synced as JS
                logs.append('Successfully transferred {0}'.format(file_name.replace('.ts', '.js')))
        return logs

    @staticmethod
    def __should_restart(run_type, bundle, hmr, file_name):
        should_restart = True
        if hmr:
            should_restart = False
        else:
            if bundle:
                should_restart = True
            else:
                if file_name is not None:
                    if '.css' in file_name or '.xml' in file_name or '.html' in file_name:
                        should_restart = False

        # ...and at the end: App restarts always on first run
        if run_type in [RunType.FIRST_TIME, RunType.FULL]:
            should_restart = True

        return should_restart

    @staticmethod
    def __app_restart_messages(app_name, platform, instrumented):
        logs = ['Restarting application on device']
        if platform == Platform.ANDROID:
            app_id = TnsPaths.get_bundle_if(app_name)
            logs.append('ActivityManager: Start proc')
            logs.append('activity org.nativescript.{0}/com.tns.NativeScriptActivity'.format(app_id))
        if instrumented:
            logs.append('QA: Application started')
        return logs

    @staticmethod
    def __app_refresh_messages(instrumented):
        return ['Refreshing application on device']

    @staticmethod
    def wait_for_log(log_file, string_list, not_existing_string_list=None, timeout=60, check_interval=3):
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
                    string_list.remove(item)
                else:
                    not_found_list.append(item)
            if not not_found_list:
                all_items_found = True
                Log.info("Log contains: {0}".format(string_list))
                break
            else:
                Log.debug("'{0}' NOT found. Wait...".format(not_found_list))
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
        if Settings.HOST_OS != OSType.WINDOWS:
            File.append(log_file, verified_flag)

        if all_items_found:
            if not_existing_string_list is None:
                pass
            else:
                for item in not_existing_string_list:
                    assert item not in log, "{0} found! It should not be in logs.\nLog:\n{1}".format(item, log)
        else:
            Log.info("NOT FOUND: {0}".format(not_found_list))
            Log.info('##### ACTUAL LOG #####\n')
            Log.info(log)
            Log.info('######################\n')
            assert False, "Output does not contain {0}".format(not_found_list)
