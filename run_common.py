import os

from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File, Folder
from core.utils.git import Git
from core.utils.gradle import Gradle
from core.utils.npm import Npm
from data.templates import Template
from products.nativescript.tns import Tns


def __cleanup():
    """
    Wipe TEST_OUT_HOME.
    """
    DeviceManager.Emulator.stop()
    if Settings.HOST_OS == OSType.OSX:
        DeviceManager.Simulator.stop()

    Tns.kill()
    Gradle.kill()
    Gradle.cache_clean()
    Folder.clean(os.path.join(Settings.TEST_RUN_HOME, 'node_modules'))
    Folder.clean(Settings.TEST_OUT_HOME)
    Folder.create(Settings.TEST_OUT_LOGS)
    Folder.create(Settings.TEST_OUT_IMAGES)


def __get_templates():
    """
    Clone hello-world templates and pack them as local npm packages.
    Hints: Creating project from local npm package is much faster than from GitHub repo.
    """
    apps = [Template.HELLO_WORLD_JS, Template.HELLO_WORLD_TS, Template.HELLO_WORLD_NG]
    for app in apps:
        template_name = app.repo.split('/')[-1]
        local_folder = os.path.join(Settings.TEST_SUT_HOME, template_name)
        out_file = os.path.join(Settings.TEST_SUT_HOME, template_name + '.tgz')
        Git.clone(repo_url=app.repo, local_folder=local_folder)
        Npm.pack(folder=local_folder, output_file=out_file)
        if File.exists(out_file):
            app.path = out_file
        else:
            raise IOError("Failed to clone and pack template: " + app.repo)


# noinspection SpellCheckingInspection
def __get_packages():
    """
    Get NativeScript CLI and runtimes in TEST_SUT_HOME.
    """

    # Copy or install NativeScript CLI
    if '.tgz' in Settings.Packages.NS_CLI:
        cli_package = os.path.join(Settings.TEST_SUT_HOME, 'nativescript.tgz')
        File.copy(src=Settings.Packages.NS_CLI, target=cli_package)
        Settings.Packages.NS_CLI = cli_package
    else:
        Npm.install(package=Settings.Packages.NS_CLI, folder=Settings.TEST_RUN_HOME)

    # Copy or download tns-android
    android_package = os.path.join(Settings.TEST_SUT_HOME, 'tns-android.tgz')
    if '.tgz' in Settings.Packages.ANDROID:
        File.copy(src=Settings.Packages.ANDROID, target=android_package)
        Settings.Packages.ANDROID = android_package
    else:
        Npm.download(package=Settings.Packages.ANDROID, output_file=android_package)

    # Copy or download tns-ios
    ios_package = os.path.join(Settings.TEST_SUT_HOME, 'tns-ios.tgz')
    if '.tgz' in Settings.Packages.IOS:
        File.copy(src=Settings.Packages.IOS, target=ios_package)
        Settings.Packages.IOS = ios_package
    else:
        Npm.download(package=Settings.Packages.IOS, output_file=ios_package)


def __install_ns_cli():
    """
    Install NativeScript CLI locally.
    """

    output = Npm.install(package=Settings.Packages.NS_CLI, folder=Settings.TEST_RUN_HOME)

    # Verify executable exists after install
    path = os.path.join(Settings.TEST_RUN_HOME, 'node_modules', '.bin', 'tns')
    assert File.exists(path), 'NativeScript executable not found at ' + path
    Settings.Executables.TNS = path

    # Verify installation output
    # noinspection SpellCheckingInspection
    assert 'postinstall.js' in output, 'Post install scripts not executed.'
    assert 'dev-post-install' not in output, 'Dev post install executed on installation.'
    assert 'Installation successful.' in output, 'No success message.'
    assert 'Connect with us on http://twitter.com/NativeScript' in output, 'No connect on twitter message.'
    assert 'tns create <app name>' in output, 'No help for create new project.'
    assert 'tns build <platform>' in output, 'No help for building app.'
    assert 'https://docs.nativescript.org/start/quick-setup' in output, 'No link to quick setup.'
    assert 'tns cloud build' in output, 'No help for cloud builds.'
    assert 'https://play.nativescript.org' in output, 'No link to {N} Playground.'
    assert 'https://stackoverflow.com/questions/tagged/nativescript' in output, 'No Stackoverflow link.'
    assert 'https://nativescriptcommunity.slack.com' in output, 'No link to community Slack.'


def __install_ng_cli():
    """
    Install Angular CLI locally.
    """
    Npm.install(package=Settings.Packages.NG_CLI, folder=Settings.TEST_RUN_HOME)

    # Verify executable exists after install
    path = os.path.join(Settings.TEST_RUN_HOME, 'node_modules', '.bin', 'ng')
    assert File.exists(path), 'Angular CLI executable not found at ' + path
    Settings.Executables.NG = path


def __install_schematics():
    """
    Install NativeScript Schematics locally.
    """
    Npm.install(package=Settings.Packages.NS_SCHEMATICS, folder=Settings.TEST_RUN_HOME)


def prepare(shared=False):
    Log.info('================== Prepare Test Run ==================')
    __cleanup()
    __get_packages()
    __install_ns_cli()
    if shared:
        __install_ng_cli()
        __install_schematics()
    else:
        __get_templates()

    Log.settings()
