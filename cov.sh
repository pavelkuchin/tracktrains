#!/bin/sh
coverage run --source='.' --omit='*migrations*,*tests*,manage.py' manage.py test
coverage report
