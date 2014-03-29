import json
#import grequests

from papaye.tasks import task


def save_release_informations(package, release, json_infos):
    release_doc = {'type': 'release', 'package': package, 'name': release}
    release_doc.update(json_infos)
    return release_doc


def write_file(package, release, filename):
    pass


@task
def download_release(package, release):
    print("download")
    #request = grequests.get('http://pypi.python.org/pypi/{}/{}/json'.format(package, release))
    #response = request.send()
    #result = json.loads(response.content)
    #urls = [release_file['url'] for release_file in result['urls']]
    #rs = (grequests.get(url) for url in urls)
    #print(grequests.map(rs))
    #import ipdb; ipdb.set_trace()
    #for release_file in result['urls']:
    #    result = grequests.get(release_file['url'])
    #    print release_file['url']
    print("downloaded")
    return {"ok": "ok"}


@task
def test_func(*args, **kwargs):
    print(args, kwargs)
    for index in range(1, 11):
        print(index)
        import time
        time.sleep(0.3)
