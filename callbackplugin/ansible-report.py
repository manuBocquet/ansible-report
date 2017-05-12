# (c) 2016, Matt Martz <matt@sivel.net>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish

# check /usr/lib/python2.7/site-packages/ansible/plugins/callback/default.py

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os
import time
from ansible.plugins.callback import CallbackBase
from ansible import constants as C
from ansible.utils.color import stringc
class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'json'

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display)
        self.results = []

    def _new_play(self, play):
        self._display.display("\n ****** ANSIBLE NEW PLAY ******",color=C.COLOR_OK)
        return {
            'play': {
                'name': play.name,
                'id': str(play._uuid)
            },
            'tasks': []
        }

    def _new_task(self, task):
        msg = "\nTask [%s]" % task.name
        self._display.display(msg)
        return {
            'task': {
                'name': task.name,
                'id': str(task._uuid)
            },
            'hosts': {}
        }

    def v2_playbook_on_play_start(self, play):
        self.results.append(self._new_play(play))

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.results[-1]['tasks'].append(self._new_task(task))

    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        self._display.display("    %30s | Ok" % (result._host.get_name()), color=C.COLOR_OK)
        self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result
        self.results[-1]['tasks'][-1]['hosts'][host.name]['epoch'] = int(time.time())

    def v2_runner_on_failed(self, result, **kwargs):
        host = result._host
        self._display.display("    %30s | Failed" % (result._host.get_name()), color=C.COLOR_ERROR)
        self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result
        self.results[-1]['tasks'][-1]['hosts'][host.name]['epoch'] = int(time.time())

    def v2_runner_on_unreachable(self, result, **kwargs):
        host = result._host
        self._display.display("    %30s | Unreachable |" % (result._host.get_name()), color=C.COLOR_UNREACHABLE)
        self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result
        self.results[-1]['tasks'][-1]['hosts'][host.name]['epoch'] = int(time.time())

    def v2_runner_on_skipped(self, result, **kwargs):
        host = result._host
        self._display.display("    %40s | Skipped     |" % (result._host.get_name()), color=C.COLOR_SKIP)
        self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result
        self.results[-1]['tasks'][-1]['hosts'][host.name]['epoch'] = int(time.time())

    def v2_playbook_on_stats(self, stats):
        """Display info about playbook statistics"""

        hosts = sorted(stats.processed.keys())
        filename = os.getenv('ANSIBLE_REPORT_FILE',"report.json")
        fileout = open(filename,"w")
        summary = {}
        for h in hosts:
            s = stats.summarize(h)
            summary[h] = s

        output = {
            'plays': self.results,
            'stats': summary
        }
        fileout.write(json.dumps(output, indent=4, sort_keys=True))
        #self._display.display(json.dumps(output, indent=4, sort_keys=True),stderr=True)
        #self._display.display(json.dumps(self.results, indent=4, sort_keys=True),stderr=True)
        #print (json.dumps(output, indent=4, sort_keys=True),stderr=True)
        #print repr(self)
