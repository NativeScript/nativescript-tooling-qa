# pylint: disable=too-many-branches
import logging
import os
from time import sleep

from core.base_test.test_context import TestContext
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import Folder
from core.utils.process import Process
from core.utils.run import run
from products.nativescript.app import App
from products.nativescript.tns_assert import TnsAssert
from products.nativescript.tns_paths import TnsPaths
from products.nativescript.tns_logs import TnsLogs


class Tns(object):
    @staticmethod
    def exec_command(command, cwd=Settings.TEST_RUN_HOME, platform=Platform.NONE, emulator=False, path=None,
                     device=None, release=False, for_device=False, provision=Settings.IOS.DEV_PROVISION, bundle=False,
                     hmr=False, aot=False, uglify=False, snapshot=False, log_trace=False, justlaunch=False,
                     options=None, wait=True, timeout=600):
        """
        Execute tns command.
        :param command: Tns command.
        :param cwd: Working directory.
        :param platform: Pass `platform <value>` to command.
        :param emulator: If true pass `--emulator` flag.
        :param path: Pass `--path <value>` to command.
        :param device: Pass `--device <value>` to command.
        :param release: If true pass `--release <all signing options>` to command.
        :param for_device: If true pass `--for-device` to command.
        :param provision: Pass `--provision <value>` to command.
        :param bundle: If true pass `--bundle` to command.
        :param hmr: If true pass `--hmr` to command.
        :param aot: If true pass `--env.aot` to command.
        :param uglify: If true pass `--env.uglify` to command.
        :param snapshot: If true pass `--env.snapshot` to command.
        :param log_trace: If not None pass `--log <level>` to command.
        :param justlaunch: If true pass `--justlaunch` to command.
        :param options: Pass additional options as string.
        :param wait: If true it will wait until command is complete.
        :param timeout: Timeout for CLI command (respected only if wait=True).
        :return: ProcessInfo object.
        :rtype: core.utils.process_info.ProcessInfo
        """
        cmd = '{0} {1}'.format(Settings.Executables.TNS, command)
        if platform is not None:
            cmd = cmd + ' ' + str(platform)
        if path is not None:
            cmd = cmd + ' --path ' + path
        if emulator:
            cmd += ' --emulator'
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
        if hmr:
            cmd += ' --hmr'
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
        if options:
            cmd += ' ' + options

        result = run(cmd=cmd, cwd=cwd, wait=wait, log_level=logging.INFO, timeout=timeout)

        # Retry in case of connectivity issues
        if result.output is not None and 'Bad Gateway' in result.output:
            Log.info('"Bad Gateway" issue detected! Will retry the command ...')
            result = run(cmd=cmd, cwd=cwd, wait=wait, log_level=logging.INFO, timeout=timeout)

        return result

    @staticmethod
    def create(app_name=Settings.AppName.DEFAULT, template=None, path=None, app_id=None,
               force=False,
               default=False,
               update=True,
               force_clean=True,
               log_trace=False,
               verify=True,
               app_data=None):
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
        :param app_data: AppInfo object with expected data (used to verify app is created properly).
        """

        # Cleanup app folder
        if force_clean:
            Folder.clean(TnsPaths.get_app_path(app_name=app_name))

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
            # Usually we do not pass path on tns create, which actually equals to cwd.
            # In such cases pass correct path to TnsAssert.created()
            if path is None:
                path = Settings.TEST_RUN_HOME
            TnsAssert.created(app_name=app_name, output=result.output, app_data=app_data, path=path)

        return result

    @staticmethod
    def platform_remove(app_name=Settings.AppName.DEFAULT, platform=Platform.NONE, verify=True,
                        log_trace=False):
        command = 'platform remove ' + str(platform) + ' --path ' + app_name
        result = Tns.exec_command(command=command, log_trace=log_trace)
        if verify:
            # TODO: Implement it!
            pass
        return result

    @staticmethod
    def platform_add(app_name=Settings.AppName.DEFAULT, platform=Platform.NONE, framework_path=None, version=None,
                     verify=True, log_trace=False):
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
            assert result.exit_code == 0, 'Prepare failed with non zero exit code.'
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
              aot=False, uglify=False, snapshot=False, log_trace=False, verify=True, app_data=None):
        result = Tns.exec_command(command='build', path=app_name, platform=platform, release=release,
                                  provision=provision, for_device=for_device, bundle=bundle, aot=aot, uglify=uglify,
                                  snapshot=snapshot, wait=True, log_trace=log_trace)
        if verify:
            assert result.exit_code == 0, 'Build failed with non zero exit code.'
            TnsAssert.build(app_name=app_name, platform=platform, release=False, provision=Settings.IOS.DEV_PROVISION,
                            for_device=False, bundle=False, aot=False, uglify=False, snapshot=False, log_trace=False,
                            output=result.output, app_data=app_data)
        return result

    @staticmethod
    def build_android(app_name, release=False, bundle=False, aot=False, uglify=False, snapshot=False, log_trace=False,
                      verify=True, app_data=None):
        return Tns.build(app_name=app_name, platform=Platform.ANDROID, release=release, bundle=bundle, aot=aot,
                         uglify=uglify, snapshot=snapshot, log_trace=log_trace, verify=verify, app_data=app_data)

    @staticmethod
    def build_ios(app_name, release=False, provision=Settings.IOS.DEV_PROVISION, for_device=False,
                  bundle=False, aot=False, uglify=False, log_trace=False, verify=True, app_data=None):
        return Tns.build(app_name=app_name, platform=Platform.IOS, release=release, for_device=for_device,
                         provision=provision, bundle=bundle, aot=aot, uglify=uglify, log_trace=log_trace, verify=verify,
                         app_data=app_data)

    @staticmethod
    def run(app_name, platform, emulator=False, device=None, release=False, provision=Settings.IOS.DEV_PROVISION,
            for_device=False, bundle=False, hmr=False, aot=False, uglify=False, snapshot=False, wait=False,
            log_trace=False, justlaunch=False, verify=True):
        result = Tns.exec_command(command='run', path=app_name, platform=platform, emulator=emulator, device=device,
                                  release=release, provision=provision, for_device=for_device,
                                  bundle=bundle, hmr=hmr, aot=aot, uglify=uglify, snapshot=snapshot,
                                  wait=wait, log_trace=log_trace, justlaunch=justlaunch)
        if verify:
            if wait:
                assert result.exit_code == 0, 'tns run failed with non zero exit code.'
                assert 'successfully synced' in result.output.lower()
            else:
                sleep(10)
        return result

    @staticmethod
    def run_android(app_name, emulator=False, device=None, release=False, bundle=False, hmr=False, aot=False,
                    uglify=False, snapshot=False, wait=False, log_trace=False, justlaunch=False, verify=True):
        return Tns.run(app_name=app_name, platform=Platform.ANDROID, emulator=emulator, device=device, release=release,
                       bundle=bundle, hmr=hmr, aot=aot, uglify=uglify, snapshot=snapshot,
                       wait=wait, log_trace=log_trace, justlaunch=justlaunch, verify=verify)

    @staticmethod
    def run_ios(app_name, emulator=False, device=None, release=False, provision=Settings.IOS.DEV_PROVISION,
                for_device=False, bundle=False, hmr=False, aot=False, uglify=False, wait=False, log_trace=False,
                justlaunch=False, verify=True):
        return Tns.run(app_name=app_name, platform=Platform.IOS, emulator=emulator, device=device, release=release,
                       provision=provision, for_device=for_device,
                       bundle=bundle, hmr=hmr, aot=aot, uglify=uglify, wait=wait, log_trace=log_trace,
                       justlaunch=justlaunch, verify=verify)

    @staticmethod
    def debug(app_name, platform, emulator=False, device=None, release=False, provision=Settings.IOS.DEV_PROVISION,
              for_device=False, bundle=False, hmr=False, aot=False, uglify=False, snapshot=False, wait=False,
              log_trace=False, verify=True):
        result = Tns.exec_command(command='debug', path=app_name, platform=platform, emulator=emulator, device=device,
                                  release=release, provision=provision, for_device=for_device,
                                  bundle=bundle, hmr=hmr, aot=aot, uglify=uglify, snapshot=snapshot,
                                  wait=wait, log_trace=log_trace)
        if verify:
            pass
        return result

    @staticmethod
    def test_init(app_name, framework, verify=True):
        """
        Execute `tns test init` command.
        :param app_name: App name (passed as --path <App name>)
        :param framework: Unit testing framework as string (jasmin, mocha, quinit).
        :param verify: Verify command was executed successfully.
        :return: Result of `tns test init` command.
        """
        command = 'test init --framework {0}'.format(str(framework))
        result = Tns.exec_command(command=command, path=app_name, timeout=300)
        if verify:
            TnsAssert.test_initialized(app_name=app_name, framework=framework, output=result.output)
        return result

    @staticmethod
    def test(app_name, platform, emulator=True, device=None, justlaunch=True, verify=True):
        """
        Execute `tns test <platform>` command.
        :param app_name: App name (passed as --path <App name>)
        :param platform: PlatformType enum value.
        :param emulator: If true pass `--emulator` to the command.
        :param device: Pass `--device <value>` to command.
        :param justlaunch: If true pass `--justlaunch` to the command.
        :param verify: Verify command was executed successfully.
        :return: Result of `tns test` command.
        """
        cmd = 'test {0}'.format(str(platform))
        result = Tns.exec_command(command=cmd, path=app_name, emulator=emulator, device=device, justlaunch=justlaunch)
        if verify:
            assert 'server started at' in result.output
            assert 'Launching browser' in result.output
            assert 'Starting browser' in result.output
            assert 'Connected on socket' in result.output
            assert 'Executed 1 of 1' in result.output
            assert 'TOTAL: 1 SUCCESS' in result.output \
                   or 'Executed 1 of 1 SUCCESS' or 'Executed 1 of 1[32m SUCCESS' in result.output
        return result

    @staticmethod
    def doctor(app_name=None):
        """
        Execute `tns doctor`
        :param app_name: App where command will be executed (by default None -> common will be executed outside app).
        :return: Result of `tns doctor` command.
        """
        cwd = Settings.TEST_RUN_HOME
        if app_name is not None:
            cwd = os.path.join(cwd, app_name)
        return Tns.exec_command(command='doctor', cwd=cwd, timeout=60)

    @staticmethod
    def info(app_name=None):
        """
        Execute `tns info`
        :param app_name: App where command will be executed (by default None -> common will be executed outside app).
        :return: Result of `tns info` command.
        """
        cwd = Settings.TEST_RUN_HOME
        if app_name is not None:
            cwd = os.path.join(cwd, app_name)
        return Tns.exec_command(command='info', cwd=cwd, timeout=60)

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
        Log.info("Kill tns processes.")
        if Settings.HOST_OS == OSType.WINDOWS:
            Process.kill(proc_name='node')
        else:
            Process.kill(proc_name='node', proc_cmdline=Settings.Executables.TNS)
            Process.kill_by_commandline(cmdline='webpack.js')

    @staticmethod
    def preview(app_name, bundle=False, hmr=False, aot=False, uglify=False, wait=False,
                log_trace=True, verify=True, timeout=60):
        result = Tns.exec_command(command='preview', path=app_name, bundle=bundle, hmr=hmr, aot=aot, uglify=uglify,
                                  wait=wait, log_trace=log_trace, timeout=timeout)
        if verify:
            strings = ['Use NativeScript Playground app and scan the QR code above to preview '\
                        'the application on your device']
            TnsLogs.wait_for_log(result.log_file, strings)

        return result
