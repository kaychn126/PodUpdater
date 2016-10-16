#!/usr/bin/env python3

import os,sys
##get log message

logmsglist = os.popen("git log -1 HEAD --pretty=format:%s").readlines()

podpush = "--pod-push"

for line in logmsglist:
	lowerline = line.lower()
	if lowerline.find(podpush) > 0:
		print("have " + podpush)
