class DownloadPackageEvent(object):

    def __init__(self, package, version, filename):
        self.package = package
        self.version = version
        self.filename = filename
