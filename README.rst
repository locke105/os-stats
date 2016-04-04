os_stats
========

A small set of scripts for gathering and manipulating some metrics/stats from your OpenStack database.

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

This drops a file in your working directory named 'os_stats.json' that has whatever metrics/tables you want to gather.
