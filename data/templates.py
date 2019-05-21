import os

from core.enums.app_type import AppType
from core.settings.Settings import TEST_SUT_HOME
from products.nativescript.template_info import TemplateInfo


def gen_template_info(name, app_type, texts=None):
    return TemplateInfo(name=name, local_package=os.path.join(TEST_SUT_HOME, '{0}.tgz'.format(name)), app_type=app_type,
                        texts=texts)


class Template(object):
    # Texts used in templates
    hw_js = ['TAP']
    hw_ng = ['Ter Stegen']
    md_str = ['Ford KA']
    dr_str = ['Home']
    tn_str = ['Item 1']
    login = ['Login']

    # Templates repo
    REPO = 'https://github.com/NativeScript/nativescript-app-templates'

    # Blank templates
    BLANK_JS = gen_template_info(name='template-blank', app_type=AppType.JS)
    BLANK_TS = gen_template_info(name='template-blank-ts', app_type=AppType.TS)
    BLANK_NG = gen_template_info(name='template-blank-ng', app_type=AppType.NG)

    # Hello-World templates
    HELLO_WORLD_JS = gen_template_info(name='template-hello-world', app_type=AppType.JS, texts=hw_js)
    HELLO_WORLD_TS = gen_template_info(name='template-hello-world-ts', app_type=AppType.TS, texts=hw_js)
    HELLO_WORLD_NG = gen_template_info(name='template-hello-world-ng', app_type=AppType.NG, texts=hw_ng)

    # Master-Detail templates (with Firebase)
    MASTER_DETAIL_JS = gen_template_info(name='template-master-detail', app_type=AppType.JS, texts=md_str)
    MASTER_DETAIL_TS = gen_template_info(name='template-master-detail-ts', app_type=AppType.TS, texts=md_str)
    MASTER_DETAIL_NG = gen_template_info(name='template-master-detail-ng', app_type=AppType.NG, texts=md_str)
    MASTER_DETAIL_VUE = gen_template_info(name='template-master-detail-vue', app_type=AppType.VUE, texts=md_str)

    # Master-Detail templates (with Kinvey)
    MASTER_DETAIL_KINVEY_JS = gen_template_info(name='template-master-detail-kinvey', app_type=AppType.JS,
                                                texts=md_str)
    MASTER_DETAIL_KINVEY_TS = gen_template_info(name='template-master-detail-kinvey-ts', app_type=AppType.TS,
                                                texts=md_str)
    MASTER_DETAIL_KINVEY_NG = gen_template_info(name='template-master-detail-kinvey-ng', app_type=AppType.NG,
                                                texts=md_str)

    # Drawer templates
    DRAWER_NAVIGATION_JS = gen_template_info(name='template-drawer-navigation', app_type=AppType.JS, texts=dr_str)
    DRAWER_NAVIGATION_TS = gen_template_info(name='template-drawer-navigation-ts', app_type=AppType.TS, texts=dr_str)
    DRAWER_NAVIGATION_NG = gen_template_info(name='template-drawer-navigation-ng', app_type=AppType.NG, texts=dr_str)
    DRAWER_NAVIGATION_VUE = gen_template_info(name='template-drawer-navigation-vue', app_type=AppType.VUE, texts=dr_str)

    # Tab templates
    TAB_NAVIGATION_JS = gen_template_info(name='template-tab-navigation', app_type=AppType.JS, texts=tn_str)
    TAB_NAVIGATION_TS = gen_template_info(name='template-tab-navigation-ts', app_type=AppType.TS, texts=tn_str)
    TAB_NAVIGATION_NG = gen_template_info(name='template-tab-navigation-ng', app_type=AppType.NG, texts=tn_str)

    # Health templates
    HEALTH_SURVEY_NG = gen_template_info(name='template-health-survey-ng', app_type=AppType.NG, texts=login)
    PATIENT_CARE_NG = gen_template_info(name='template-patient-care-ng', app_type=AppType.NG, texts=login)

    # Vue templates
    VUE_BLANK = gen_template_info(name='template-blank-vue', app_type=AppType.VUE)

    # Enterprise templates
    ENTERPRISE_AUTH_JS = gen_template_info(name='template-enterprise-auth', app_type=AppType.JS, texts=['Log in'])
    ENTERPRISE_AUTH_TS = gen_template_info(name='template-enterprise-auth-ts', app_type=AppType.TS, texts=['Log in'])
    ENTERPRISE_AUTH_NG = gen_template_info(name='template-enterprise-auth-ng', app_type=AppType.NG, texts=['Log in'])

    # Minimal templates (not shipped for users, we bring them in assets folder)
    MIN_JS = gen_template_info(name='template-min', app_type=AppType.JS)
