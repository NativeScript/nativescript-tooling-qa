class TestContext(object):

    class Processes(object):
        STARTED_PROCESSES = []

    class CurrentTest(object):
        TEST_NAME = None
        TEST_APP_NAME = None

    class CurrentDevice(object):
        EMU_ID = None
        SIM_ID = None
        ANDROID_ID = None
        IOS_IS = None
