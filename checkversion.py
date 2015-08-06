#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

def application(environ, start_response):
	start_response('200 OK', [('Content-Type', 'text/html')])
	return [sys.version]
