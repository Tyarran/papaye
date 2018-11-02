import json

from pyramid.events import BeforeRender, subscriber

from papaye.events import DownloadPackageEvent
from papaye.tasks.download import download_release_from_pypi


@subscriber(DownloadPackageEvent)
def cache_missing(event):
    download_release_from_pypi.delay(
        event.package,
        event.version,
        event.filename,
    )


@subscriber(BeforeRender)
def add_state(event):
    event['state'] = json.dumps(
        event['request'].state
    )
