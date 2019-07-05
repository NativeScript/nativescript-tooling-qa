# pylint: disable=invalid-name
import logging
import os
import platform
import sys

from core.enums.env import EnvironmentType
from core.enums.os_type import OSType
from core.utils.device.appium_capabilities import AppiumCapabilities
from core.utils.device.emulator_info import EmulatorInfo
from core.utils.device.simulator_info import SimulatorInfo


def get_os():
    if 'Windows' in platform.platform():
        return OSType.WINDOWS
    if 'Darwin' in platform.platform():
        return OSType.OSX
    return OSType.LINUX


def get_python_version():
    return sys.version_info[0]


def get_env():
    env = os.environ.get('TEST_ENV', 'next')
    if 'next' in env:
        return EnvironmentType.NEXT
    elif 'rc' in env:
        return EnvironmentType.RC
    elif 'pr' in env:
        return EnvironmentType.PR
    else:
        return EnvironmentType.LIVE


def get_project_home():
    home = os.getcwd()
    while not os.path.exists(os.path.join(home, 'requirements.txt')):
        home = os.path.split(home)[0]
    return home


HOST_OS = get_os()
PYTHON_VERSION = get_python_version()
ENV = get_env()

LOG_LEVEL = logging.DEBUG

NS_GIT_ORG = 'NativeScript'

TEST_RUN_HOME = get_project_home()
TEST_SUT_HOME = os.path.join(TEST_RUN_HOME, 'sut')

TEST_OUT_HOME = os.path.join(TEST_RUN_HOME, 'out')
TEST_OUT_LOGS = os.path.join(TEST_OUT_HOME, 'logs')
TEST_OUT_IMAGES = os.path.join(TEST_OUT_HOME, 'images')
TEST_OUT_TEMP = os.path.join(TEST_OUT_HOME, 'temp')

ASSETS_HOME = os.path.join(TEST_RUN_HOME, 'assets')

SSH_CLONE = os.environ.get('SSH_CLONE', False)

BACKUP_FOLDER = os.path.join(TEST_RUN_HOME, "backup_folder")


def resolve_package(name, variable, default=str(ENV)):
    tag = os.environ.get(variable, default)
    # For local packages (tgz files) or NG nightly builds (angular/cli-builds) just return value of the env. variable
    if '.tgz' not in tag and '-builds' not in tag:
        return name + '@' + tag
    else:
        return tag


class Executables(object):
    ns_path = os.path.join(TEST_RUN_HOME, 'node_modules', '.bin', 'tns')
    ng_path = os.path.join(TEST_RUN_HOME, 'node_modules', '.bin', 'ng')
    TNS = ns_path if os.path.isfile(ns_path) else 'tns'
    NG = ng_path if os.path.isfile(ng_path) else 'ng'


# noinspection SpellCheckingInspection
class Packages(object):
    # CLIs
    NS_CLI = resolve_package(name='nativescript', variable='nativescript')
    NS_SCHEMATICS = resolve_package(name='@nativescript/schematics', variable='nativescript_schematics')
    NG_CLI = resolve_package(name='@angular/cli', variable='ng_cli', default='latest')

    # Preview and Playground packages
    PREVIEW_PATH = os.environ.get('preview_folder_path', os.path.join("/tns-dist", "Playground",
                                                                      "ns-play-dev", "debug"))
    PREVIEW_APP_ID = "org.nativescript.preview"
    PLAYGROUND_PATH = os.environ.get('playground_folder_path', os.path.join("/tns-dist", "Playground",
                                                                            "ns-play", "debug"))

    PREVIEW_APP_IOS = os.path.join(PREVIEW_PATH, "nsplaydev.tgz")
    PREVIEW_APP_ANDROID = os.path.join(PREVIEW_PATH, "app-universal-release.apk")
    PLAYGROUND_APP_IOS = os.path.join(PLAYGROUND_PATH, "nsplay.tgz")
    PLAYGROUND_APP_ANDROID = os.path.join(PLAYGROUND_PATH, "app-release.apk")

    # Runtimes
    ANDROID = resolve_package(name='tns-android', variable='android')
    IOS = resolve_package(name='tns-ios', variable='ios')

    # Modules and Plugins
    MODULES = resolve_package(name='tns-core-modules', variable='tns_core_modules')
    ANGULAR = resolve_package(name='nativescript-angular', variable='nativescript_angular')
    WEBPACK = resolve_package(name='nativescript-dev-webpack', variable='nativescript_dev_webpack')
    TYPESCRIPT = resolve_package(name='nativescript-dev-typescript', variable='nativescript_dev_typescript')
    SASS = resolve_package(name='nativescript-dev-sass', variable='nativescript_dev_sass')

    # Templates branch
    TEMPLATES_BRANCH = os.environ.get('templates_branch', 'master')


