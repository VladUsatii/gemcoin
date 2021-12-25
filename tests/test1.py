# Testing JSON read struct
import json

add_dict = {'new_key': 'new_value'}

with open('data.txt') as f:
	# getting json read into a variable
	data = json.load(f)

print(data)

# appending to the dictionary
data.update(add_dict)

with open('data.txt', 'w') as f:
	json.dump(data, f)

print(data)
