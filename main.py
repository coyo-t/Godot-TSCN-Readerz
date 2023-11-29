from dataclasses import dataclass, field
from json import JSONDecoder
from pathlib import Path
import string
from reader import Reader as StringReader
from pprint import pprint

DSKT = Path('D:/_projects/_desktop')
PARA = Path('D:/_projects/parallel2shit/godot/font2')

@dataclass
class Sect:
	name: str
	props: dict = field(default_factory=dict)
	body: dict = field(default_factory=dict)

@dataclass
class Constructor:
	name: str
	args: list

def main2 ():
	text = (PARA/'scenes/_thought2.tscn').read_text('utf8').replace('\r\n', '\n').replace('\r', '\n')
	f = StringReader(text)

	WHITESPACE = string.whitespace
	STARTS_NUMBER = '-+'+string.digits
	VALID_NUMBER = STARTS_NUMBER + 'eE.'
	STARTS_IDENTIFIER = string.ascii_letters+'_'
	VALID_IDENTIFIER = STARTS_IDENTIFIER + string.digits
	VALID_KEY_FUCK = VALID_IDENTIFIER+'/'
	def skip_whitespace ():
		f.skip_while(WHITESPACE)

	def read_string (matching='"'):
		# assumes beginning " was consumed
		begin = f.tell()
		while (sch:=f.read()) != '':
			if sch == matching:
				if f.peek(-2) == '\\':
					continue
				return f.text[begin:f.tell()-1] # trailing quote excluded
		assert False, f'Unclosed string starting at {begin} (hint: {repr(f.text[begin:begin+32])})'

	def read_number ():
		return float(f.vore_while(VALID_NUMBER))

	def read_identifier ():
		return f.vore_while(VALID_IDENTIFIER)

	def read_key ():
		return f.vore_while(VALID_KEY_FUCK)

	def read_key_value ():
		k = read_key()
		skip_whitespace()
		assert f.vore('='), f'Expected = between key ({k}) and value'
		skip_whitespace()
		return k, read_value()

	def read_array (ending=']', typename='array'):
		outa = []
		while True:
			skip_whitespace()
			if f.vore(ending):
				break
			outa.append(read_value())
			skip_whitespace()
			if f.vore(','): continue
			if f.vore(ending): break
			assert False, f'Unclosed {typename}'
		return outa

	def read_dict ():
		outd = dict()
		while True:
			skip_whitespace()
			if f.vore('}'): break
			key = read_string()
			skip_whitespace()
			assert f.vore(':'), 'Expected :'
			skip_whitespace()
			outd[key] = read_value()
			skip_whitespace()
			if f.vore(','): continue
			if f.vore('}'): break
			assert False, 'Unclosed dict'
		return outd

	def read_value ():
		if f.vore('"'):
			return read_string()
		if f.peek_is(STARTS_NUMBER):
			return read_number()
		if f.peek_is(STARTS_IDENTIFIER):
			name = read_identifier()
			if   name == 'true':  return True
			elif name == 'false': return False
			elif name == 'null':  return None
			skip_whitespace()
			assert f.vore('('), f'Unknown raw identifier {name}'
			args = read_array(')', 'constructor args')
			return Constructor(name, args)
		if f.vore('['):
			return read_array()
		if f.vore('{'):
			return read_dict()
		assert False, f'Unknown value type @{f.tell()}'

	def skip_comment ():
		f.skip_until('\n')
		f.skip()

	sections = []
	current_section = None
	def read_section_header ():
		skip_whitespace()
		kc = Sect(read_key())
		while True:
			skip_whitespace()
			if f.vore(']'):
				break
			if f.peek_is(''):
				assert False, 'Unclosed section header'
			k, v = read_key_value()
			kc.props[k] = v
		return kc

	while f.can_read():
		skip_whitespace()
		ch = f.read()

		if ch == '[':
			current_section = read_section_header()
			sections.append(current_section)
			continue
		elif ch == ';':
			skip_comment()
			continue
		elif ch == '':
			break
		assert current_section is not None, 'No current section'
		f.rewind()
		k, v = read_key_value()
		current_section.body[k] = v

	for sect in sections:
		print(sect.name)
		pprint(sect.body)



if __name__ == '__main__':
	main2()
