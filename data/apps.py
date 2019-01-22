"""
App info.

Notes:
    - SIZE is size, not size on disk!
"""
from core.enums.app_type import AppType


class SizeInfo(object):
    def __init__(self, init=None,
                 apk=None, apk_bundle=None, apk_bundle_uglify_aot=None, apk_bundle_uglify_aot_snapshot=None,
                 ipa=None, ipa_bundle=None, ipa_bundle_uglify_aot=None):
        """
        SizeInfo object.
        :param init: Initial project size (before npm install and platform add).
        :param apk: Size of apk after default release build
        :param apk_bundle: Size of apk after release build with --bundle
        :param apk_bundle_uglify_aot:  Size of apk after release build with --bundle --env.uglify --env.aot
        :param apk_bundle_uglify_aot_snapshot: Size of apk after release build with all the options.
        :param ipa: Size of ipa after default release build.
        :param ipa_bundle:  Size of ipa after release build with --bundle
        :param ipa_bundle_uglify_aot: Size of ipa after release build with --bundle --env.uglify --env.aot
        """
        self.init = init
        self.apk = apk
        self.apk_bundle = apk_bundle
        self.apk_bundle_uglify_aot = apk_bundle_uglify_aot
        self.apk_bundle_uglify_aot_snapshot = apk_bundle_uglify_aot_snapshot
        self.ipa = ipa
        self.ipa_bundle = ipa_bundle
        self.ipa_bundle_uglify_aot = ipa_bundle_uglify_aot


# noinspection PyShadowingBuiltins
class AppInfo(object):
    def __init__(self, app_type, app_id, size, texts):
        """
        AppInfo object.
        :param app_type: Type of Project.
        :param app_id: Bundle id for the app.
        :param size: SizeInfo object.
        :param texts: Array of texts that should be on the home page.
        """
        self.app_type = app_type
        self.bundle_id = app_id
        self.size = size
        self.texts = texts


class Apps(object):
    __ns_only_size = SizeInfo(init=248157241, apk_bundle_uglify_aot_snapshot=15743753, ipa_bundle_uglify_aot=15743753)
    __shared_size = SizeInfo(init=273331339, apk_bundle_uglify_aot_snapshot=15743753, ipa_bundle_uglify_aot=15743753)
    SCHEMATICS_SHARED = AppInfo(app_type=AppType.SHARED_NG, app_id=None, size=__shared_size, texts=['Welcome'])
    SCHEMATICS_SHARED_SAMPLE = AppInfo(app_type=AppType.SHARED_NG, app_id=None, size=__shared_size, texts=['Barcelona'])
    SCHEMATICS_NS = AppInfo(app_type=AppType.NG, app_id=None, size=__ns_only_size, texts=['Tap the button'])
    HELLO_WORLD_JS = AppInfo(type=AppType.JS, app_id=None, size=None, texts=None)
    HELLO_WORLD_TS = AppInfo(type=AppType.TS, app_id=None, size=None, texts=None)
    HELLO_WORLD_NG = AppInfo(type=AppType.NG, app_id=None, size=None, texts=None)
