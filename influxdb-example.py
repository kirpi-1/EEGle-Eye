import os
from influxdb_client import InfluxDBClient, Point, Dialect
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np

token = os.environ['INFLUX_TOKEN']
bucket = "test-bucket"
org = "Insight"
client = InfluxDBClient(url="http://localhost:9999",token=token,org="Insight")
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()



def line_protocol(name,timestamp,value):
	return "{} timestamp={},value={}".format(name,timestamp,value)


time = np.arange(0,5,1/100)
x = np.cos(2*np.pi*3*time)
lp =""
for idx,t in enumerate(time):
	lp = lp+line_protocol("cos",t,x[idx])+"\n"
write_api.write(org=org,bucket=bucket, record = lp)

