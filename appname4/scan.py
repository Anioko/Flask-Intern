#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
from flask.ext.script import Manager
from appname4 import app, db, lm
from appname4.models import Movie, Subtitle

import time
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
