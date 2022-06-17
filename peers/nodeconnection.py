import socket
import time
import threading
import json

from packerfuncs import *

class NodeConnection(threading.Thread):
	def __init__(self, main_node, sock, id, host, port):
		super(NodeConnection, self).__init__()

		self.host = host
		self.port = port
		self.main_node = main_node
		self.sock = sock
		self.terminate_flag = threading.Event()

		self.id = id
		self.EOT_CHAR = 0x04.to_bytes(1, 'big')
		self.info = {}

		self.sock.settimeout(10.0)

		self.main_node.debug_print("NodeConnection.send: Started with client (" + self.id[0] + ") '" + self.host + ":" + str(self.port) + "'")

	def send(self, data, encoding_type='utf-8'):
		if isinstance(data, str):
			try:
				self.sock.sendall(data.encode(encoding_type) + self.EOT_CHAR)
			except Exception as e:
				self.main_node.debug_print("nodeconnection send: Error sending data to node: " + str(e))
				self.stop()

		elif isinstance(data, dict):
			try:
				json_data = json.dumps(data)
				json_data = json_data.encode(encoding_type) + self.EOT_CHAR
				self.sock.sendall(json_data)
			except TypeError as type_error:
				self.main_node.debug_print('This dict is invalid')
				self.main_node.debug_print(type_error)
			except Exception as e:
				self.main_node.debug_print("nodeconnection send: Error sending data to node: " + str(e))
				self.stop()

		elif isinstance(data, bytes):
			bin_data = data + self.EOT_CHAR
			self.sock.sendall(bin_data)
		else:
			self.main_node.debug_print('datatype used is not valid plese use str, dict (will be send as json) or bytes')

	def stop(self):
		self.terminate_flag.set()

	def parse_packet(self, packet):
		try:
			packet_decoded = packet.decode('utf-8')

			try:
				return json.loads(packet_decoded)

			except json.decoder.JSONDecodeError:
				return packet_decoded

		except UnicodeDecodeError:
			return packet

	def run(self):
		buffer = b'' # Hold the stream that comes in!

		while not self.terminate_flag.is_set():
			chunk = b''

			try:
				chunk = self.sock.recv(4096)

			except socket.timeout:
				self.main_node.debug_print("NodeConnection: timeout")

			except Exception as e:
				self.terminate_flag.set() # Exception occurred terminating the connection
				self.main_node.debug_print('Unexpected error')
				self.main_node.debug_print(e)

			if chunk != b'':
				buffer += chunk
				eot_pos = buffer.find(self.EOT_CHAR)
				print(buffer)

				while eot_pos > 0:
					packet = buffer[:eot_pos]
					buffer = buffer[eot_pos + 1:]

					self.main_node.message_count_recv += 1
					self.main_node.node_message(self, self.parse_packet(packet))

					eot_pos = buffer.find(self.EOT_CHAR)

			time.sleep(0.01)

		self.sock.settimeout(None)
		self.sock.close()
		self.main_node.node_disconnected(self)
		self.main_node.debug_print("NodeConnection: Stopped")

	def set_info(self, key, value):
		self.info[key] = value

	def get_info(self, key):
		return self.info[key]

	def __str__(self):
		return 'NodeConnection: {}:{} <-> {}:{} ({})'.format(self.main_node.host, self.main_node.port, self.host, self.port, self.id[0])
	def __repr__(self):
		return '<NodeConnection: Node {}:{} <-> Connection {}:{}>'.format(self.main_node.host, self.main_node.port, self.host, self.port)