# noinspection SpellCheckingInspection
class Android(object):
    # Local runtime package
    FRAMEWORK_PATH = os.path.join(TEST_SUT_HOME, 'tns-android.tgz')

    # Signing options
    ANDROID_KEYSTORE_PATH = os.environ.get('ANDROID_KEYSTORE_PATH')
    ANDROID_KEYSTORE_PASS = os.environ.get('ANDROID_KEYSTORE_PASS')
    ANDROID_KEYSTORE_ALIAS = os.environ.get('ANDROID_KEYSTORE_ALIAS')
    ANDROID_KEYSTORE_ALIAS_PASS = os.environ.get('ANDROID_KEYSTORE_ALIAS_PASS')

    # Chrome Dev Tools debug port
    DEBUG_PORT = 40000


class IOS(object):
    # Local runtime package
    FRAMEWORK_PATH = os.path.join(TEST_SUT_HOME, 'tns-ios.tgz')

    # Signing options
    DEVELOPMENT_TEAM = os.environ.get("DEVELOPMENT_TEAM")
    PROVISIONING = os.environ.get("PROVISIONING")
    DISTRIBUTION_PROVISIONING = os.environ.get("DISTRIBUTION_PROVISIONING")

    # Chrome Dev Tools debug port
    DEBUG_PORT = 41000


class Emulators(object):
    EMU_API_19 = EmulatorInfo(avd=os.environ.get('EMU_API_19', 'Emulator-Api19-Default'), os_version=4.4, port='5560',
                              emu_id='emulator-5560')
    EMU_API_23 = EmulatorInfo(avd=os.environ.get('EMU_API_23', 'Emulator-Api23-Default'), os_version=6.0, port='5562',
                              emu_id='emulator-5562')
    EMU_API_24 = EmulatorInfo(avd=os.environ.get('EMU_API_24', 'Emulator-Api24-Default'), os_version=7.0, port='5568',
                              emu_id='emulator-5568')
    EMU_API_26 = EmulatorInfo(avd=os.environ.get('EMU_API_26', 'Emulator-Api26-Google'), os_version=8.0, port='5564',
                              emu_id='emulator-5564')
    EMU_API_28 = EmulatorInfo(avd=os.environ.get('EMU_API_28', 'Emulator-Api28-Google'), os_version=9.0, port='5566',
                              emu_id='emulator-5566')
    EMU_API_29 = EmulatorInfo(avd=os.environ.get('EMU_API_29', 'Emulator-Api29-Google'), os_version=10.0, port='5568',
                              emu_id='emulator-5568')

    DEFAULT = EMU_API_23


class Simulators(object):
    SIM_IOS10 = SimulatorInfo(name=os.environ.get('SIM_IOS10', 'iPhone7_10'), device_type='iPhone 7', sdk=10.0)
    SIM_IOS11 = SimulatorInfo(name=os.environ.get('SIM_IOS11', 'iPhone7_11'), device_type='iPhone 7', sdk=11.2)
    SIM_IOS12 = SimulatorInfo(name=os.environ.get('SIM_IOS12', 'iPhoneXR_12'), device_type='iPhone XR', sdk=12.0)
    SIM_IOS13 = SimulatorInfo(name=os.environ.get('SIM_IOS13', 'iPhoneXR_13'), device_type='iPhone XR', sdk=13.0)
    DEFAULT = SIM_IOS12


class AppName(object):
    DEFAULT = 'TestApp'
    APP_NAME = 'app'
    WITH_DASH = 'tns-app'
    WITH_SPACE = 'Test App'
    WITH_NUMBER = '123'


class AppiumCaps(object):
    SIM_iOS12 = AppiumCapabilities(platform_name='iOS', platform_version='12.0', automation_name='XCUITest')
    EMU_API_23 = AppiumCapabilities(platform_name='Android', platform_version='6.0', automation_name='UIAutomator2')
