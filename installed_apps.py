#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""Take diags from settings help in Android (probaly iOS too?)

dump out web pages of installed apps and watch faces
"""

import bisect  # TODO consider using https://github.com/grantjenks/python-sortedcontainers instead, py3 and py2 API is the same
import json
import logging
import os
import sys

import stache  # https://github.com/clach04/Stache

import locker2dict


def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' % (sys.version, sys.platform))

    # TODO .gz
    filename = 'locker.log'
    try:
        f = open(filename, 'r', encoding="utf-8")  # open in text (utf-8 encoding) mode to avoid explict decode/encode
    except TypeError:
        # Python 2 hack - not tested properly (look at either io.open() or codecs (py2.5) instead)
        f = open(filename, 'r')
    entries = locker2dict.file2dict(f)
    f.close()
    f.close()
    #print(json.dumps(entries, indent=4))
    all_apps = {
        'watchapp': [],
        'watchface': [],
    }
    for entry_key in entries:
        entry = entries[entry_key]
        """
        if entry['uuid'] not in (
            'af760190-bfc0-11e4-bb52-0800200c9a66'  # Calls
        ):
        """
        if not entry['is_system_app']:
            """
            print(entry['uuid'])
            print(entry['type'])
            #print(entry['title'])  #    Special cases title='UNSUPPORTED WATCHFACES' and title='NOT ON WATCH'
            print(entry['version'])
            print(entry['developer_name'])
            print(entry['share'])
            print(entry['is_reorderable'])
            print(entry['is_sideloaded'])
            print(entry['is_system_app'])
            print(entry['locker_order'])
            print(entry['companion_required'])
            print(entry['companion_url'])
            """
            platform_dependent_data = entry['platform_dependent_data']
            #print(platform_dependent_data)
            supported_platform_dependent_data = {}
            for index_offset, platform_dependent_entry in enumerate(platform_dependent_data):
                if platform_dependent_entry['supported']:
                    supported_platform_dependent_data[platform_dependent_entry['platform']] = index_offset
            entry['supported_platform_dependent_data'] = supported_platform_dependent_data
            pebble_platform_index = 0
            for platform_str in ('basalt', 'aplite', 'chalk'):
                pebble_platform_index_tmp = supported_platform_dependent_data.get(platform_str)
                if pebble_platform_index_tmp:
                    pebble_platform_index = pebble_platform_index_tmp
                    break
            entry['display_platform_dependent_entry'] = platform_dependent_data[pebble_platform_index]
            """
            for platform_dependent_entry in platform_dependent_data:
                if platform_dependent_entry['supported']:
                    print(platform_dependent_entry['platform'])
                    print(platform_dependent_entry['screenshot'])
                    print(platform_dependent_entry['icon_list'])
                    print(platform_dependent_entry['description'])
            """
            #print(entry)
            #all_apps[entry['type']].append(entry)  # # TODO some sort of sort operation, or just shove the whole thing into a sqlite3 db/table
            bisect.insort_left(all_apps[entry['type']], entry, key=lambda x: x['locker_order'] or -1)  # NOTE "key" support in bisect.insort requires Python 3.10 (or a backport?)

    print(json.dumps(all_apps, indent=4))
    #print(json.dumps(all_apps, indent=4).encode('utf-8'))
    print('-' * 65)

    data = all_apps
    # TODO uuid
    # TODO url with pbw download option
    template = u"""
<h2>Apps</h2>
{{#watchapp}}
    <h3>{{title}}</h3>
    Version: {{version}}<br>
    Author: {{developer_name}}<br>
    Sideloaded: {{is_sideloaded}}<br>
    {{^is_sideloaded}}
        <a href="{{{share}}}">{{title}} {{version}}</a><br>
        {{?companion_url}}
        <a href="{{{companion_url}}}">Companion App</a><img src="{{{companion_icon}}}"><br>
        {{/companion_url}}
    {{/is_sideloaded}}
    {{#is_sideloaded}}
    SIDE-LOADED<br>
    {{/is_sideloaded}}
    {{#display_platform_dependent_entry}}
        {{description}}
        <br>
        <img src="{{{screenshot}}}">
    {{/display_platform_dependent_entry}}
{{/watchapp}}
<hr>
<h2>Watchfaces</h2>
{{#watchface}}
    <h3>{{title}}</h3>
    Version: {{version}}<br>
    Author: {{developer_name}}<br>
    Sideloaded: {{is_sideloaded}}<br>
    {{^is_sideloaded}}
        <a href="{{{share}}}">{{title}} {{version}}</a><br>
        {{?companion_url}}
        <a href="{{{companion_url}}}">Companion App</a><img src="{{{companion_icon}}}"><br>
        {{/companion_url}}
    {{/is_sideloaded}}
    {{#is_sideloaded}}
    SIDE-LOADED<br>
    {{/is_sideloaded}}
    {{#display_platform_dependent_entry}}
        {{description}}
        <br>
        <img src="{{{screenshot}}}">
    {{/display_platform_dependent_entry}}
{{/watchface}}
"""
    result = stache.render(template, data)
    #print(repr(result))
    outf = open('out.html' ,'wb')
    outf.write(result.encode('utf-8'))
    outf.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())

