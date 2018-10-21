from abc import ABCMeta, abstractmethod
class Intent(object):


	def __init__(self, name, params, action):
		self.name = name
		self.action = action
		#print("name=", self.name)
		#print("action=", self.action)

		self.params = []
		for param in params:
			# print param['required']
			self.params += [Parameter(param)]

class Parameter():
	def __init__(self, info):
		self.name = info['name']
		#print("calss param name=", self.name)
		self.placeholder = info['placeholder']
		self.prompts = info['prompts']
		self.required = info['required']
		self.context = info['context']
