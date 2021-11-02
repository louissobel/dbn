from . import ast_nodes
from .token import DBNToken

class ParseError(ValueError):
	def __init__(self, message, line, char):
		super().__init__(message)

		self.message = message
		self.line = line
		self.char = char
