#!/usr/bin/python3
import sys,json,requests,re

#if any impacting changes to this plugin kindly increment the plugin version here.
PLUGIN_VERSION = "2"
#Setting this to true will alert you when there is a communication problem while posting plugin data to server
HEARTBEAT="true"
SOLR_URL = "http://localhost:8983"
SOLR_DEFAULT_CORE = "searchterms"
METRIC_UNITS = {'uptime': 'Seconds', 'memoryUsageJVM': '%'}

def solrApiCall (uri, params={}):
    params['wt'] = 'json'
    try:
        r =  requests.get(SOLR_URL + uri, params=params)
        j = json.loads(r.text)
        return j
    except:
        raise

def solrPingCall (core):
    r = solrApiCall('/solr/'+core+'/admin/ping',{'distrib': 'false'})
    return r

def metricCollector():
    data = {'heartbeat_required':HEARTBEAT, 'plugin_version':PLUGIN_VERSION}
    data["units"] = METRIC_UNITS
    try:
        solrAdminInfo = solrApiCall("/solr/admin/info/system")
        data["uptime"] = (solrAdminInfo['jvm']['jmx']['upTimeMS'] / 1000 )
        totalMemoryJVM = re.split('\s', solrAdminInfo['jvm']['memory']['total'])
        data["totalMemoryJVM"] = totalMemoryJVM[0] # value
        data["units"]["totalMemoryJVM"] = totalMemoryJVM[1]
        usedMemoryJVM = re.split('\s', solrAdminInfo['jvm']['memory']['used'])
        data["usedMemoryJVM"] = usedMemoryJVM[0] # value
        data["units"]["usedMemoryJVM"] = usedMemoryJVM[1]
        data["memoryUsageJVM"] = re.findall(r'\(%(\S+)\)', usedMemoryJVM[2])[0]
        data["defaultCorePing"] = solrPingCall(SOLR_DEFAULT_CORE)['status']
    except Exception as e:
        print ("status error ",e)
        data["error"] = str(e)
    return data

if __name__ == "__main__":
    result = metricCollector()

print(json.dumps(result, indent=4, sort_keys=True))
