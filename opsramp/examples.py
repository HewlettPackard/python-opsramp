#!/usr/bin/env python
#
# Exercise the opsramp module as an illustration of how to use it.
#
# (c) Copyright 2019 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import os

import opsramp.binding
import opsramp.rba
import opsramp.msp


CATEGORY_NAME = 'Testing 123'


def main():
    OPSRAMP_URL = os.environ.get('OPSRAMP_URL')
    TENANT_ID = os.environ.get('OPSRAMP_TENANT_ID')
    KEY = os.environ.get('OPSRAMP_KEY')
    SECRET = os.environ.get('OPSRAMP_SECRET')

    ormp = opsramp.binding.connect(OPSRAMP_URL, KEY, SECRET)

    # Print some random global "stuff" just to show that we can.
    cfg = ormp.config()
    print('alert types', cfg.get_alert_types())
    print('channels', cfg.get_channels())
    print('countries', len(cfg.get_countries()))
    print('timezones', len(cfg.get_timezones()))
    print('alert technologies', len(cfg.get_alert_technologies()))
    print('nocs', len(cfg.get_nocs()))
    print('device types', len(cfg.get_device_types()))

    # Focus on a specific tenant.
    tenant = ormp.tenant(TENANT_ID)

    print('List the integrations on tenant', TENANT_ID)
    ints = tenant.integrations()
    group = ints.types()
    found = group.search()
    print(found['totalResults'], 'integration types')
    for i in found['results']:
        print(i)

    print('Define a new custom integration on', TENANT_ID)
    newtype = 'OAUTH2'
    newcint = ints.mkCustom(
        display_name='Example %s integration' % newtype,
        inbound_auth_type=newtype
    )
    print(newcint)
    # uncomment these lines to actually create the integration.
    # resp = ints.create_instance('CUSTOM', newcint)
    # if 'inboundConfig' in resp:
    #     for creds in resp['inboundConfig']['authentication']['apiKeyPairs']:
    #         for i in creds.keys():
    #             creds[i] = 'REDACTED'
    # print(resp)

    group = ints.instances()
    found = group.search()
    print(found['totalResults'], 'integration instances')
    # "found" contains a complete description of each integration but let's
    # pull them individually anyway and assert that this gives same result.
    for i in found['results']:
        print('...', i['id'], i['integration']['id'],
              '"' + i.get('displayName', '<no name>') + '"')
        ithis = ints.instance(i['id'])
        direct = ithis.get()
        assert direct == i

    # Retrieve the agent installation script for this client. The string
    # that OpsRamp returns will contain keys for the client so just print
    # its length and first line to show that we got something.
    if tenant.is_client():
        print('agent installation script for client', TENANT_ID)
        agent_script = tenant.get_agent_script()
        print('length', len(agent_script))
        print(agent_script.split('\n')[0])
    else:
        print('List the clients of tenant', TENANT_ID)
        cs = tenant.clients()
        for c in cs.get_list():
            print(c)
            cobj = cs.client(c['uniqueId'])
            resp = cobj.get()
            print('createdBy', resp['createdBy'])
        print('Exercise the create-client code')
        cdef = opsramp.msp.Client.mkclient(
            name='test client 93',
            address='Death Valley',
            time_zone='America/Los_Angeles',
            country='United States')
        print(cdef)
        # uncomment these lines to actually create the client.
        # resp = cs.create_client(cdef)
        # print(resp)

    print('List the monitoring templates on tenant', TENANT_ID)
    monitoring = tenant.monitoring()
    templates = monitoring.templates()
    resp = templates.search()
    print(resp['totalResults'], 'templates')
    for t in resp['results']:
        print('...', t['name'])

    print('Search for open alerts on tenant', TENANT_ID)
    open_alerts = tenant.get_alerts('actions:OPEN')
    # there might be thousands so only print the first one.
    print(open_alerts['totalResults'], 'open alerts')
    al0 = open_alerts['results'][0]
    for key, value in al0.items():
        print('>', key, value)

    # list the RBA script categories and find or create the one we want.
    print('List the RBA categories on tenant', TENANT_ID)
    rba = tenant.rba()
    clist = rba.get_categories()
    print(len(clist), 'categories')
    for c in clist:
        print(c)
        if c['name'] == CATEGORY_NAME:
            cid = c['id']
            break
    else:
        resp = rba.create_category(CATEGORY_NAME)
        cid = resp['id']

    print('Scripts in category', cid)
    cobj = rba.category(cid)
    slist = cobj.get_scripts()
    print(len(slist), 'scripts')
    # slist contains a complete description of each script but let's pull
    # them individually anyway and assert that this gives the same result.
    for s in slist:
        print('...', s['id'], s['name'])
        sobj = cobj.script(s['id'])
        direct = sobj.get()
        assert s == direct

    # Create a new RBA script in this category, with one parameter. You can
    # see from the "payload" that this gets passed to the script as $1
    p1 = opsramp.rba.Script.mkparameter(
        name='venue',
        description='Where am I today?',
        datatype='STRING'
    )
    print('Parameter definition struct')
    print(p1)
    s1 = opsramp.rba.Script.mkscript(
        name='Hello <venue>',
        description='Stereotypical rock star intro',
        platforms=['LINUX'],
        execution_type='COMMAND',
        payload='echo "hello $1"',
        parameters=[p1]
    )
    print('Script definition struct')
    print(s1)
    # uncomment these lines to actually create the script.
    # resp = cobj.create_script(s1)
    # print(resp)

    print('Management policies on tenant', TENANT_ID)
    policies = tenant.policies()
    plist = policies.get_list()
    print(len(plist), 'policies')
    for p in plist:
        rules = p['rules']
        actions = p['actions']
        print('...', p['id'], p['uid'], p['name'],
              'rules', len(rules),
              'actions', len(actions))
        for r in rules:
            print('...... rule', r)
        for a in actions:
            print('...... action', a['action'])
        # plist contains a complete description of each policy
        # but let's pull them individually anyway and assert that
        # this gives the same result.
        pobj = policies.policy(p['id'])
        direct = pobj.get()
        assert p == direct


if __name__ == "__main__":
    main()
