# LSystem.py
#
# A parser for L-Systems.
#
# B. Bird - 02/09/2016

import re

class LSystemParseException:
	pass


EVEN_FLAG = '%'
ODD_FLAG = '^'
LHS_pattern = re.compile('^\s*([0-9]+)?\s*([%^]+)?\s*([A-Za-z\[\]])\s*$')


class LSystemRule:
	def __init__(self,rule_string):
		if '=' not in rule_string:
			raise LSystemParseException
		lhs,rhs = (x.strip() for x in rule_string.split('=',1))
		self.substitution = rhs
		lhs_match = LHS_pattern.match(lhs)
		if lhs_match is None:
			raise LSystemParseException
		lifetime, flags, rule_char = lhs_match.groups()
		if lifetime is not None:
			lifetime = int(lifetime)
		if flags is None:
			flags = ''
		self.lifetime = lifetime
		self.flags = flags
		self.rule = rule_char
		

class LSystem:
	def __init__(self, filename):
		self.axiom = None
		self.rules = []
		try:
			f = open(filename)
		except IOError:
			raise LSystemParseException
		for line in f:
			line = line.strip()
			if line == '' or line[0] == '#':
				continue
			if self.axiom is None:
				self.axiom = line
			else:
				self.rules.append( LSystemRule(line) )
		if self.axiom is None:
			raise LSystemParseException
		
		
	def generate_recursive(self, max_iterations, current_iteration, input_string):
		output_string = ''
		for c in input_string:
			if current_iteration < max_iterations:
				found_rule = False
				for rule in self.rules:
					if rule.rule != c:
						continue
					if rule.lifetime is not None:
						if rule.lifetime < 0 and max_iterations+rule.lifetime <= current_iteration:
							continue
						if rule.lifetime > 0 and rule.lifetime < current_iteration:
							continue
					if EVEN_FLAG in rule.flags and (current_iteration%2 == 1):
						continue
					if ODD_FLAG in rule.flags and (current_iteration%2 == 0):
						continue
					found_rule = True
					output_string += self.generate_recursive(max_iterations,current_iteration+1,rule.substitution)
					break
				if found_rule:
					continue
			output_string += c
		return output_string
						
	def generate_system_string(self, iterations):
		return self.generate_recursive(iterations, 0, self.axiom)
	
	
