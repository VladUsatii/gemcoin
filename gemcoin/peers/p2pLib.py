#!/usr/bin/env python3
from node import Node


# Network event handler
class srcNode(Node):
	def __init__(self, host, port, id=None, callback=None, max_connections=0):
		super(srcNode, self).__init__(host, port, id, callback, max_connections)
		print("gemcoin searching for peers. . .")

	def outbound_node_connected(self, node):
		print("Connected to potential peer.")
        
	def inbound_node_connected(self, node):
		print("inbound_node_connected: (" + self.id + "): " + node.id)

	def inbound_node_disconnected(self, node):
		print("(Inbound) Disconnected from peer.")

	def outbound_node_disconnected(self, node):
		print("(Outbound) Disconnected from peer.")

	def node_message(self, node, data):
		print("node_message (" + self.id + ") from " + node.id + ": " + str(data))
        
	def node_disconnect_with_outbound_node(self, node):
		print("node wants to disconnect with oher outbound node: (" + self.id + "): " + node.id)
        
	def node_request_to_stop(self):
		print("node is requested to stop (" + self.id + "): ")
