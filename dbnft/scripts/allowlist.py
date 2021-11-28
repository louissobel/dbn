import argparse
import json
import os
import os.path
import collections

import boto3
import botocore

parser = argparse.ArgumentParser(description='edit allowlist')
parser.add_argument('--env', required=True)
parser.add_argument('--init', action='store_true')
parser.add_argument('--set', action='append')

args = parser.parse_args()

client = boto3.client('s3')

key = "%s/allowlist_hints.json" % args.env


def get_allowlist():
    obj = client.get_object(Bucket='dbnft', Key=key)
    return json.loads(
        obj['Body'].read().decode('utf-8'),
        object_pairs_hook=collections.OrderedDict,
    )


def store_allowlist(l):
    data = json.dumps(l, indent=2).encode('utf-8') + b"\n"
    client.put_object(Bucket='dbnft', Key=key, Body=data)

def main():
    if args.init:
        print('Initializing %s to {}' % key)
        store_allowlist({})
        return

    current = get_allowlist()

    print(key)

    if args.set:
        for s in args.set:
            k, v = s.split('=')
            print('adding %s: %s' % (k, v))
            current[k] = v
        store_allowlist(current)

    print("%d entries" % len(current))
    print("=============")


    for k, v in current.items():
        print("%s: %s" % (k, v))



main()



