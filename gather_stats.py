#!/usr/bin/env python2

#  Copyright (C) 2016 Mathew Odden
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# NOTE(mrodden): only testing on python27... might work with py3

from __future__ import print_function

import argparse
import csv
import json

# many drivers fill this interface...
import MySQLdb as db_driver
from MySQLdb import cursors


metrics = {
    'instances.active.count': 'select count(*) from instances where deleted=0',
    'compute_node.active.count': 'select count(*) from compute_nodes where deleted=0'
}

metric_tables = {
    'service.binary.%s': {
        'query': 'select services.binary, count(*) as count from services where deleted=0 group by services.binary',
        'metric_vary_field': 'binary'
    },
    'flavors.%s': {
        'query': 'select instance_types.id,instance_types.name,instance_types.vcpus,instance_types.memory_mb,instance_types.root_gb,instance_types.is_public,(case when instance_types.deleted<>0 then 1 else 0 end) as is_deleted,count(instances.id) as num_active from instances,instance_types where instances.deleted=0 and instances.instance_type_id=instance_types.id group by instances.instance_type_id order by num_active desc',
        'metric_vary_field': 'id',
        'fields': ['num_active']
    }
}


tables = {
    'flavor_info': {
        'query': 'select instance_types.id,instance_types.name,instance_types.vcpus,instance_types.memory_mb,instance_types.root_gb,instance_types.is_public,(case when instance_types.deleted<>0 then 1 else 0 end) as is_deleted,count(instances.id) as num_active from instances,instance_types where instances.deleted=0 and instances.instance_type_id=instance_types.id group by instances.instance_type_id order by num_active desc'
    },
    'service_counts': {
        'query': 'select services.binary, count(*) as count from services where deleted=0 group by services.binary'
    },
    'images_top_10_active': {
        'query': 'select image_ref, count(id) as count from instances where instances.deleted=0 group by image_ref order by count desc LIMIT 10'
    },
    'tenants_top_10_active_instances': {
        'query': 'select project_id, count(id) as count from instances where deleted=0 group by project_id order by count desc LIMIT 10'
    }
}


def get_conn(**kwargs):
    kwargs.update(conn_defaults)
    return db_driver.connect(**kwargs)


def dump_table(conn, table_name):
    table = {'headers': [],
             'data_rows': []}

    c = conn

    c.execute('describe %s' % table_name)
    for result in c.fetchall():
        table['headers'].append(result[0])

    c.execute('select * from %s' % table_name)
    for result in c.fetchall():
        table['data_rows'].append(result)

    return table


def main():
    args = _parse_args()

    global conn_defaults
    conn_defaults = {'host': args.host,
                     'db': args.database,
                     'user': args.user}
    if args.passwd is not None:
        conn_defaults['passwd'] = args.passwd

    metric_data = {}

    for metric,query in metrics.iteritems():
        with get_conn() as c:
            c.execute(query)
            for result in c.fetchone():
                metric_data[metric] = result


    for metric_fmtstr,table_info in metric_tables.iteritems():
        with get_conn(cursorclass=cursors.DictCursor) as c:
            c.execute(table_info['query'])
            for result in c.fetchall():
                metric_name_base = metric_fmtstr % result[table_info['metric_vary_field']]
                for key,val in result.iteritems():
                    if key == table_info['metric_vary_field']:
                        continue
                    elif (table_info.get('fields') is not None and
                          key not in table_info.get('fields', [])):
                        continue
                    else:
                        metric_name = metric_name_base + '.%s' % key
                        metric_data[metric_name] = val

    table_data = {}

    for metric,item_info in tables.iteritems():
        with get_conn(cursorclass=cursors.DictCursor) as c:
            c.execute(item_info['query'])
            data_list = []
            for result in c.fetchall():
                data_list.append(result)
            table_data[metric] = data_list

    data = {'metrics': metric_data,
            'tables': table_data}

    if args.outfile is not None:
        with open(args.outfile, 'w') as stat_file:
            json.dump(data, stat_file)
    else:
        print(json.dumps(data))


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-u', '--user', required=True)
    p.add_argument('-p', '--passwd')
    p.add_argument('-H', '--host', default='localhost')
    p.add_argument('-D', '--database', default='nova')
    p.add_argument('-O', '--outfile')

    return p.parse_args()


if __name__ == '__main__':
    main()
