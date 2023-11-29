from dataclasses import dataclass, field
from pathlib import Path
from pprint import pprint

from gd_reader_raw import GDReader

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
	ss = GDReader(text)


	for sect in ss.read():
		print(sect.name)
		pprint(sect.body)



if __name__ == '__main__':
	main2()
