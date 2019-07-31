from agentMET4FOF_ML.coupled_ML import main as coupled_ml_main
from agentMET4FOF_ML.decoupled_ML import main as decoupled_ml_main


class TestML:

    def test_coupled_ML(self):
        coupled_ml_main().shutdown()

    def test_decoupled_ML(self):
        decoupled_ml_main().shutdown()
