from nbval.plugin import IPyNbFile


def pytest_collectstart(collector):
    if isinstance(collector, IPyNbFile):
        collector.skip_compare += 'stderr', \
                                  'application/javascript', \
                                  'application/vnd.holoviews_load.v0+json', \
                                  'text/html',
