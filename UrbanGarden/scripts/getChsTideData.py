""" 
--------------
getChsTideData.py

Description: Get Water Level data via the CHS webservice between given dates.

Inputs: (name, type, description and allowed values)

	dtype 	[string]:	'obs' for observational data, 'pred' for predictions
	sd 	[string]: 	startDate in YYYY-MM-DD HH:MM:SS format
	ed 	[string]: 	endDate in YYYY-MM-DD HH:MM:SS format
	order 	[string]: 	order to arrange output data - 'asc' for ascending, 'desc' for descending
	stnId 	[string]: 	5 digit tide station id
	numData [int]: 		Number of data to return in each call
	dtFmt	[string]:	Date format of input date string

Output:

	pandas DataFrame with columns ['TYPE','DATETIME','MDATE','STATION_ID','LAT','LON','VALUE']
	* note that MDATE is a serialized date in the matlab format	
	
Example Call:

	getTide('obs','2017-09-08 12:00:00', '2017-09-09 12:00:00', 'asc', '07120', 1000)

Sept 27, 2017 MAJ

""" 


from zeep import helpers,Client
import json
import datetime as dt
import matplotlib.dates as mdates
import pandas as pd
from dateutil.relativedelta import relativedelta

def getTide(dtype, sd, ed, order, stnId, numData, dtFmt):

	# get observational or prediction data
	if dtype=='pred':
		endPoint = 'https://ws-shc.qc.dfo-mpo.gc.ca/predictions?WSDL'
		print('Retrieving predictions from ' + sd + ' to ' + ed + ' for Station ' + stnId)
	else:
		endPoint = 'https://ws-shc.qc.dfo-mpo.gc.ca/observations?WSDL'
		print('Retrieving observations from ' + sd + ' to ' + ed + ' for Station ' + stnId)
	# origStartDtObj = dt.datetime.strptime(dt.datetime.strptime(sd,dtFmt).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
	origStartDtObj = dt.datetime.strptime(sd,dtFmt)
	endDtObj = dt.datetime.strptime(dt.datetime.strptime(ed,dtFmt).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

	client = Client(endPoint)
	data = []
	dates = []
	startDtObj = origStartDtObj
	df = pd.DataFrame(columns=['TYPE','DATETIME','MDATE','STATION_ID','LAT','LON','VALUE'])
	while startDtObj<endDtObj:
	
	    newStartDate = startDtObj.strftime('%Y-%m-%d %H:%M:%S')
	    if dtype=='pred':
	    	    obj = client.service.search("wl15", -90.0, 90.0, -180.0, 180.0, 0.0, 0.0, newStartDate,ed, 1, numData, True, "station_id="+stnId, order)	    
	    else:
	    	    obj = client.service.search("wl", -90.0, 90.0, -180.0, 180.0, 0.0, 0.0, newStartDate,ed, 1, numData, True, "station_id="+stnId, order)
	    inputDict = helpers.serialize_object(obj)
	    outputDict = json.loads(json.dumps(inputDict))
	    if bool(inputDict['data'])==True:
	    	for i,var in enumerate(outputDict['data']):
	    	    data.append(float(outputDict['data'][i]['value']))
	    	    dates.append(outputDict['data'][i]['boundaryDate']['min'])
	    	startDtObj = dt.datetime.strptime(dates[-1],'%Y-%m-%d %H:%M:%S')
	    else:
	    	print('      No data found between '+newStartDate+' and '+ed+' for '+stnId)
	    	# increment by a day 
	    	startDtObj = startDtObj + relativedelta(days=1)
	    	
	dts = [dt.datetime.strptime(d,dtFmt) for d in dates]
	mdts = [mdates.date2num(d) for d in dts]
	if bool(dts)==False:
		if dtype=='pred':
			print('No predictions found between '+sd+' and '+ed+' for '+stnId)
		else:
			print('No data found between '+sd+' and '+ed+' for '+stnId)
	else:
		print('Retrieval complete.')
		df['TYPE'] = dtype
		df['DATETIME'] = dts
		df['MDATE'] = mdts
		df['STATION_ID'] = stnId
		df['LAT'] = outputDict['boundarySpatial']['latitude']['min']
		df['LON'] = outputDict['boundarySpatial']['longitude']['min']
		df['VALUE'] = data
	return df