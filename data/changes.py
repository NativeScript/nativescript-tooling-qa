import os

from core.settings import Settings
from core.utils.file_utils import File
from data.const import Colors


# noinspection PyShadowingBuiltins
class ChangeSet(object):
    def __init__(self, file_path, old_value, new_value, old_text=None, new_text=None, old_color=None, new_color=None):
        self.file_path = file_path
        self.old_value = old_value
        self.new_value = new_value
        self.old_text = old_text
        self.new_text = new_text
        self.old_color = old_color
        self.new_color = new_color


class Sync(object):
    @staticmethod
    def replace(app_name, change_set, fail_safe=False):
        path = os.path.join(Settings.TEST_RUN_HOME, app_name, change_set.file_path)
        File.replace(path=path, old_string=change_set.old_value, new_string=change_set.new_value, fail_safe=fail_safe)

    @staticmethod
    def revert(app_name, change_set, fail_safe=False):
        path = os.path.join(Settings.TEST_RUN_HOME, app_name, change_set.file_path)
        File.replace(path=path, old_string=change_set.new_value, new_string=change_set.old_value, fail_safe=fail_safe)


class Changes(object):
    class JSHelloWord(object):
        JS = ChangeSet(file_path=os.path.join('app', 'main-view-model.js'),
                       old_value='taps left', new_value='clicks left',
                       old_text='taps left', new_text='clicks left')
        CSS = ChangeSet(file_path=os.path.join('app', 'app.css'),
                        old_value='font-size: 18', new_value='font-size: 50',
                        old_color=None, new_color=None)
        XML = ChangeSet(file_path=os.path.join('app', 'main-page.xml'),
                        old_value='TAP', new_value='HIT',
                        old_text='TAP', new_text='HIT')
        XML_ACTION_BAR = ChangeSet(file_path=os.path.join('app', 'main-page.xml'),
                                   old_value='My App', new_value='TestApp',
                                   old_text='My App', new_text='TestApp')

    class TSHelloWord(object):
        TS = ChangeSet(file_path=os.path.join('app', 'main-view-model.ts'),
                       old_value='taps left', new_value='clicks left',
                       old_text='taps left', new_text='clicks left')
        CSS = ChangeSet(file_path=os.path.join('app', 'app.css'),
                        old_value='font-size: 18', new_value='font-size: 50',
                        old_color=None, new_color=None)
        XML = ChangeSet(file_path=os.path.join('app', 'main-page.xml'),
                        old_value='TAP', new_value='HIT',
                        old_text='TAP', new_text='HIT')

    class NGHelloWorld(object):
        TS = ChangeSet(file_path=os.path.join('src', 'app', 'item', 'item.service.ts'),
                       old_value='Ter Stegen', new_value='Unknown',
                       old_text='Ter Stegen', new_text='Unknown')
        CSS = ChangeSet(file_path=os.path.join('src', 'app.css'),
                        old_value='light', new_value='dark',
                        old_color=Colors.WHITE, new_color=Colors.DARK)
        HTML = ChangeSet(file_path=os.path.join('src', 'app', 'item', 'items.component.html'),
                         old_value='"item.name"', new_value='"item.id"',
                         old_text=None, new_text=None)

    class MasterDetailNG(object):
        TS = ChangeSet(file_path=os.path.join('src', 'app', 'cars', 'shared', 'car.model.ts'),
                       old_value='options.name;', new_value='"SyncTSTest";',
                       old_text='Ford KA', new_text='SyncTSTest')
        HTML = ChangeSet(file_path=os.path.join('src', 'app', 'cars', 'car-list.component.html'),
                         old_value='Browse', new_value='Best Car Ever!',
                         old_text='Browse', new_text='Best Car Ever!')

        # This change should make title of cars pink
        SCSS_ROOT_COMMON = ChangeSet(file_path=os.path.join('src', '_app-common.scss'),
                                     old_value='$accent-dark;', new_value='pink;',
                                     old_color=Colors.ACCENT_DARK, new_color=Colors.PINK)

        # This change should add some red between list view items on home page
        SCSS_ROOT_ANDROID = ChangeSet(file_path=os.path.join('src', 'app.android.scss'),
                                      old_value='Android here',
                                      new_value='Android here\n.page { background-color: red;}\n',
                                      old_color=Colors.WHITE, new_color=Colors.RED_DARK)
        SCSS_ROOT_IOS = ChangeSet(file_path=os.path.join('src', 'app.ios.scss'),
                                  old_value='iOS here',
                                  new_value='iOS here\n.page { padding: 30; background-color: red; }\n',
                                  old_color=Colors.WHITE, new_color=Colors.RED)

        # This change should make background of items on home page purple
        SCSS_NESTED_COMMON = ChangeSet(file_path=os.path.join('src', 'app', 'cars', '_car-list.component.scss'),
                                       old_value='$background-light;', new_value='purple;',
                                       old_color=Colors.WHITE, new_color=Colors.PURPLE)

        # This change should make icons on home page yellow
        SCSS_NESTED_ANDROID = ChangeSet(file_path=os.path.join('src', 'app', 'cars', 'car-list.component.android.scss'),
                                        old_value='Android here',
                                        new_value='Android here\n.list-group{.list-group-item{.fa{color:yellow;}}}\n',
                                        old_color=None, new_color=Colors.YELLOW)

        SCSS_NESTED_IOS = ChangeSet(file_path=os.path.join('src', 'app', 'cars', 'car-list.component.ios.scss'),
                                    old_value='iOS here',
                                    new_value='iOS here\n.list-group{.list-group-item{.fa{color:yellow;}}}\n',
                                    old_color=None, new_color=Colors.YELLOW)

    class SharedHelloWorld(object):
        TS = ChangeSet(file_path=os.path.join('src', 'app', 'item', 'item.service.ts'),
                       old_value='Ter Stegen', new_value='Unknown',
                       old_text='Ter Stegen', new_text='Unknown')
        CSS = ChangeSet(file_path=os.path.join('src', 'app', 'app.css'),
                        old_value='light', new_value='dark',
                        old_color=None, new_color=None)
        HTML = ChangeSet(file_path=os.path.join('src', 'app', 'item', 'items.component.html'),
                         old_value='"item.name"', new_value='"item.id"',
                         old_text=None, new_text=None)

    class BlankVue(object):
        VUE_SCRIPT = ChangeSet(file_path=os.path.join('app', 'components', 'Home.vue'),
                               old_value='Blank {N}-Vue app', new_value='TEST APP',
                               old_text='Blank {N}-Vue app', new_text='TEST APP')
        VUE_TEMPLATE = ChangeSet(file_path=os.path.join('app', 'components', 'Home.vue'),
                                 old_value='Home', new_value='TITLE',
                                 old_text='Home', new_text='TITLE')
        VUE_STYLE = ChangeSet(file_path=os.path.join('app', 'components', 'Home.vue'),
                              old_value='font-size: 20;', new_value='font-size: 20; color: red;',
                              old_color=Colors.DARK, new_color=Colors.RED)

    class MasterDetailVUE(object):
        VUE_SCRIPT = ChangeSet(file_path=os.path.join('app', 'components', 'Home.vue'),
                               old_value='Blank {N}-Vue app', new_value='TEST APP',
                               old_text='Blank {N}-Vue app', new_text='TEST APP')
        VUE_TEMPLATE = ChangeSet(file_path=os.path.join('app', 'components', 'CarList.vue'),
                                 old_value='Car List', new_value='Master Detail',
                                 old_text='Car List', new_text='Master Detail')
        VUE_STYLE = ChangeSet(file_path=os.path.join('app', 'components', 'CarList.vue'),
                              old_value='background-color: $background-light;',
                              new_value='background-color: rgb(229, 4, 5);',
                              old_color=Colors.WHITE, new_color=Colors.RED_DARK)
        VUE_DETAIL_PAGE_TEMPLATE = ChangeSet(file_path=os.path.join('app', 'components', 'CarDetails'),
                                             old_value='<Span text="/day" />', new_value='<Span text="/24h" />',
                                             old_text='/day', new_text='/24h')
