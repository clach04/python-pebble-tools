#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""Take diags from settings help in Android (probaly iOS too?)

dump out web pages of installed apps and watch faces
"""

import json
import logging
import os
import pprint
#import shlex
import sys


logging.basicConfig() ## NO debug, no info. But logs warnings
log = logging.getLogger("locker2dict")
#log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)

def coerce_type(key, value):
    if value == 'null':
        return None
    elif key.startswith('is_') or key in ('companion_required'):
        # assume bool:
        if value == '0':
            return False
        elif value == '1':
            return True
        else:
            raise NotImplementedError('Bool %r = %r' % (key, value))
    elif key in ('locker_order'):
        return int(value)
    else:
        return value

def file2dict(f):
    # read in from file object `f` returning a dict of contents
    # where `f` is being read from a locker.log from inside of a pebble.log.gz (which is a zip file with misleading file name)
    log.debug('f %r', f)
    entries = {}
    reading_entry = False
    temp_dict = {}
    for line in f:
        log.debug('raw line %r', line)
        line = line.strip()
        if line.endswith('{'):
            # start of new entry, don't care what number it is
            reading_entry = True
            temp_dict = {}
        elif line == '}':
            # end of new entry, stow it away
            reading_entry = False
            #key = temp_dict['locker_order']  # can't use - there are many locker_order=0 entries
            key = temp_dict['_id']
            assert key not in entries, key
            if temp_dict['platform_dependent_data']:
                temp_dict['platform_dependent_data'] = json.loads(temp_dict['platform_dependent_data'])
            entries[key] = temp_dict
        else:
            if reading_entry:
                log.debug('reading_entry %r', line)
                key, value = line.split('=', 1)  # NOTE all entries are string; key and value (even "null", zero, one, etc.)
                value = coerce_type(key, value)
                temp_dict[key] = value
    return entries


def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' % (sys.version, sys.platform))
    log.info('Python %s on %s', sys.version, sys.platform)

    filename = 'locker.log'
    try:
        f = open(filename, 'r', encoding="utf-8")  # open in text (utf-8 encoding) mode to avoid explict decode/encode
    except TypeError:
        # Python 2 hack - not tested properly (look at either io.open() or codecs (py2.5) instead)
        f = open(filename, 'r')
    entries = file2dict(f)
    f.close()
    f.close()
    #pprint.pprint(entries)
    print(json.dumps(entries, indent=4))

    return 0


if __name__ == "__main__":
    sys.exit(main())