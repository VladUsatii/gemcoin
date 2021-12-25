import socket
import time
import threading
import random
import hashlib

from nodeconnection import NodeConnection

class Node(threading.Thread):
	def __init__(self, host, port, id=None, callback=None, max_connections=0):
		super(Node, self).__init__()

		# FLAGS
		self.TERMINATE = threading.Event()

		self.host = host
		self.port = port
		self.callback = callback

		self.nodes_inbound = []  # Nodes that are connect with us N->(US)
		self.nodes_outbound = []  # Nodes that we are connected to (US)->N
		self.reconnect_to_nodes = []

		if id == None:
			self.id = self.dhke()
		else:
			self.id = str(id)

		self.connected_node_ids = []

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.init_server()

		self.message_count_send = 0
		self.message_count_recv = 0
		self.message_count_rerr = 0
        
		self.max_connections = max_connections

		self.debug = True

	@property
	def all_nodes(self):
		return self.nodes_inbound + self.nodes_outbound

	def debug_print(self, message):
		if self.debug: print("INFO (" + self.id[0] + "): " + message)

	def dhke(self):
		""" Generate a D-H key for symmetric encryption of packets """
		GEN, MOD = 9, 37
		host_rand_num = int(random.random()*1000)

		# [src diffie hellman key, host randum number]
		return [str((GEN**host_rand_num) % MOD), host_rand_num]

	def dhkey(self, y, x):
		# y = dest exchange
		# x = host random number
		MOD = 37
		return str((int(y)**x) % MOD)

	def init_server(self):
		print("Initialisation of the Node on port: " + str(self.port) + " on node (" + self.id[0] + ")")
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))
		self.sock.settimeout(10.0)
		self.sock.listen(1)

	def print_connections(self):
		print("Node connection overview:")
		print("- Total nodes connected with us: %d" % len(self.nodes_inbound))
		print("- Total nodes connected to     : %d" % len(self.nodes_outbound))

	def send_to_nodes(self, data, exclude=[]):
		self.message_count_send = self.message_count_send + 1
		for n in self.nodes_inbound:
			if n in exclude:
				self.debug_print("Node send_to_nodes: Excluding node in sending the message")
			else:
				self.send_to_node(n, data)

		for n in self.nodes_outbound:
			if n in exclude:
				self.debug_print("Node send_to_nodes: Excluding node in sending the message")
			else:
				self.send_to_node(n, data)

	def send_to_node(self, n, data):
		self.message_count_send = self.message_count_send + 1
		if n in self.nodes_inbound or n in self.nodes_outbound:
			n.send(data)
		else:
			self.debug_print("Node send_to_node: Could not send the data, node is not found!")

	def connect_with_node(self, host, port, reconnect=False):
		if host == self.host and port == self.port:
			print("connect_with_node: Cannot connect with yourself!!")
			return False
		for node in self.nodes_outbound:
			if node.host == host and node.port == port:
				print("connect_with_node: Already connected with this node (" + node.id[0] + ").")
				return True

		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.debug_print("connecting to %s port %s" % (host, port))
			sock.connect((host, port))

			sock.send(self.id[0].encode('utf-8'))
			connected_node_id = sock.recv(4096).decode('utf-8')

			print(connected_node_id)
			self.connected_node_ids.append(connected_node_id)

			session_key = self.dhkey(connected_node_id, self.id[1])
			print(f"\n\nSESSION KEY FOR {host}: {session_key}\n\n")

			if self.id == connected_node_id:
				print("connect_with_node: You cannot connect with yourself?!")
				sock.send("CLOSING: Already having a connection together".encode('utf-8'))
				sock.close()
				return True

			for node in self.nodes_inbound:
				if node.host == host and node.id == connected_node_id:
					print("connect_with_node: This node (" + node.id[0] + ") is already connected with us.")
					sock.send("CLOSING: Already having a connection together".encode('utf-8'))
					sock.close()
					return True

			thread_client = self.create_new_connection(sock, connected_node_id, host, port)
			thread_client.start()

			self.nodes_outbound.append(thread_client)
			self.outbound_node_connected(thread_client)

			"""
			if reconnect:
				self.debug_print("connect_with_node: Reconnection check is enabled on node " + host + ":" + str(port))
				self.reconnect_to_nodes.append({"host": host, "port": port, "tries": 0})
				return True
			"""
			return thread_client
		except ConnectionRefusedError:
			self.debug_print("TcpServer.connect_with_node: Can't establish a communication with an idle node.")
			return False
		except Exception as e:
			self.debug_print("TcpServer.connect_with_node: Could not connect with node. (" + str(e) + ")")
			return False

	def disconnect_with_node(self, node):
		if node in self.nodes_outbound:
			self.node_disconnect_with_outbound_node(node)
			node.stop()
		else:
			self.debug_print("Node disconnect_with_node: cannot disconnect with a node with which we are not connected.")

	def stop(self):
		self.node_request_to_stop()
		self.TERMINATE.set()

	def create_new_connection(self, connection, id, host, port):
		return NodeConnection(self, connection, id, host, port)

	def reconnect_nodes(self):
		for node_to_check in self.reconnect_to_nodes:
			found_node = False
			self.debug_print("reconnect_nodes: Checking node " + node_to_check["host"] + ":" + str(node_to_check["port"]))

			for node in self.nodes_outbound:
				if node.host == node_to_check["host"] and node.port == node_to_check["port"]:
					found_node = True
					node_to_check["trials"] = 0 # Reset the trials
					self.debug_print("reconnect_nodes: Node " + node_to_check["host"] + ":" + str(node_to_check["port"]) + " still running!")

			if not found_node: # Reconnect with node
				node_to_check["trials"] += 1
				if self.node_reconnection_error(node_to_check["host"], node_to_check["port"], node_to_check["trials"]):
					self.connect_with_node(node_to_check["host"], node_to_check["port"]) # Perform the actual connection
				else:
					self.debug_print("reconnect_nodes: Removing node (" + node_to_check["host"] + ":" + str(node_to_check["port"]) + ") from the reconnection list!")
					self.reconnect_to_nodes.remove(node_to_check)

	def run(self):
		while not self.TERMINATE.is_set():  # Check whether the thread needs to be closed
			try:
				self.debug_print("Node: Wait for incoming connection")
				connection, client_address = self.sock.accept()

				self.debug_print("Total inbound connections:" + str(len(self.nodes_inbound)))
				if self.max_connections == 0 or len(self.nodes_inbound) < self.max_connections:
					connected_node_id = connection.recv(4096).decode('utf-8') # When a node is connected, it sends it id!
					connection.send(self.id[0].encode('utf-8')) # Send my id to the connected node!

					thread_client = self.create_new_connection(connection, connected_node_id, client_address[0], client_address[1])
					thread_client.start()

					self.nodes_inbound.append(thread_client)
					self.inbound_node_connected(thread_client)

				else:
					self.debug_print("New connection is closed. You have reached the maximum connection limit!")
					connection.close()
            
			except socket.timeout:
				self.debug_print('Node: Connection timeout!')
			except Exception as e:
				raise e

			self.reconnect_nodes()
			time.sleep(0.01)

		print("Node stopping...")
		for t in self.nodes_inbound:
			t.stop()
		for t in self.nodes_outbound:
			t.stop()

		time.sleep(1)

		for t in self.nodes_inbound:
			t.join()
		for t in self.nodes_outbound:
			t.join()

		self.sock.settimeout(None)   
		self.sock.close()
		print("Node stopped")

	def outbound_node_connected(self, node):
		self.debug_print("outbound_node_connected: " + node.id[0])
		if self.callback is not None:
			self.callback("outbound_node_connected", self, node, {})

	def inbound_node_connected(self, node):	
		"""
		Node has connected to you

		Synchronizes to the nearest ten seconds and attempts verification of the node.
		"""
		key = self.dhkey(int(self.connected_node_ids[-1]), int(self.id[1]))
		print(f"\n\nInbound key: {key}\n\n")

		node = (str(self.nodes_inbound[-1:].host), int(self.nodes_inbound[-1:].port))
		self.connect_with_node(node)
		print("Connected with node")

		# sync connection 
		current_time = int(datetime.now().strftime("%S"))
		next_10_seconds = roundup(current_time)
		while int(datetime.now().strftime("%S")) != next_10_seconds:
			print("Waiting for synchronization. . .")
			sys.stdout.write("\033[F")

		self.debug_print("inbound_node_connected: " + node.id[0])
		if self.callback is not None:
			self.callback("inbound_node_connected", self, node, {})

	def node_disconnected(self, node):
		self.debug_print("node_disconnected: " + node.id[0])

		if node in self.nodes_inbound:
			del self.nodes_inbound[self.nodes_inbound.index(node)]
			self.inbound_node_disconnected(node)

		if node in self.nodes_outbound:
			del self.nodes_outbound[self.nodes_outbound.index(node)]
			self.outbound_node_disconnected(node)

	def inbound_node_disconnected(self, node):
		self.debug_print("inbound_node_disconnected: " + node.id[0])
		if self.callback is not None:
			self.callback("inbound_node_disconnected", self, node, {})

	def outbound_node_disconnected(self, node):
		self.debug_print("outbound_node_disconnected: " + node.id[0])
		if self.callback is not None:
			self.callback("outbound_node_disconnected", self, node, {})

	def node_message(self, node, data):
		self.debug_print("node_message: " + node.id[0] + ": " + str(data))
		if self.callback is not None:
			self.callback("node_message", self, node, data)

	def node_disconnect_with_outbound_node(self, node):
		self.debug_print("node wants to disconnect with oher outbound node: " + node.id[0])
		if self.callback is not None:
			self.callback("node_disconnect_with_outbound_node", self, node, {})

	def node_request_to_stop(self):
		self.debug_print("node is requested to stop!")
		if self.callback is not None:
			self.callback("node_request_to_stop", self, {}, {})

	def node_reconnection_error(self, host, port, trials):
		self.debug_print("node_reconnection_error: Reconnecting to node " + host + ":" + str(port) + " (trials: " + str(trials) + ")")
		return True

	def __str__(self):
		return 'Node: {}:{}'.format(self.host, self.port)
	def __repr__(self):
		return '<Node {}:{} id: {}>'.format(self.host, self.port, self.id[0])
