import time

from core.enums.app_type import AppType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from products.nativescript.run_type import RunType
from products.nativescript.tns_paths import TnsPaths


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
            logs.append('Project successfully prepared (android)')
        if platform == Platform.IOS:
            logs.append('Project successfully prepared (ios)')
        for plugin in plugins:
            logs.append('Successfully prepared plugin {0} for {1}'.format(plugin, str(platform)))
        return logs

    @staticmethod
    def build_messages(platform, run_type=RunType.FULL):
        """
        Get log messages that should be present when project is build.
        :param platform: Platform.ANDROID or Platform.IOS
        :param run_type: RunType enum value.
        :return: Array of strings.
        """
        logs = []
        if run_type in [RunType.FIRST_TIME, RunType.FULL]:
            logs = ['Building project...', 'Project successfully built.']
            if platform == Platform.ANDROID:
                logs.append('Gradle build...')
            if platform == Platform.IOS:
                logs.append('Xcode build...')
        return logs

    @staticmethod
    def run_messages(app_name, platform, run_type=RunType.FULL, bundle=True, hmr=True, uglify=False, app_type=None,
                     file_name=None, instrumented=False, plugins=None, aot=False, device=None, just_launch=False,
                     transfer_all=False, release=False, snapshot=False):
        """
        Get log messages that should be present when running a project.
        :param app_name: Name of the app (for example TestApp).
        :param platform: Platform.ANDROID or Platform.IOS.
        :param run_type: RunType enum value (None when it can not be defined strictly).
        :param bundle: True if `--bundle is specified.`
        :param hmr: True if `--hmr is specified.`
        :param uglify: True if `--env.uglify is specified.`
        :param app_type: AppType enum value.
        :param file_name: Name of changed file.
        :param instrumented: If true it will return logs we place inside app (see files in assets/logs).
        :param plugins: List of plugins.
        :param aot: True if `--env.aot is specified.`
        :param device: Device object.
        :param transfer_all: different strings for transfer of files depends on their count - 10 or more
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
                                                    bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, app_type=app_type,
                                                    transfer_all=transfer_all))

        if run_type == RunType.JUST_LAUNCH:
            logs.append('Preparing project...')
            logs.append('Webpack compilation complete.')
            logs.append('Project successfully prepared')
            logs.append('Restarting application on device')

        # App restart messages:
        if run_type in [RunType.UNKNOWN, RunType.JUST_LAUNCH]:
            Log.info('Can not define if app should be restarted or not.')
        else:
            if TnsLogs.__should_restart(run_type=run_type, bundle=bundle, hmr=hmr, file_name=file_name):
                logs.extend(TnsLogs.__app_restart_messages(app_name=app_name, platform=platform,
                                                           instrumented=instrumented, app_type=app_type,
                                                           device=device, just_launch=just_launch))
            else:
                logs.extend(TnsLogs.__app_refresh_messages(instrumented=instrumented, app_type=app_type,
                                                           file_name=file_name, hmr=hmr))

        # Add message for successful sync
        if not release:
            app_id = TnsPaths.get_bundle_id(app_name)
            logs.append('Successfully synced application {0} on device'.format(app_id))

        if app_type == AppType.NG and not release:
            logs.append('Angular is running in the development mode. Call enableProdMode() to enable '
                        'the production mode.')
            # If you are in NG with hmr project changes of app.css should not cause angular reload
            if file_name is not None:
                if hmr and 'app.css' in file_name:
                    logs.remove('Angular is running in the development mode. Call enableProdMode() to enable '
                                'the production mode.')

        # Add message for snapshot
        if snapshot and release:
            logs.append('Successfully generated snapshots')
            logs.append('Snapshot enabled')

        # Return logs
        return logs

    @staticmethod
    def __file_changed_messages(run_type, file_name, platform, bundle, hmr, uglify, aot=False, app_type=None,
                                transfer_all=False):
        logs = []
        if file_name is None:
            if run_type not in [RunType.FIRST_TIME, RunType.FULL, RunType.UNKNOWN, RunType.JUST_LAUNCH]:
                # logs.append('Skipping prepare.')
                logs.append('Starting incremental webpack compilation...')
        else:
            if not hmr:
                # logs.extend(TnsLogs.prepare_messages(platform=platform, plugins=None))
                logs.append('Webpack compilation complete.')
                logs.append('Webpack build done!')
                logs.append('File change detected. Starting incremental webpack compilation...')
                logs.append('Restarting application on device')
                logs.append('Successfully synced application')
            if bundle:
                logs.append('File change detected.')
                logs.append('Starting incremental webpack compilation...')
                if app_type != AppType.VUE:
                    logs.append(file_name)
                # When env.aot html files are processed differently and you wont see
                # the exact file name in the log
                if aot:
                    if file_name is not None:
                        if '.html' in file_name:
                            logs.remove(file_name)
                logs.append('Webpack compilation complete.')
                logs.append('Webpack build done!')
                if hmr:
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

        # Migrated
        if run_type in [RunType.FIRST_TIME, RunType.FULL]:
            if platform == Platform.IOS:
                if bundle or hmr:
                    if transfer_all is True:
                        logs.append('Successfully transferred all files on device')
                    else:
                        logs.append('Successfully transferred bundle.js on device')
                        logs.append('Successfully transferred package.json on device')
                        logs.append('Successfully transferred vendor.js on device')
                else:
                    logs.append('Successfully transferred all files on device')

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
    def __app_restart_messages(app_name, platform, instrumented, app_type, device, just_launch=False):
        logs = ['Restarting application on device']
        if platform == Platform.ANDROID:
            app_id = TnsPaths.get_bundle_id(app_name)
            if device is not None and device.version < 7.0 and just_launch is False:
                logs.append('ActivityManager: Start proc')
                logs.append('activity {0}/com.tns.NativeScriptActivity'.format(app_id))
        if instrumented:
            logs.append('QA: Application started')
            if app_type == AppType.NG:
                logs.append('QA: items component on init')
        return logs

    @staticmethod
    def __app_refresh_messages(instrumented, app_type, hmr=False, file_name=None):
        logs = ['Refreshing application on device']
        if instrumented:
            if app_type == AppType.NG:
                logs.append('QA: items component on init')
                # If you are in NG with hmr project changes of app.css should not cause angular reload
                if file_name is not None:
                    if hmr and 'app.css' in file_name:
                        logs.remove('QA: items component on init')

        return logs

    @staticmethod
    def __webpack_messages():
        return ['File change detected.',
                'Starting incremental webpack compilation...',
                'Webpack compilation complete.',
                'Webpack build done!']

    @staticmethod
    def preview_initial_messages(platform, device, bundle=True, hmr=False, instrumented=False):
        logs = ['Start sending initial files for platform {0}'.format(str(device.model)),
                'Successfully sent initial files for platform {0}'.format(str(device.model))]
        if bundle or hmr:
            logs.extend(TnsLogs.__webpack_messages())
        if instrumented:
            logs.append('QA: Application started')
        return logs

    @staticmethod
    def preview_file_changed_messages(platform, device, file_name, run_type=RunType.INCREMENTAL,
                                      bundle=True, hmr=True, instrumented=False):
        logs = ['Start syncing changes for platform {0}'.format(str(platform))]
        if bundle or hmr:
            logs.extend(TnsLogs.__webpack_messages())
            logs.append(file_name)
        else:
            logs.append('Successfully synced')
            logs.append('{0} for platform {1}'.format(file_name.replace('.ts', '.js'), str(platform)))
        if hmr:
            logs.append('hot-update.json')
            logs.append('HMR: Checking for updates to the bundle with hmr hash')
            logs.append('HMR: The following modules were updated:')
            logs.append('HMR: Successfully applied update with hmr hash')
        if instrumented:
            if TnsLogs.__should_restart(run_type=run_type, bundle=bundle, hmr=hmr, file_name=file_name):
                logs.append('QA: Application started')
        return logs

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
                else:
                    not_found_list.append(item)
            string_list = not_found_list
            if not not_found_list:
                all_items_found = True
                Log.info("All items found")
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
