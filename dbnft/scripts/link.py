import argparse
import json
from collections import deque

parser = argparse.ArgumentParser(description='Link DBN drawing with harness + functions')
parser.add_argument('--drawing', required=True)
parser.add_argument('--harness', required=True)
parser.add_argument('--functions', required=True)
parser.add_argument('--output')

def main():
	args = parser.parse_args()

	with open(args.functions) as f:
		function_data_by_name = json.load(f)


	with open(args.harness) as f:
		harness_data = f.read()

	with open(args.drawing) as f:
		drawing_data = f.read()


	seen = set()
	linkQueue = deque([harness_data, drawing_data])
	output = []

	while linkQueue:
		nextItem = linkQueue.popleft()
		output.append(nextItem)
		links = parse_links(nextItem)

		for link in links:
			if not link in function_data_by_name:
				raise ValueError("No data for linked function %s" % link)
			if not link in seen:
				seen.add(link)
				linkQueue.append(function_data_by_name[link])

	# this.... is a bit of a hack
	# but we want the drawing to be at the end
	# but it's also convenient to have it in the recursive algorithm get
	# handled like the others
	# so..... just pull it out and append it to the end /shrug
	del output[1]
	output.append(drawing_data)

	result = "\n\n".join(output)
	if args.output:
		with open(args.output, "w") as f:
			f.write(result)
	else:
		print(result)


def add_data(function_data_by_name, output, already_added, data):
	output.append(data)

	first_line, *_ = data.split("\n", 1)
	if first_line.startswith(';link:'):
		_, link_list = first_line.split(':', 1)
		if link_list:
			links = link_list.split(',')
			for link in links:
				try:
					data = function_data_by_name[link]
				except KeyError:
					raise ValueError("No data for linked function %s" % link)

				if not link in already_added:
					already_added.add(link)
					add_data(function_data_by_name, output, already_added, data)


def parse_links(data):
	first_line, *_ = data.split("\n", 1)
	if first_line.startswith(';link:'):
		_, link_list = first_line.split(':', 1)
		if link_list:
			return link_list.split(',')
	return []


if __name__ == '__main__':
	main()
