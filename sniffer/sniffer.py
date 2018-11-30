#!/usr/bin/python3
from scapy.all import *
import socket
import json
import time
import requests
import _thread
import argparse


data_list = []
time_old = 0


def enumeration(packet):
	"""
	Enumeration of the packet's layers
	"""
	yield packet.name
	while packet.payload:
		packet =packet.payload
		yield packet.name

# Function from https://stackoverflow.com/questions/5998245/get-current-time-in-milliseconds-in-python
# Epoch milliseconds calculator
epoch_millis = lambda: int(round(time.time() * 1000))


def send(data):
	"""
	Function to send the data to the configured server
	"""
	try:
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		resp = requests.post('http://'+parameters.ip+':'+parameters.port+'/save', data=data, headers=headers)
		return resp.status_code
	except Exception:
		print('conection error')


def parser(packet):
	"""
	Sniff the traffic, store the important metadata and send it to the server
	"""
	global data_list
	global time_old
	dictionary = {}

	# Timestamp identification for Grafana and ElasticSearch
	dictionary['@timestamp'] = epoch_millis()
	layers = ""
	# Agregation of all the packet's layers
	for i in enumeration(packet):
		if i == 'Raw':
			break
		if (layers == ""):
			layers = i
		layers += ',' + i
	dictionary['layers'] = layers

	# Agregation of specific packet's data
	try:
		dictionary['MacOrigen'] = getattr(packet.getlayer('Ethernet'),'src')
		if(packet.getlayer('IP')):
			dictionary['IpOrigen'] = getattr(packet.getlayer('IP'),'src')
			dictionary['IpDestino'] = getattr(packet.getlayer('IP'),'dst')
		if(packet.getlayer('TCP')):
			dictionary['TCPseq'] = getattr(packet.getlayer('TCP'),'seq')
			dictionary['PuertoOrigen'] = getattr(packet.getlayer('TCP'),'sport')
			dictionary['PuertoDestino'] = getattr(packet.getlayer('TCP'),'dport')
		if(packet.getlayer('UDP')):
			dictionary['PuertoOrigen'] = getattr(packet.getlayer('UDP'),'sport')
			dictionary['PuertoDestino'] = getattr(packet.getlayer('UDP'),'dport')

	except Exception as e:
		print(str(e))

	# Json creation and data sending
	json_data = json.dumps(dictionary)
	time = epoch_millis()

	# Data agregation
	data_list.append(json_data)
	if (time_old == 0):
		time_old = time 
	elif ((time - time_old) > parameters.time):
		try:
			# Sending the data to the server API
			_thread.start_new_thread(send,(json.dumps(data_list),))
		except Exception as e:
			print(str(e))
		data_list = []
		time_old = 0


def main():
	# Parsing arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--ip', action='store',
						dest='ip',
						default='127.0.0.1')
	parser.add_argument('--port', action='store',
						dest='port',
						default='5001')
	parser.add_argument('--time', action='store',
						dest='time',
						default=300000, type=int)
	parameters = parser.parse_args()

	# Start Sniffer
	sniff(filter='ip',prn=parser)


if __name__ == "__main__":
	main()
	