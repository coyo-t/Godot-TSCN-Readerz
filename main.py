from dataclasses import dataclass, field
from pathlib import Path
from pprint import pprint

from gd_reader_raw import GDReader

DSKT = Path('D:/_projects/_desktop')
PARA = Path('D:/_projects/parallel2shit/godot/font2')


@dataclass
class Node:
	name:str
	type:str
	instance:object=None
	parent:object=None
	@property
	def is_root (self):
		return self.parent is None
	@property
	def is_scene_instance (self):
		return self.instance is not None

@dataclass
class WipResource:
	type:str
	id:str
	path:str=None
	uid:str=None
	@property
	def is_sub (self):
		return self.path is None


def main2 ():
	text = (PARA/'scenes/_thought2.tscn').read_text('utf8').replace('\r\n', '\n').replace('\r', '\n')
	ss = GDReader(text)

	nodes = list[Node]()
	ext_resources = dict[str, WipResource]()
	sub_resources = dict[str, WipResource]()
	for sect in ss.read():
		# if sect.name == 'node':
		# 	n = Node(sect.get_prop('name'), sect.get_prop('type'))
		# 	if (inst:=sect.get_prop('instance')) is not None:
		# 		n.instance = inst
		# 	if (parent:=sect.get_prop('parent')) is not None:
		# 		n.parent = parent
		# 	nodes.append(n)
		# 	print(n)

		if sect.name == 'ext_resource':
			ext = WipResource(
				sect.get_prop('type'),
				sect.get_prop('id'),
				sect.get_prop('path'),
				sect.get_prop('uid'),
			)
			ext_resources[ext.id] = ext
		elif sect.name == 'sub_resouce':
			sub = WipResource(
				sect.get_prop('type'),
				sect.get_prop('id'),
			)
			sub_resources[sub.id] = sub
		print(sect)
	# for k,v in ext_resources.items():
	# 	print(k, v)
	# for k,v in sub_resources.items():
	# 	print(k, v)


if __name__ == '__main__':
	main2()
