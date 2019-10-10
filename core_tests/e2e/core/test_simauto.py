from core.base_test.tns_run_ios_test import TnsRunIOSTest

from core.utils.device.simctl import Simctl


class SimAutoTests(TnsRunIOSTest):
    apk_path = None

    @classmethod
    def setUpClass(cls):
        TnsRunIOSTest.setUpClass()

    def setUp(self):
        TnsRunIOSTest.setUp(self)

    def tearDown(self):
        TnsRunIOSTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsRunIOSTest.tearDownClass()

    def test_01_sim_auto_smoke_test(self):
        self.sim.wait_for_text(text="Calendar")
        self.sim.wait_for_text(text="Photos")
