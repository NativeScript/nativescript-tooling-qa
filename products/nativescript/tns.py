import logging
import os
import time

from core.base_test.run_context import TestContext
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import Folder, File
from core.utils.process import Run, Process
from products.nativescript.app import App
from products.nativescript.tns_assert import TnsAssert


class Tns(object):
    @staticmethod
    def exec_command(command, cwd=Settings.TEST_RUN_HOME, platform=Platform.NONE, path=None, device=None, release=False,
                     for_device=False, provision=Settings.IOS.DEV_PROVISION, bundle=False, aot=False, uglify=False,
                     snapshot=False, log_trace=False, justlaunch=False, wait=True):
        """
        Execute tns command.
        :param command: Tns command.
        :param cwd: Working directory.
        :param platform: Pass `platform <value>` to command.
        :param path: Pass `--path <value>` to command.
        :param device: Pass `--device <value>` to command.
        :param release: If true pass `--release <all signing options>` to command.
        :param for_device: If true pass `--for-device` to command.
        :param provision: Pass `--provision <value>` to command.
        :param bundle: If true pass `--bundle` to command.
        :param aot: If true pass `--env.aot` to command.
        :param uglify: If true pass `--env.uglify` to command.
        :param snapshot: If true pass `--env.snapshot` to command.
        :param log_trace: If true pass `--log trace` to command.
        :param justlaunch: If true pass `--justlaunch` to command.
        :param wait: If true it will wait until command is complete.
        :return: ProcessInfo object.
        :rtype: core.utils.process_info.ProcessInfo
        """
        cmd = '{0} {1}'.format(Settings.Executables.TNS, command)
        if platform is not None:
            cmd = cmd + ' ' + str(platform)
        if path is not None:
            cmd = cmd + ' --path ' + path
        if device is not None:
            cmd = cmd + ' --device ' + device
        if release:
            cmd += ' --release'
            if platform is Platform.ANDROID:
                cmd += ' --key-store-path {0} --key-store-password {1} --key-store-alias {2} ' \
                       '--key-store-alias-password {3}'.format(Settings.Android.ANDROID_KEYSTORE_PATH,
                                                               Settings.Android.ANDROID_KEYSTORE_PASS,
                                                               Settings.Android.ANDROID_KEYSTORE_ALIAS,
                                                               Settings.Android.ANDROID_KEYSTORE_ALIAS_PASS)
            if platform is Platform.IOS:
                cmd = cmd + ' --provision ' + provision
        if for_device:
            cmd += ' --for-device'
        if bundle:
            cmd += ' --bundle'
        if aot:
            cmd += ' --env.aot'
        if uglify:
            cmd += ' --env.uglify'
        if snapshot:
            cmd += ' --env.snapshot'
        if justlaunch:
            cmd += ' --justlaunch'
        if log_trace:
            cmd += ' --log trace'
        return Run.command(cmd=cmd, cwd=cwd, wait=wait, log_level=logging.INFO)

    @staticmethod
    def create(app_name=Settings.AppName.DEFAULT, template=None, path=None, app_id=None,
               force=False,
               default=False,
               update=True,
               force_clean=True,
               log_trace=False,
               verify=True):
        """
        Create {N} application.
        :param app_name: Application name (TestApp by default).
        :param template: Template string (it can be everything that can be npm installed - npm package, git url ...)
        :param path: Path where app to be created (Passes `--path <value>` to tns command. None by default).
        :param app_id: Application identifier.
        :param force: If true passes '--force' to tns command.
        :param default: If true passes '--default' to tns command.
        :param update: If True update the app (modules and plugins).
        :param force_clean: If True clean app folder before creating a project.
        :param log_trace: If True runs tns command with '--log trace'.
        :param verify: If True assert app is created properly.
        """

        # Cleanup app folder
        if force_clean:
            Folder.clean(os.path.join(Settings.TEST_RUN_HOME, app_name))

        # Create app
        normalized_app_name = app_name
        if ' ' in app_name:
            normalized_app_name = '"' + app_name + '"'
        command = 'create ' + normalized_app_name
        if template is not None:
            command = command + ' --template ' + template
        if path is not None:
            command = command + ' --path ' + path
        if app_id is not None:
            # noinspection SpellCheckingInspection
            command = command + ' --appid ' + app_id
        if force:
            command += ' --force'
        if default:
            command += ' --default'
        result = Tns.exec_command(command, log_trace=log_trace)

        # Update the app (if specified)
        if update:
            App.update(app_name=app_name)

        # Let TestContext know app is created
        TestContext.TEST_APP_NAME = app_name

        # Verify app is created properly
        if verify is not False:
            TnsAssert.created(app_name=app_name, output=result.output)

        return result

    @staticmethod
    def platform_add(app_name=Settings.AppName.DEFAULT, platform=Platform.NONE, framework_path=None, version=None,
                     verify=True,
                     log_trace=False):
        platform_add_string = str(platform)
        if version is not None:
            platform_add_string = platform_add_string + '@' + version
        command = 'platform add ' + platform_add_string + ' --path ' + app_name
        if framework_path is not None:
            command = command + ' --frameworkPath ' + framework_path
        result = Tns.exec_command(command=command, log_trace=log_trace)
        if verify:
            TnsAssert.platform_added(app_name=app_name, platform=platform, output=result.output)
        return result

    @staticmethod
    def platform_add_android(app_name=Settings.AppName.DEFAULT, framework_path=None, version=None, verify=True,
                             log_trace=False):
        return Tns.platform_add(app_name=app_name, platform=Platform.ANDROID, framework_path=framework_path,
                                version=version, verify=verify, log_trace=log_trace)

    @staticmethod
    def platform_add_ios(app_name=Settings.AppName.DEFAULT, framework_path=None, version=None, verify=True,
                         log_trace=False):
        return Tns.platform_add(app_name=app_name, platform=Platform.IOS, framework_path=framework_path,
                                version=version, verify=verify, log_trace=log_trace)

    @staticmethod
    def prepare(app_name, platform, release=False, for_device=False, bundle=False, log_trace=False, verify=True):
        result = Tns.exec_command(command='prepare', path=app_name, platform=platform, release=release,
                                  for_device=for_device, bundle=bundle, wait=True, log_trace=log_trace)
        if verify:
            assert result.exit_code is 0, 'Prepare failed with non zero exit code.'
        return result

    @staticmethod
    def prepare_android(app_name, release=False, log_trace=False, verify=True):
        return Tns.prepare(app_name=app_name, platform=Platform.ANDROID, release=release, log_trace=log_trace,
                           verify=verify)

    @staticmethod
    def prepare_ios(app_name, release=False, for_device=False, log_trace=False, verify=True):
        return Tns.prepare(app_name=app_name, platform=Platform.IOS, release=release, for_device=for_device,
                           log_trace=log_trace, verify=verify)

    @staticmethod
    def build(app_name, platform, release=False, provision=Settings.IOS.DEV_PROVISION, for_device=False, bundle=False,
              aot=False, uglify=False, snapshot=False, log_trace=False, verify=True):
        result = Tns.exec_command(command='build', path=app_name, platform=platform, release=release,
                                  provision=provision, for_device=for_device, bundle=bundle, aot=aot, uglify=uglify,
                                  snapshot=snapshot, wait=True, log_trace=log_trace)
        if verify:
            assert result.exit_code is 0, 'Build failed with non zero exit code.'
            assert 'Project successfully built.' in result.output
        return result

    @staticmethod
    def build_android(app_name, release=False, bundle=False, aot=False, uglify=False, snapshot=False, log_trace=False,
                      verify=True):
        return Tns.build(app_name=app_name, platform=Platform.ANDROID, release=release,
                         bundle=bundle, aot=aot, uglify=uglify, snapshot=snapshot, log_trace=log_trace, verify=verify)

    @staticmethod
    def build_ios(app_name, release=False, provision=Settings.IOS.DEV_PROVISION, for_device=False,
                  bundle=False, aot=False, uglify=False, log_trace=False, verify=True):
        return Tns.build(app_name=app_name, platform=Platform.IOS, release=release, for_device=for_device,
                         provision=provision, bundle=bundle, aot=aot, uglify=uglify, log_trace=log_trace, verify=verify)

    @staticmethod
    def run(app_name, platform, device=None, release=False, provision=Settings.IOS.DEV_PROVISION, for_device=False,
            bundle=False, aot=False, uglify=False, snapshot=False, wait=False, log_trace=False, justlaunch=False,
            verify=True):
        result = Tns.exec_command(command='run', path=app_name, platform=platform, device=device, release=release,
                                  provision=provision, for_device=for_device, bundle=bundle, aot=aot, uglify=uglify,
                                  snapshot=snapshot, wait=wait, log_trace=log_trace, justlaunch=justlaunch)
        if verify:
            if wait:
                assert result.exit_code is 0, 'tns run failed with non zero exit code.'
                assert 'successfully synced' in result.output.lower()
            else:
                end_time = time.time() + 500
                complete = False
                log = ''
                while time.time() < end_time:
                    log = File.read(result.log_file)
                    install_complete = 'Successfully installed' in log
                    sync_complete = 'Successfully synced application' in log
                    android_native_build_failed = 'BUILD FAILED' in log
                    sync_failed = 'Unable to apply changes' in log
                    if install_complete or sync_complete:
                        complete = True
                        break
                    elif android_native_build_failed or sync_failed:
                        complete = False
                        break
                    else:
                        time.sleep(1)
                assert complete, 'Tns run failed!' + os.linesep + 'LOG:' + os.linesep + log
        return result

    @staticmethod
    def run_android(app_name, device=None, release=False, bundle=False, aot=False, uglify=False, snapshot=False,
                    wait=False, log_trace=False, justlaunch=False, verify=True):
        return Tns.run(app_name=app_name, platform=Platform.ANDROID, device=device, release=release,
                       bundle=bundle, aot=aot, uglify=uglify, snapshot=snapshot,
                       wait=wait, log_trace=log_trace, justlaunch=justlaunch, verify=verify)

    @staticmethod
    def run_ios(app_name, device=None, release=False, provision=Settings.IOS.DEV_PROVISION, for_device=False,
                bundle=False, aot=False, uglify=False, wait=False, log_trace=False, justlaunch=False, verify=True):
        return Tns.run(app_name=app_name, platform=Platform.IOS, device=device, release=release, provision=provision,
                       for_device=for_device, bundle=bundle, aot=aot, uglify=uglify, wait=wait, log_trace=log_trace,
                       justlaunch=justlaunch, verify=verify)

    @staticmethod
    def debug(app_name, platform, device=None, release=False, provision=Settings.IOS.DEV_PROVISION, for_device=False,
              bundle=False,
              aot=False, uglify=False, snapshot=False, wait=False,
              log_trace=False, verify=True):
        result = Tns.exec_command(command='debug', path=app_name, platform=platform, device=device, release=release,
                                  provision=provision, for_device=for_device, bundle=bundle, aot=aot, uglify=uglify,
                                  snapshot=snapshot, wait=wait, log_trace=log_trace)
        if verify:
            pass
        return result

    @staticmethod
    def doctor(app_name=None):
        """
        Execute `tns doctor`
        :param app_name: App where command will be executed (by default None -> doctor will be executed outside app).
        :return: Result of `tns doctor` command.
        """
        cwd = Settings.TEST_RUN_HOME
        if app_name is not None:
            cwd = os.path.join(cwd, app_name)
        return Tns.exec_command(command='doctor', cwd=cwd)

    @staticmethod
    def version():
        """
        Get version of CLI
        :return: Version of the CLI as string
        """
        return Tns.exec_command(command='--version').output.split(os.linesep)[-1]

    @staticmethod
    def kill():
        """
        Kill all tns related processes.
        """
        if Settings.HOST_OS == OSType.WINDOWS:
            Process.kill(proc_name='node')
        else:
            Process.kill_by_commandline(cmdline=Settings.Executables.TNS)
            Process.kill_by_commandline(cmdline='webpack.js')
