import os

from core.base_test.tns_run_android_test import TnsRunAndroidTest
from core.settings.Settings import TEST_SUT_HOME, TEST_RUN_HOME, AppName, Android
from core.utils.device.adb import Adb
from core.utils.file_utils import Folder, File
from core.utils.run import run
from core.utils.docker import Docker
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


class AndroidAppBundleTests(TnsRunAndroidTest):
    app_name = AppName.DEFAULT
    app_path = os.path.join(TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(TEST_RUN_HOME, 'data', 'temp', app_name)
    bundletool_path = os.path.join(TEST_SUT_HOME, "bundletool.jar")
    path_to_apks = os.path.join(app_path, 'app.apks')

    @classmethod
    def setUpClass(cls):
        TnsRunAndroidTest.setUpClass()
        Docker.start()

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Android.FRAMEWORK_PATH)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.app_path, target=cls.target_project_dir)

        # Download bundletool
        url = 'https://github.com/google/bundletool/releases/download/0.10.0/bundletool-all-0.10.0.jar'
        File.download('bundletool.jar', url, TEST_SUT_HOME)

    def setUp(self):
        TnsRunAndroidTest.setUp(self)

        # Ensure app is in initial state
        Folder.clean(self.app_path)
        Folder.copy(source=self.target_project_dir, target=self.app_path)

    @classmethod
    def tearDownClass(cls):
        TnsRunAndroidTest.tearDownClass()
        Docker.stop()

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

    def test_100_run_android_app_bundle_compile_snapshot(self):
        """Run app on android with --aab option with optimisations for snapshot.
           Verify the output(app.aab)."""

        path_to_aab = os.path.join(self.app_name, "platforms", "android", "app", "build",
                                   "outputs", "bundle", "release", "app-release.aab")
        path_to_apks = os.path.join(self.app_name, "platforms", "android", "app", "build",
                                   "outputs", "bundle", "release", "app-release.apks")

        # env.snapshot is applicable only in release build
        result = Tns.run_android(self.app_path, aab=True, release=True, snapshot=True,
                                   uglify=True, verify=False, compileSnapshot=True)
        strings = ['Successfully generated snapshots',
                   'The build result is located at: {0}'.format(path_to_aab)]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=180)
       
        # Verify app can be deployed on emulator via nativescript
        # Verify app looks correct inside emulator
        self.emu.wait_for_text(text='TAP')

        # Verify that the correct .so file is included in the package
        File.unzip(path_to_apks, os.path.join(self.app_name, 'apks'))
        File.unzip(os.path.join(self.app_name, 'apks', 'standalones', 'standalone-arm64_v8a_hdpi.apk'),
                   os.path.join(self.app_name, 'standalone-arm64'))
        assert File.exists(os.path.join(self.app_name, 'standalone-arm64', 'lib', 'arm64-v8a', 'libNativeScript.so'))
        assert  not File.exists(os.path.join(self.app_name, 'standalone-arm64', 'assets', 'snapshots', 'x86_64',
                                             'snapshot.blob'))
    
    def test_200_build_android_app_bundle(self):
        """Build app with android app bundle option. Verify the output(app.aab) and use bundletool
           to deploy on device."""
        path_to_aab = os.path.join(self.app_name, "platforms", "android", "app", "build", "outputs",
                                   "bundle", "debug", "app-debug.aab")

        result = Tns.build_android(self.app_path, aab=True, verify=False)
        assert "The build result is located at:" in result.output
        assert path_to_aab in result.output
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

    def test_205_build_android_app_bundle_env_snapshot(self):
        """Build app with android app bundle option with --bundle and optimisations for snapshot.
           Verify the output(app.aab) and use bundletool to deploy on device."""
        # This test will not run on windows because env.snapshot option is not available on that OS

        path_to_aab = os.path.join(self.app_name, "platforms", "android", "app", "build",
                                   "outputs", "bundle", "release", "app-release.aab")

        # Configure app with snapshot optimisations
        source = os.path.join('assets', 'abdoid-app-bundle', 'app.gradle')
        target = os.path.join(self.app_name, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source, target)

        webpack_config = os.path.join(self.app_name, 'webpack.config.js')
        File.replace(webpack_config, 'webpackConfig: config,', """webpackConfig: config,
        \nuseLibs: true,\nandroidNdkPath: \"$ANDROID_NDK_HOME\",""")

        # env.snapshot is applicable only in release build
        result = Tns.build_android(self.app_path, aab=True, release=True, snapshot=True,
                                   uglify=True, verify=False)
        assert "The build result is located at:" in result.output
        assert path_to_aab in result.output
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
