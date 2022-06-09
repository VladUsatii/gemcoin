import binascii
import codecs
import socket
import time
import threading
import random
import hashlib
import subprocess
import dbm
from pathlib import Path

from nodeconnection import NodeConnection

from serialization import *
from packerfuncs import * # pack() and unpack() for data-link layer

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.prompt.color import Color
from gemcoin.prompt.errors import *
from gemcoin.symmetric import AES_byte_exchange
from gemcoin.wallet.keygenerator import Wallet

class Node(threading.Thread):
	def __init__(self, host, port, id=None, callback=None, max_connections=0):
		super(Node, self).__init__()

		self.VERSION = self.git_revision_hash()
		self.VERACK = False

		# FLAGS
		self.TERMINATE = threading.Event()

		self.task_args = []

		self.host = host
		self.port = port
		self.callback = callback

		# block information from cache
		self.latest_block_number = 0
		self.latest_block_hash   = ""

		self.nodes_inbound = []  # Nodes that are connected with us N->(US)
		self.nodes_outbound = []  # Nodes that we are connected to (US)->N
		self.reconnect_to_nodes = []

		self.region = self.getRegion()

		self.connected = 0
		self.tried     = 0
		self.banned    = 0

		# attempts to quit
		self.attempted = 0

		if id == None:
			self.id = self.dhke()
		else:
			self.id = str(id)

		self.client_dict = {0: "full_node", 1: "full_node_less", 2: "full_node_less_headersonly", 3: "light_node", 4: "light_node_less", 5: "light_node_less_headersonly", 6: "less_client", 7: "less_client_noheaders", 8: "spectator"}
		self.node_type = self.node_type()
		self.node_num = str([key for key, value in self.client_dict.items() if value == self.node_type][0])

		self.connected_node_ids = []

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.init_server()

		self.message_count_send = 0
		self.message_count_recv = 0
		self.message_count_rerr = 0

		self.max_connections = max_connections

		self.debug = True

	def getRegion(self):
		"""
		import urllib.request as regioner
		import requests
		import json

		external_ip = regioner.urlopen('https://ident.me').read().decode('utf8')
		response = requests.get(f"https://geolocation-db.com/json/{external_ip}&position=true").json()

		return "\n" + json.dumps(response, indent=4, sort_keys=False)
		"""
		return "None"

	@property
	def all_nodes(self):
		return self.nodes_inbound + self.nodes_outbound

	def debug_print(self, message):
		if self.debug:
			info(f"({self.node_num}) {message}")

	def incrementAttempts(self, increment: int):
		self.attempted += increment
		if self.attempted < 10:
			warning(f"Panic more to force quit.   {Color.YELLOW}attempts{Color.END}={self.attempted}")
		else:
			sys.exit(0)

	def addTask(self, tasks: list):
		self.task_args += tasks

	def node_type(self):
		try:
			arg = int(sys.argv[1])
			if arg in range(0,8):
				return self.client_dict[arg]
			else:
				return self.client_dict[8]
		except IndexError:
			return self.client_dict[8]
		except Exception as e:
			panic("Invalid node type. Use a number from 0-8; please do research before entering one of these numbers.")

	def mapPublicAddr(self, priv_key: str):
		pub = Wallet.nonstatic_private_to_public(priv_key)
		addr = Wallet.nonstatic_public_to_address(pub)
		return addr

	def dhke(self):
		""" Generate a D-H key for symmetric encryption of packets """
		GEN, MOD = 9, 37
		host_rand_num = int(random.random()*1000)

		basic_id = [str((GEN**host_rand_num) % MOD), str(host_rand_num), self.VERSION]

		# add private key if it exists
		curdir = Path(__file__).resolve().parents[1]
		if os.path.isfile(f'{curdir}/priv_key_store.db'):
			with dbm.open(f'{curdir}/priv_key_store', 'r') as db:
				# candidate key
				candidate_key = db['priv_key']
				# check if valid hash
				if len(candidate_key)*4 != 256:
					panic("You have a fake key. Use SHA256 to generate a secure private key. Import must be in WIF format.")
					self.stop()
				else:
					# map private key to public key via node function
					full_pub_addr = self.mapPublicAddr(db['priv_key'])

					# append public key to ID
					basic_id.append(full_pub_addr)

					print(info(f"(DHKey) {basic_id[0]}", returner=True) + "     " + info(f"(DHKeyOutput) {basic_id[1]}", returner=True))
					print(version(str(basic_id[2])[:8] + "..", returner=True)           + "                  " + info(f"(PublicAddress) {full_pub_addr}", returner=True))
		else:
			panic("You don't have a private key.")

		return basic_id

	def dhkey(self, y, x):
		# y = dest exchange
		# x = host random number
		MOD = 37
		return str((int(y)**int(x)) % MOD)

	def git_revision_hash(self) -> str:
		return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

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

	# runs when a node connects to another node
	def connect_with_node(self, host, port, reconnect=False):
		if host == self.host and port == self.port:
			panic("Another node is using the same gemaddress. Change your private key now. Disconnecting.")
			return False
		for node in self.nodes_outbound:
			if node.host == host and node.port == port:
				panic("connect_with_node: Already connected with this node (" + node.id[0] + ").")
				return True

		try:
			# init the connection
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((host, port))

			# serialize the id (rlp) & send
			payload = pack(self.id)
			sock.send(payload)

			# wait to receive the id
			connected_node_id = sock.recv(4096)

			# deserialize the id (rlp)
			connected_node_id = unpack(connected_node_id)

			print(connected_node_id)

			self.connected_node_ids.append(connected_node_id)

			if self.id[0:1] == connected_node_id[0:1]:
				print("connect_with_node: You cannot connect with yourself.")
				sock.send("CLOSING: Already having a connection together".encode('utf-8'))
				sock.close()
				return True

			if self.id[2] == connected_node_id[2]:
				# check if node is connecting twice
				if self.VERACK is not True:
					self.VERACK = True
				else:
					panic("(UntrustworthyNode) Disconnecting.")
					sock.send("ERROR: Sent version message twice".encode('utf-8'))
					sock.close()
			else:
				panic("Github version is incompatible. Try a git pull.")
				sock.close()
				return True

			for node in self.nodes_inbound:
				if node.host == host and node.id[2] == connected_node_id[2]:
					print("connect_with_node: This node (" + node.id[0] + ") is already connected with us.")
					sock.send("CLOSING: Already having a connection together".encode('utf-8'))
					sock.close()
					return True

			thread_client = self.create_new_connection(sock, connected_node_id, host, port)
			thread_client.start()

			self.nodes_outbound.append(thread_client)
			self.outbound_node_connected(thread_client)

			self.connected += 1
			self.tried += 1

			return thread_client
		except ConnectionRefusedError:
			self.tried += 1
			info(f"Connecting to nearby peers               {Color.GREEN}connected{Color.END}={self.connected} {Color.GREEN}attempted{Color.END}={self.tried} {Color.GREEN}banned{Color.END}={self.banned}")
			return False
		except Exception as e:
			self.tried += 1
			info(f"Connecting to nearby peers               {Color.GREEN}connected{Color.END}={self.connected} {Color.GREEN}attempted{Color.END}={self.tried} {Color.GREEN}banned{Color.END}={self.banned}")
			return False

	def disconnect_with_node(self, node):
		if node in self.nodes_outbound:
			self.node_disconnect_with_outbound_node(node)
			node.stop()
			self.connected -= 1
			self.VERACK = False
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
				self.debug_print(f"(VERBOSE) Searching Region: {self.region}")
				connection, client_address = self.sock.accept()

				self.debug_print("Total inbound connections:" + str(len(self.nodes_inbound)))
				if self.max_connections == 0 or len(self.nodes_inbound) < self.max_connections:

					connected_node_id = connection.recv(4096) # When a node is connected, it sends it id!
					connected_node_id = unpack(connected_node_id)

					payload = pack(self.id)
					connection.send(payload) # Send my id to the connected node!

					thread_client = self.create_new_connection(connection, connected_node_id, client_address[0], client_address[1])
					thread_client.start()

					self.nodes_inbound.append(thread_client)
					self.inbound_node_connected(thread_client)

				else:
					self.debug_print("New connection is closed. You have reached the maximum connection limit!")
					connection.close()

			except socket.timeout:
				self.tried += 1
				info(f"Connecting to nearby peers               {Color.GREEN}connected{Color.END}={self.connected} {Color.GREEN}attempted{Color.END}={self.tried} {Color.GREEN}banned{Color.END}={self.banned}")
			except Exception as e:
				self.tried += 1
				info(f"Connecting to nearby peers               {Color.GREEN}connected{Color.END}={self.connected} {Color.GREEN}attempted{Color.END}={self.tried} {Color.GREEN}banned{Color.END}={self.banned}")
				raise e

			self.reconnect_nodes()
			time.sleep(0.01)

		info("Node stopping...")
		total_sockets = len(self.nodes_inbound) + len(self.nodes_outbound)
		for t in self.nodes_inbound:
			t.stop()
		for t in self.nodes_outbound:
			t.stop()

		info(f"All connected nodes are now disconnected. Closing {Color.GREEN}{total_sockets}{Color.END} socket threads.")
		time.sleep(1)

		for t in self.nodes_inbound:
			t.join()
		for t in self.nodes_outbound:
			t.join()

		self.sock.settimeout(None)
		self.sock.close()
		info("Node stopped")

	def outbound_node_connected(self, node):
		"""
		You have connected to node
		"""
		self.connected += 1
		self.debug_print("outbound_node_connected: " + self.node_num)
		if self.callback is not None:
			self.callback("outbound_node_connected", self, node, {})

	def inbound_node_connected(self, node):	
		"""
		Node has connected to you

		Synchronizes to the nearest ten seconds and attempts verification of the node.
		"""
		key = self.dhkey(int(self.connected_node_ids[-1][0]), int(self.id[1]))
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
			self.verifyNode((node.host, node.port))

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
		self.debug_print("node wants to disconnect with outbound node: " + node.id[0])
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
