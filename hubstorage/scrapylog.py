import os, time

from twisted.python import log as txlog
from scrapy.utils.python import unicode_to_str
from scrapy import log
from hubstorage import Client

def initialize_hubstorage_logging():
    """Initialize twisted logging to use a hubstorage log observer, and return
    that observer.
    """
    e = os.environ
    url = e.get('SHUB_STORAGE', 'http://localhost:8002')
    observer = HubStorageLogObserver(e['SHUB_JOBAUTH'], e['SHUB_PROJECT'],
        e['SHUB_SPIDER'], e['SHUB_JOB'], url=url)
    txlog.startLoggingWithObserver(observer.emit, setStdout=False)
    from twisted.internet import reactor
    reactor.addSystemEventTrigger('after', 'shutdown', observer.stop)
    return observer

def get_log_item(ev, min_level=log.INFO):
    """Get HubStorage log item for the given Twisted event, or None if no
    document should be inserted
    """
    if ev['system'] == 'scrapy':
        level = ev['logLevel']
    else:
        if ev['isError']:
            level = log.ERROR
        else:
            return # ignore non-scrapy & non-error messages
    if level < min_level:
        return
    msg = ev.get('message')
    if msg:
        msg = unicode_to_str(msg[0])
    failure = ev.get('failure', None)
    if failure:
        msg = failure.getTraceback()
    why = ev.get('why', None)
    if why:
        msg = "%s\n%s" % (why, msg)
    fmt = ev.get('format')
    if fmt:
        try:
            msg = fmt % ev
        except:
            msg = "UNABLE TO FORMAT LOG MESSAGE: fmt=%r ev=%r" % (fmt, ev)
            level = log.ERROR
    msg = msg.replace('\n', '\n\t') # to replicate typical scrapy log appeareance
    return {'message': msg, 'level': level, 'time': int(time.time()*1000)}

class HubStorageLogObserver(object):

    def __init__(self, apikey, project, spider, job, level=log.INFO, url='http://localhost:8002'):
        self.level = level
        self.errors_count = 0
        self.client = Client(apikey, url=url)
        path = "/logs/%s/%s/%s" % (project, spider, job)
        self.writer = self.client.open_item_writer(path)

    def emit(self, ev):
        logitem = get_log_item(ev, self.level)
        if logitem:
            self.writer.write_item(logitem)
            self.errors_count += logitem['level'] == log.ERROR

    def stop(self):
        self.writer.close()

    def change_level(self, level):
        self.level = getattr(log, level)
