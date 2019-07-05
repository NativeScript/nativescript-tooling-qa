import os
import unittest
from core.enums.os_type import OSType
from core.utils.file_utils import Folder, File
from core.utils.device.adb import Adb
from core.utils.run import run
from core.base_test.tns_run_test import TnsRunTest
from core.settings import Settings
from core.settings.Settings import TEST_SUT_HOME, TEST_RUN_HOME, AppName, Android, IOS, HOST_OS
from data.templates import Template
from products.nativescript.tns import Tns


class AndroidAppBundleTests(TnsRunTest):

    app_name = AppName.DEFAULT
    app_path = os.path.join(TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(TEST_RUN_HOME, 'data', 'temp', app_name)
    bundletool_path = os.path.join(TEST_SUT_HOME, "bundletool.jar")
    path_to_apks = os.path.join(app_path, 'app.apks')

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Android.FRAMEWORK_PATH)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.app_path, target=cls.target_project_dir)

        # Download bundletool
        url = 'https://github.com/google/bundletool/releases/download/0.10.0/bundletool-all-0.10.0.jar'
        File.download('bundletool.jar', url, TEST_SUT_HOME)

    def setUp(self):
        TnsRunTest.setUp(self)

        # Ensure app is in initial state
        Folder.clean(self.app_path)
        Folder.copy(source=self.target_project_dir, target=self.app_path)

    @staticmethod
    def bundletool_build(bundletool_path, path_to_aab, path_to_apks):
        build_command = ('java -jar {0} build-apks --bundle="{1}" --output="{2}" --ks="{3}" --ks-pass=pass:"{4}" \
            --ks-key-alias="{5}" --key-pass=pass:"{6}"').format(bundletool_path, path_to_aab, path_to_apks,
                                                                Android.ANDROID_KEYSTORE_PATH,
                                                                Android.ANDROID_KEYSTORE_PASS,
                                                                Android.ANDROID_KEYSTORE_ALIAS,
                                                                Android.ANDROID_KEYSTORE_ALIAS_PASS)
        result = run(build_command)
        assert "Error" not in result.output, "create of .apks file failed"

    @staticmethod
    def bundletool_deploy(bundletool_path, path_to_apks, device_id):
        deploy_command = ('java -jar {0} install-apks --apks="{1}" --device-id={2}').format(bundletool_path,
                                                                                            path_to_apks,
                                                                                            device_id)
        result = run(deploy_command)
        assert "Error" not in result.output, "deploy of app failed"
        assert "The APKs have been extracted in the directory:" in result.output, "deploy of app failed"

    def test_200_build_android_app_bundle(self):
        """Build app with android app bundle option. Verify the output(app.aab) and use bundletool
           to deploy on device"""
        path_to_aab = os.path.join(self.app_name, "platforms", "android", "app", "build", "outputs",
                                   "bundle", "debug", "app.aab")

        Tns.build_android(self.app_path, aab=True, verify=False)
        # There is an issue at the moment that the path is not shown in log.
        # TODO: uncomment this when the issue is fixed
        # assert "The build result is located at:" in result.output
        # assert path_to_aab in result.output
        assert File.exists(path_to_aab)

        # Verify app can be deployed on emulator via bundletool
        # Use bundletool to create the .apks file
        self.bundletool_build(self.bundletool_path, path_to_aab, self.path_to_apks)
        assert File.exists(self.path_to_apks)

        # Deploy on device
        self.bundletool_deploy(self.bundletool_path, self.path_to_apks, device_id=self.emu.id)

        # Start the app on device
        Adb.start_application(self.emu.id, "org.nativescript.TestApp")

        # Verify app looks correct inside emulator
        self.emu.wait_for_text(text='TAP')

    @unittest.skipIf(Settings.HOST_OS == OSType.WINDOWS, "Skip on Windows")
    def test_205_build_android_app_bundle_env_snapshot(self):
        """Build app with android app bundle option with --bundle and optimisations for snapshot.
           Verify the output(app.aab) and use bundletool to deploy on device."""
        # This test will not run on windows because env.snapshot option is not available on that OS

        path_to_aab = os.path.join(self.app_name, "platforms", "android", "app", "build",
                                   "outputs", "bundle", "release", "app.aab")

        # Configure app with snapshot optimisations
        source = os.path.join('assets', 'abdoid-app-bundle', 'app.gradle')
        target = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source, target)

        webpack_config = os.path.join(self.app_name, 'webpack.config.js')
        File.replace(webpack_config, 'webpackConfig: config,', """webpackConfig: config,
        \ntargetArchs: [\"arm\", \"arm64\", \"ia32\"],
        \nuseLibs: true,\nandroidNdkPath: \"$ANDROID_NDK_HOME\"""")

        # env.snapshot is applicable only in release build
        Tns.build_android(self.app_path, aab=True, release=True, snapshot=True,
                          uglify=True, verify=False)
        # There is an issue at the moment that the path is not shown in log.
        # TODO: uncomment this when the issue is fixed
        # assert "The build result is located at:" in result.output
        # assert path_to_aab in result.output
        assert File.exists(path_to_aab)

        # Verify app can be deployed on emulator via bundletool
        # Use bundletool to create the .apks file
        self.bundletool_build(self.bundletool_path, path_to_aab, self.path_to_apks)
        assert File.exists(self.path_to_apks)

        # Verify that the correct .so file is included in the package
        File.unzip(self.path_to_apks, os.path.join(self.app_name, 'apks'))
        File.unzip(os.path.join(self.app_name, 'apks', 'splits', 'base-x86.apk'),
                   os.path.join(self.app_name, 'base_apk'))
        assert File.exists(os.path.join(self.app_name, 'base_apk', 'lib', 'x86', 'libNativeScript.so'))

        # Deploy on device
        self.bundletool_deploy(self.bundletool_path, self.path_to_apks, device_id=self.emu.id)

        # Start the app on device
        Adb.start_application(self.emu.id, "org.nativescript.TestApp")

        # Verify app looks correct inside emulator
        self.emu.wait_for_text(text='TAP')
