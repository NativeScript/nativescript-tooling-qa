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
    def __init__(self, type, id, size, texts):
        """
        AppInfo object.
        :param type: Type of Project.
        :param id: Bundle id for the app.
        :param size: SizeInfo object.
        :param texts: Array of texts that should be on the home page.
        """
        self.type = type
        self.id = id
        self.size = size
        self.texts = texts


class Apps(object):
    __ns_only_size = SizeInfo(init=273331339, apk_bundle_uglify_aot_snapshot=15743753, ipa_bundle_uglify_aot=15743753)
    __shared_size = SizeInfo(init=366628675, apk_bundle_uglify_aot_snapshot=15743753, ipa_bundle_uglify_aot=15743753)
    SHEMATICS_SHARED = AppInfo(type=AppType.SHARED_NG, id=None, size=__shared_size, texts=['Welcome'])
    SHEMATICS_SHARED_SAMPLE = AppInfo(type=AppType.SHARED_NG, id=None, size=__shared_size, texts=['Barcelona'])
    SHEMATICS_NS = AppInfo(type=AppType.NG, id=None, size=__ns_only_size, texts=['Tap the button'])
