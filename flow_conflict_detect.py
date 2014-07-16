#!/usr/local/bin/python

import urllib2,json,re,libxml2,sys,time

def parse_json(jsonurl, key):
	response=urllib2.urlopen(jsonurl).read()
	result=json.loads(response)[key]
	
	flows=[]
	if key=='jobs':
		for job in result:
			if re.search('flow', job['url']) is not None:
				flows.append(job['url'])
	elif key=='downstreamProjects':
		flows.append(result[0]['url'])
	else:
		print 'parse_json does not parse %s with %s' % (jsonurl, key)
		sys.exit(1)
	return flows
		
def parse_dsl(flowlist):
	dsls=[]
	for flow in flowlist:
		configurl=flow+'config.xml'
		configxml=urllib2.urlopen(configurl).read()
		doc=libxml2.parseDoc(configxml)
		ctxt=doc.xpathNewContext()
		dsl=ctxt.xpathEval('//dsl')
		dsls.append(dsl[0].content.replace('\n', ''))
		doc.freeDoc()
		ctxt.xpathFreeContext()
	alldols=[]
	alltbls=[]
	for dsl in dsls:
		if re.search('guard', dsl) is not None:	
			doltbl=re.search('guard\s\{(.*)\}\srescue', dsl).group(1)
			dols=re.findall('dol:\s\"(.*?)\"', doltbl)
			alldols.extend(dols)
			tbls=re.findall('table:\s\"(.*?)\"', doltbl)
			alltbls.extend(tbls)
		else:
			dols=re.findall('dol:\s\"(.*?)\"', doltbl) 
                        alldols.extend(dols)
                        tbls=re.findall('table:\s\"(.*?)\"', doltbl)
                        alltbls.extend(tbls)

	alldolset=set(alldols)
	alldolset2=set()
	for dol in alldolset:
		alldolset2.add(dol.split('.')[-2])
		
	alltblset=set(alltbls)			
	doltbl=[alldolset2, alltblset]

	return doltbl

def detect_conflict():

        building_api_url='http://10.1.7.159/view/building/api/json'
        conflict_detect_url=sys.argv[1]

        building_flows=parse_json(building_api_url, 'jobs')
        tobuild_flow=parse_json(conflict_detect_url, 'downstreamProjects')

        building_doltbl=parse_dsl(building_flows)
        tobuild_doltbl=parse_dsl(tobuild_flow)	
	
	if (len(building_doltbl[0].intersection(tobuild_doltbl[0])) != 0) or (len(building_doltbl[0].intersection(tobuild_doltbl[1])) != 0) or (len(building_doltbl[1].intersection(tobuild_doltbl[0])) != 0):
		return True
	return False

if __name__== '__main__':
	
	if_conflict=True
	while if_conflict:
		if_conflict=detect_conflict()
		time.sleep(2)
	sys.exit(0)
