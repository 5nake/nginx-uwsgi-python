#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jinja2 import Template

html = open('/home/user/myapp/static/index.html').read()
template = Template(html)
print(template.render(name=u'Петя'))