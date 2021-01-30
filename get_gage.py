'''
Toolkit for downloading USGS streamflow data based on station_id and date range

Datetime are converted to UTC time for the ease of modeling.


__author__= 'Allen'
__date__= '2021/01/30'
'''

import pandas as pd
from pytz import timezone
from climata.usgs import InstantValueIO
import argparse
import sys
import numpy as np

parser = argparse.ArgumentParser(description='Retrieve USGS streamflow/stage records, output data in metrics')
parser.add_argument('--id', type=str, metavar='id',
                    help='one (or more) stations e.g., 08076700')

parser.add_argument('--parameter_id', metavar='param', type=str, default='00060', nargs='?',
                   help='parameter to retrieve, default - 00060 - streamflow')

parser.add_argument('--start_time', metavar='start', type=str,
                    help='the beginning time (%Y%m%d%H%M%S) e.g.,201708250000')

parser.add_argument('--end_time', metavar='end', type=str,
                    help='the end time (%Y%m%d%H%M%S) e.g.,201708300000')

parser.add_argument('--to_UTC', metavar='UTC', type=bool, nargs='?', default=True,
                   help='Convert to UTC time, default True')

parser.add_argument('--dst', metavar='dst', type=str, nargs='?', default='output.csv',
                   help='Output file name')

args = parser.parse_args()
station_id= args.id
parameter_id= args.parameter_id
isConvert=args.to_UTC
start= args.start_time
end=args.end_time
dst= args.dst

print(
'''
-----------------------
Downloading station %s from %s to %s
-----------------------
'''%(station_id, start, end))


try:
    start= pd.to_datetime(start, format='%Y%m%d%H%M')
    end= pd.to_datetime(end, format='%Y%m%d%H%M')
except:
    sys.exit('Date format is not correct. Recgonizable format %Y%m%d%H%M e.g., 201708250000')
    
datelist = pd.date_range(start=start, end=end).tolist()
data = InstantValueIO(
    start_date=datelist[0],
    end_date=datelist[-1],
    station=station_id,
    parameter=parameter_id,
)

for series in data:
    data = [r[1] for r in series.data]
    dates = [r[0] for r in series.data]
    
df=pd.DataFrame()
if isConvert:
    df['datetime']=[date.astimezone(timezone('UTC')) for date in dates]
else:
    df['datetime']= dates
    
df['discharge']= np.array(data) * 0.0283
df.set_index('datetime', inplace=True)
df.index= df.index.tz_localize(None)
df.to_csv(dst)