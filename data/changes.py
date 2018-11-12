import os

from core.settings import Settings
from core.utils.file_utils import File


# noinspection PyShadowingBuiltins
class ChangeSet(object):
    def __init__(self, file, old_value, new_value):
        self.file = file
        self.old_value = old_value
        self.new_value = new_value


class Sync(object):
    @staticmethod
    def replace(app_name, change_set):
        path = os.path.join(Settings.TEST_RUN_HOME, app_name, change_set.file)
        File.replace(path=path, old_string=change_set.old_value, new_string=change_set.new_value)

    @staticmethod
    def revert(app_name, change_set):
        path = os.path.join(Settings.TEST_RUN_HOME, app_name, change_set.file)
        File.replace(path=path, old_string=change_set.new_value, new_string=change_set.old_value)


class Changes(object):
    class JSHelloWord(object):
        JS = ChangeSet(file=os.path.join('app', 'main-view-model.js'), old_value='taps left', new_value='clicks left')
        CSS = ChangeSet(file=os.path.join('app', 'app.css'), old_value='font-size: 18', new_value='font-size: 50')
        XML = ChangeSet(file=os.path.join('app', 'main-page.xml'), old_value='TAP', new_value='HIT')

    class TSHelloWord(object):
        TS = ChangeSet(file=os.path.join('app', 'main-view-model.ts'), old_value='taps left', new_value='clicks left')
        CSS = ChangeSet(file=os.path.join('app', 'app.css'), old_value='font-size: 18', new_value='font-size: 50')
        XML = ChangeSet(file=os.path.join('app', 'main-page.xml'), old_value='TAP', new_value='HIT')

    class NGHelloWorld(object):
        TS = ChangeSet(file=os.path.join('src', 'app', 'item', 'item.service.ts'), old_value='Ter Stegen',
                       new_value='Unknown')
        CSS = ChangeSet(file=os.path.join('src', 'app.css'), old_value='light', new_value='dark')
        HTML = ChangeSet(file=os.path.join('src', 'app', 'item', 'items.component.html'), old_value='"item.name"',
                         new_value='"item.id"')

    class MasterDetailNG(object):
        TS = ChangeSet(file=os.path.join('src', 'app', 'cars', 'shared', 'car.model.ts'),
                       old_value='this._name = options.name;',
                       new_value='this._name = "SyncTSTest";')
        CSS = ChangeSet(file=os.path.join('src', 'app.css'), old_value='light', new_value='dark')
        HTML = ChangeSet(file=os.path.join('src', 'app', 'cars', 'shared', 'car-list.component.html'),
                         old_value='Browse',
                         new_value='Best Car Ever!')

    class SharedHelloWorld(object):
        TS = ChangeSet(file=os.path.join('src', 'app', 'item', 'item.service.ts'), old_value='Ter Stegen',
                       new_value='Unknown')
        CSS = ChangeSet(file=os.path.join('src', 'app', 'app.css'), old_value='light', new_value='dark')
        HTML = ChangeSet(file=os.path.join('src', 'app', 'item', 'items.component.html'), old_value='"item.name"',
                         new_value='"item.id"')
