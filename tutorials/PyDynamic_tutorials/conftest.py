"""This is the all so famous conftest.py which is available in all pytest runs"""
from nbval.plugin import IPyNbFile


def pytest_collectstart(collector):
    """Exclude those outputs from nbval's comparisons that change from run to run"""
    if isinstance(collector, IPyNbFile):
        collector.skip_compare += (
            "stderr",
            "application/javascript",
            "application/vnd.holoviews_load.v0+json",
            "text/html",
        )
