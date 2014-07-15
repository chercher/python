#!/usr/local/bin/python

import urllib2,json,re,libxml2


def parse_json(jsonurl, key):
	response=urllib2.urlopen(jsonurl).read()
	result=json.load(response)[key]
	
	global building_flows
	global tobuild_flow
	if key == 'jobs':
		for job in result:
			if re.search('flow', job['url']) is not None:
				building_flows.append(job['url'])
	elif key == "downstreamProjects":
		tobuild_flow.append(result[0]['url'])
	else:
		print "invalid key"
		sys.exit(1)
		
def parse_dsl(flowlist):
	dsls=[]
	for flow in flowlist:
		configurl=flow+'config.xml'
		configxml=urllib2.urlopen(configurl).read()
		ctxt=libxml2.parseDoc(configxml).xpathNewContext()
		dsl=ctxt.xpathEval('//dsl')
		dsls.append(dsl[0].content.replace('\n', ''))
	alldols=[]
	alltbls=[]
	for dsl in dsls:
		if re.search('guard', dsl) is not None:	
			doltbl=re.search('guard\s\{(.*)\}\srescue', dsl).group(1)
			dols=re.findall('dol:\s\"(.*?)\"', doltbl)
			alldols.append(dols)
			tbls=re.findall('table:\s\"(.*?)\"', doltbl)
			alltbls.append(tbls)
		else:
			dols=re.findall('dol:\s\"(.*?)\"', doltbl) 
                        alldols.append(dols)
                        tbls=re.findall('table:\s\"(.*?)\"', doltbl)
                        alltbls.append(tbls)

	alldolset=set(alldols)
	alltblset=set(alltblset)			
	doltbl=[alldolset, alltblset]

	return doltbl



building_api_url='http://10.1.7.159/view/building/api/json'
building_flows=[]
tobuild_flow=[]


