import json

from tabulate import tabulate


def main():
    with open('os_stats.json') as json_file:
        data = json.load(json_file)

    # scalar metrics
    headers = map(lambda x: x.upper(), ['metric', 'value'])

    print '%s %s %s' % ('=' * 8, 'metrics'.upper(), '=' * 8)
    print tabulate(sorted(data['metrics'].iteritems()),
                   headers=headers)

    # tables
    for table_name,table_data in data['tables'].iteritems():
        print
        print '%s %s %s' % ('=' * 8, table_name.upper(), '=' * 8)
        print tabulate(table_data, headers='keys')



if __name__=='__main__':
    main()
