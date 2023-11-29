from dataclasses import dataclass, field
import string
from reader import Reader as StringReader

WHITESPACE = string.whitespace
STARTS_NUMBER = '-+'+string.digits
VALID_NUMBER = STARTS_NUMBER + 'eE.'
STARTS_IDENTIFIER = string.ascii_letters+'_'
VALID_IDENTIFIER = STARTS_IDENTIFIER + string.digits
VALID_KEY_FUCK = VALID_IDENTIFIER+'/'

@dataclass
class Sect:
	name: str
	props: dict = field(default_factory=dict)
	body:  dict = field(default_factory=dict)

@dataclass
class Constructor:
	name: str
	args: list

strsimplematch = {
	'n': '\n',
	't': '\t',
	'r': '\r',
	'a': '\a',
	'b': '\b',
	'f': '\f',
	'v': '\v',
	'"': '"',
	"'": "'",
	'\\': '\\',
}


# THIS IS AWFUL BAD BAD BAD FFFFFFFFFFFFFFFF
def digest_string (s: str):
	l = len(s)
	i = 0
	outs = ''
	while i < l:
		ch = s[i]
		if ch == '\\':
			i += 1
			assert (ch := s[i:i+1]) != '', 'Unclosed escape seq at end of str'
			if ch in strsimplematch:
				ch = strsimplematch[ch]
			elif ch == 'u':
				i += 1
				assert len(vals:=s[i:i+4]) == 4, 'Need 4 chars for utf16 escape seq'
				ch = chr(int(vals, 16))
				i += 3 # 3 instead of 4, skips total 4 chars at end of loop
			elif ch == 'U':
				i += 1
				assert len(vals:=s[i:i+6]) == 6, 'Need 6 chars for utf32 escape seq'
				ch = chr(int(vals, 16))
				i += 5 # see above
			else:
				assert False, f'Invalid escape sequence \\{ch}'
		outs += ch
		i += 1
	return outs

class GDReader:
	def __init__ (self, src_text:str):
		self.f = StringReader(src_text.replace('\r\n', '\n').replace('\r', '\n'))
		self.sections = list[Sect]()

	def skip_whitespace (self):
		self.f.skip_while(WHITESPACE)

	def read_string (self, matching='"'):
		# assumes beginning " was consumed
		f = self.f
		begin = f.tell()
		has_esc_seq = False
		while (sch:=f.read()) != '':
			if sch == matching:
				if f.peek(-2) == '\\':
					has_esc_seq = True
					continue
				s = f.text[begin:f.tell()-1] # trailing quote excluded
				return digest_string(s) if has_esc_seq else s
		assert False, f'Unclosed string starting at {begin} (hint: {repr(f.text[begin:begin+32])})'

	def read_number (self):
		return float(self.f.vore_while(VALID_NUMBER))

	def read_identifier (self):
		return self.f.vore_while(VALID_IDENTIFIER)

	def read_key (self):
		return self.f.vore_while(VALID_KEY_FUCK)

	def read_key_value (self):
		k = self.read_key()
		self.skip_whitespace()
		assert self.f.vore('='), f'Expected = between key ({k}) and value'
		self.skip_whitespace()
		return k, self.read_value()

	def read_array (self, ending=']', typename='array'):
		outa = []
		f = self.f
		while True:
			self.skip_whitespace()
			if f.vore(ending):
				break
			outa.append(self.read_value())
			self.skip_whitespace()
			if f.vore(','): continue
			if f.vore(ending): break
			assert False, f'Unclosed {typename}'
		return outa

	def read_dict (self):
		f=self.f
		outd = dict()
		while True:
			self.skip_whitespace()
			if f.vore('}'): break
			key = self.read_string()
			self.skip_whitespace()
			assert f.vore(':'), 'Expected :'
			self.skip_whitespace()
			outd[key] = self.read_value()
			self.skip_whitespace()
			if f.vore(','): continue
			if f.vore('}'): break
			assert False, 'Unclosed dict'
		return outd

	def read_value (self):
		f = self.f
		if f.vore('"'): return self.read_string('"')
		if f.vore("'"): return self.read_string("'")
		if f.peek_is(STARTS_NUMBER):
			return self.read_number()
		if f.peek_is(STARTS_IDENTIFIER):
			name = self.read_identifier()
			if   name == 'true':  return True
			elif name == 'false': return False
			elif name == 'null':  return None
			self.skip_whitespace()
			assert f.vore('('), f'Unknown raw identifier {name}'
			args = self.read_array(')', 'constructor args')
			return Constructor(name, args)
		if f.vore('['):
			return self.read_array()
		if f.vore('{'):
			return self.read_dict()
		assert False, f'Unknown value type @{f.tell()}'

	def skip_comment (self):
		self.f.skip_until('\n')
		self.f.skip()

	def read_section_header (self):
		f = self.f
		self.skip_whitespace()
		kc = Sect(self.read_key())
		while True:
			self.skip_whitespace()
			if f.vore(']'):
				break
			if f.peek_is(''):
				assert False, 'Unclosed section header'
			k, v = self.read_key_value()
			kc.props[k] = v
		return kc

	def read (self):
		f = self.f
		current_section: Sect|None = None
		while f.can_read():
			self.skip_whitespace()
			ch = f.read()

			if ch == '[':
				current_section = self.read_section_header()
				self.sections.append(current_section)
				continue
			elif ch == ';':
				self.skip_comment()
				continue
			elif ch == '':
				break
			assert current_section is not None, 'No current section'
			f.rewind()
			k, v = self.read_key_value()
			current_section.body[k] = v
		return self.sections
