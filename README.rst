os_stats
========

A small set of scripts for gathering and manipulating some metrics/stats from your OpenStack database.

Currently, we have metrics for:

- number of Nova services active (including active compute nodes)
- number of active instances/servers
- current flavor usage of active instances/servers
- top 10 active tenants by number of instances/servers
- top 10 currently deployed images

usage
-----

Currently, I run this through a short Ansible playbook to dump information directly from the OpenStack Nova database.

Ansible Playbook::

  ---
  - name: gather stats
    hosts: mysql_host
    gather_facts: no
    tasks:
      - name: run stat gather
        script: ../os-stats/gather_stats.py --user nova -D nova --host localhost -p YOURDBPASSWORD -O /tmp/os_stats.json
      - name: fetch results
        fetch:
          src: /tmp/os_stats.json
          dest: os_stats.json
          flat: yes

This drops a file in your working directory named **os_stats.json** that has whatever metrics/tables you want to gather.

Pretty print the data with the **print_info.py** script included.
Note that the output here was trimmed for readability purposes::

  # in the same directory as os_stats.json
  python print_info.py
  ======== METRICS ========
  METRIC                                   VALUE
  -------------------------------------  -------
  compute_node.active.count                   84
  flavors.1012.num_active                      1
  flavors.1057.num_active                      1
  flavors.1348.num_active                   1587
  ...
  instances.active.count                    2158
  service.binary.nova-cert.count               6
  service.binary.nova-compute.count           84
  service.binary.nova-conductor.count          6
  service.binary.nova-consoleauth.count        6
  service.binary.nova-scheduler.count          6
  ...

  ======== IMAGES_TOP_10_ACTIVE ========
  count  image_ref
  -------  ------------------------------------
  796  97f6164b-9bc9-4bff-93f1-5e010eda82ad
  445  7305c3f6-2bd0-49de-8f01-be60b04d792a
  221  aceefa6f-7914-49df-839b-61bf6cc97694
  ...
