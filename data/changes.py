import os

from core.settings import Settings
from core.utils.file_utils import File


# noinspection PyShadowingBuiltins
class ChangeSet(object):
    def __init__(self, file, old_value, new_value, old_text, new_text):
        self.file = file
        self.old_value = old_value
        self.new_value = new_value
        self.old_text = old_text
        self.new_text = new_text


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
        JS = ChangeSet(file=os.path.join('app', 'main-view-model.js'),
                       old_value='taps left', new_value='clicks left',
                       old_text='taps left', new_text='clicks left')
        CSS = ChangeSet(file=os.path.join('app', 'app.css'),
                        old_value='font-size: 18', new_value='font-size: 50',
                        old_text=None, new_text=None)
        XML = ChangeSet(file=os.path.join('app', 'main-page.xml'),
                        old_value='TAP', new_value='HIT',
                        old_text='TAP', new_text='HIT')

    class TSHelloWord(object):
        TS = ChangeSet(file=os.path.join('app', 'main-view-model.ts'),
                       old_value='taps left', new_value='clicks left',
                       old_text='taps left', new_text='clicks left')
        CSS = ChangeSet(file=os.path.join('app', 'app.css'),
                        old_value='font-size: 18', new_value='font-size: 50',
                        old_text=None, new_text=None)
        XML = ChangeSet(file=os.path.join('app', 'main-page.xml'),
                        old_value='TAP', new_value='HIT',
                        old_text='TAP', new_text='HIT')

    class NGHelloWorld(object):
        TS = ChangeSet(file=os.path.join('src', 'app', 'item', 'item.service.ts'),
                       old_value='Ter Stegen', new_value='Unknown',
                       old_text='Ter Stegen', new_text='Unknown')
        CSS = ChangeSet(file=os.path.join('src', 'app.css'),
                        old_value='light', new_value='dark',
                        old_text=None, new_text=None)
        HTML = ChangeSet(file=os.path.join('src', 'app', 'item', 'items.component.html'),
                         old_value='"item.name"', new_value='"item.id"',
                         old_text=None, new_text=None)

    class MasterDetailNG(object):
        TS = ChangeSet(file=os.path.join('src', 'app', 'cars', 'shared', 'car.model.ts'),
                       old_value='this._name = options.name;', new_value='this._name = "SyncTSTest";',
                       old_text='BMW 5 Series', new_text='SyncTSTest')
        CSS = ChangeSet(file=os.path.join('src', 'app.css'),
                        old_value='light', new_value='dark',
                        old_text=None, new_text=None)
        HTML = ChangeSet(file=os.path.join('src', 'app', 'cars', 'shared', 'car-list.component.html'),
                         old_value='Browse', new_value='Best Car Ever!',
                         old_text='Browse', new_text='Best Car Ever!')

    class SharedHelloWorld(object):
        TS = ChangeSet(file=os.path.join('src', 'app', 'item', 'item.service.ts'),
                       old_value='Ter Stegen', new_value='Unknown',
                       old_text='Ter Stegen', new_text='Unknown')
        CSS = ChangeSet(file=os.path.join('src', 'app', 'app.css'),
                        old_value='light', new_value='dark',
                        old_text=None, new_text=None)
        HTML = ChangeSet(file=os.path.join('src', 'app', 'item', 'items.component.html'),
                         old_value='"item.name"', new_value='"item.id"',
                         old_text=None, new_text=None)
