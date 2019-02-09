from core.base_test.tns_run_test import TnsRunTest
from core.log.log import Log


class TestTnsRunBaseTest(TnsRunTest):

    def test_smoke(self):
        Log.info(self.emu.get_text())
        Log.info(self.sim.get_text())
