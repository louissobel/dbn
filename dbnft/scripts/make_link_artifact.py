import argparse
import json
import os.path

parser = argparse.ArgumentParser(description='Generate function --> data json blob')
parser.add_argument('file', nargs='+')
parser.add_argument('--output')

args = parser.parse_args()

output = {}
for path in args.file:
	functionName, _ = os.path.splitext(os.path.basename(path))
	if functionName in output:
		raise ValueError("duplicate function %s" % functionName)
	with open(path) as f:
		output[functionName] = f.read()

result = json.dumps(output, indent=2)

if args.output:
	with open(args.output, 'w') as f:
		f.write(result)
else:
	print(result)
