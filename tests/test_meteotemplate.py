import http.server
import queue
import sqlite3
import threading
from urllib.parse import parse_qs, urlsplit

import pytest
import weewx
import weewx.restx
import meteotemplate


class Archive:
    table_name = 'archive'

    def __init__(self):
        self.connection=sqlite3.connect(':memory:')
        self.connection.execute('CREATE TABLE archive (dateTime INTEGER, usUnits INTEGER, rain REAL)')
        self.connection.executemany('INSERT INTO archive VALUES (?,17,?)', [(1700049300,2),(1700049600,3)])

    def getSql(self, query, parameters):
        return self.connection.execute(query,parameters).fetchone()


def test_daily_rain_uses_archive_sum_not_last_increment():
    worker=meteotemplate.MeteotemplateThread(queue.Queue(),password='local')
    record=worker.get_record({'dateTime':1700049600,'usUnits':weewx.METRICWX,'rain':3},Archive())
    data=parse_qs(urlsplit(worker.format_url(record)).query)
    assert data['R']==['5.000']


def test_optional_ecowitt_fields_reach_receiver_and_errors_stay_visible():
    received=[]
    reply=[b'Success\n']

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            received.append(parse_qs(urlsplit(self.path).query))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(reply[0])

        def log_message(self,*args):
            pass

    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        worker=meteotemplate.MeteotemplateThread(queue.Queue(),password='local',server_url='http://127.0.0.1:%d/api.php'%server.server_port,field_map={'PP1':'pm2_5','PP2':'pm10','L':'lightning_strike_count'},max_tries=1)
        worker.process_record({'dateTime':1700000000,'usUnits':weewx.METRICWX,'pm2_5':0,'pm10':None,'lightning_strike_count':2},None)
        assert received[0]['PP1']==['0.000']
        assert received[0]['L']==['2']
        assert 'PP2' not in received[0]
        reply[0]=b'Unauthorized'
        with pytest.raises(weewx.restx.FailedPost):
            worker.process_record({'dateTime':1700000300,'usUnits':weewx.METRICWX,'outTemp':0},None)
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_prerelease_of_newer_weewx_is_supported():
    assert meteotemplate._version_key('5.2.0b1') > meteotemplate._version_key('3.5.0')
    assert meteotemplate._version_key('3.5.0b1') < meteotemplate._version_key('3.5.0')


def test_unknown_option_is_ignored_with_warning(tmp_path, monkeypatch, caplog):
    import types
    import configobj
    monkeypatch.setattr(meteotemplate.MeteotemplateThread, 'start', lambda self: None)
    engine=types.SimpleNamespace(bind=lambda *args: None)
    config=configobj.ConfigObj({'WEEWX_ROOT':str(tmp_path),'StdRESTful':{'Meteotemplate':{'password':'local','timeout':'5','station':'x'}}})
    service=meteotemplate.Meteotemplate(engine,config)
    assert service._thread.timeout==5
    assert 'Ignoring unknown option station' in caplog.text


def test_snow_depth_is_sent_in_mm():
    worker=meteotemplate.MeteotemplateThread(queue.Queue(),password='local')
    data=parse_qs(urlsplit(worker.format_url({'dateTime':1700000000,'usUnits':weewx.US,'snowDepth':2.0})).query)
    assert data['SD']==['50.800']


def test_metric_record_without_database_is_not_changed():
    worker=meteotemplate.MeteotemplateThread(queue.Queue(),password='local')
    record={'dateTime':1700000000,'usUnits':weewx.METRIC,'dayRain':1.0,'rainRate':2.0,'snowDepth':3.0}
    data=parse_qs(urlsplit(worker.format_url(worker.get_record(record,None))).query)
    assert data['R']==['10.000']
    assert record=={'dateTime':1700000000,'usUnits':weewx.METRIC,'dayRain':1.0,'rainRate':2.0,'snowDepth':3.0}
