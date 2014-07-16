#!/usr/local/bin/python

import urllib2,json,re,libxml2,sys,time

def parse_json(jsonurl, key):
	try:
		response=urllib2.urlopen(jsonurl).read()
		result=json.loads(response)[key]
	except urllib2.HTTPError:
		sys.exit('HTTP Error 404: Not Found %s' % jsonurl)
	
	flows=[]
	if key=='jobs':
		for job in result:
			if re.search('flow', job['url']) is not None:
				flows.append(job['url'])
	elif key=='downstreamProjects':
		flows.append(result[0]['url'])
	else:
		sys.exit('parse_json does not parse %s with %s' % (jsonurl, key))
	return flows
		
def parse_dsl(flowlist):
	dsls=[]
	for flow in flowlist:
		configurl=flow+'config.xml'
		try:
			configxml=urllib2.urlopen(configurl).read()
			doc=libxml2.parseDoc(configxml)
			ctxt=doc.xpathNewContext()
			dsl=ctxt.xpathEval('//dsl')
			if dsl:
				dsls.append(dsl[0].content.replace('\n', ''))
			doc.freeDoc()
			ctxt.xpathFreeContext()
		except urllib2.HTTPError: 
			sys.exit('HTTP Error 404: Not Found %s' % configurl)

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

def detect_conflict(conflict_detect_job_url):
        building_api_url='http://10.1.7.159/view/building/api/json'

        building_flows=parse_json(building_api_url, 'jobs')
        tobuild_flow=parse_json(conflict_detect_job_url, 'downstreamProjects')

        building_doltbl=parse_dsl(building_flows)
        tobuild_doltbl=parse_dsl(tobuild_flow)	

	#print building_doltbl
	#print tobuild_doltbl
	
	if (len(building_doltbl[0].intersection(tobuild_doltbl[0])) != 0) or (len(building_doltbl[0].intersection(tobuild_doltbl[1])) != 0) or (len(building_doltbl[1].intersection(tobuild_doltbl[0])) != 0):
		return True
	return False

if __name__== '__main__':
	if (len(sys.argv) != 2):
		sys.exit('Usage: %s conflict_detect_job_url' % sys.argv[0])

        conflict_detect_job_url=sys.argv[1]
	if_conflict=detect_conflict(conflict_detect_job_url)
	while if_conflict:
		print 'conflict occurs! wait 10 secondes ...'
		sys.stdout.flush()
		time.sleep(10)
		if_conflict=detect_conflict(conflict_detect_job_url)
	sys.exit(0)
