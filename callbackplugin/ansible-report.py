# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: debug
    type: stdout
    short_description: formated stdout/stderr display
    description:
      - Use this callback to sort though extensive debug output
    version_added: "2.4"
    extends_documentation_fragment:
      - default_callback
    requirements:
      - set as stdout in configuration
'''

from ansible.plugins.callback.default import CallbackModule as CallbackModule_default
from ansible import constants as C
import json
import os
import time
import sqlite3

class CallbackModule(CallbackModule_default):  # pylint: disable=too-few-public-methods,no-init
    '''
    Override for the default callback module.
    Render std err/out outside of the rest of the result which it prints with
    indentation.
    '''
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'debug'
    db  = None
    cdb = None

    def __init__(self):
        self.results = []
        return CallbackModule_default.__init__(self)

    ##################################################################
    #    Add module filter to send data to an sqlite database

    def init_sqlite(self, file):
        #self._display.display("init database [%s]" % file)
        self.db  = sqlite3.connect(file)
        self.cdb = self.db.cursor()
        self.cdb.execute('''DROP TABLE IF EXISTS ansible''')
        self.cdb.execute('''CREATE TABLE ansible( host TEXT, data TEXT, value TEXT, epoch REAL, task TEXT, unique (host,data,task))''')

    def db_update_value(self, hostname, data, value, epoch, task):
        self.cdb.execute("INSERT or REPLACE INTO ansible (host,data,value,epoch,task) VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" % (hostname,data,value,epoch,task))

    def module_filter(self, result):
        #self._display.display("Module filter, action: {}".format(result._task.action))
        if result._task.action == "set_fact":
            #self._display.display( json.dumps({"host": result._result}, indent=4) )
            #self._display.display( "task {}".format(result._task.name ))
            #if result._task.args:
            #    self._display.display(json.dumps(result._task.args))
            if 'sqlite' in result._task.args:
                if not self.db:
                    dbfile = result._task.args['sqlite']
                    self.init_sqlite(dbfile)
                dargs = result._task.args['data']
                for data in dargs:
                    value = str(dargs[data])
                    self.db_update_value(result._host,data,value,result._result['epoch'],result._task.name)
   
    #########################
    # End module filter


    def _new_play(self, play):
        return {
            'play': {
                'name': play.name,
                'id': str(play._uuid)
            },
            'tasks': []
        }

    def _new_task(self, task):
        return {
            'task': {
                'name': task.name,
                'id': str(task._uuid)
            },
            'hosts': {}
        }
 
    def v2_playbook_on_play_start(self, play):
        self.results.append(self._new_play(play))
        return CallbackModule_default.v2_playbook_on_play_start(self, play)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.results[-1]['tasks'].append(self._new_task(task))
        return CallbackModule_default.v2_playbook_on_task_start(self, task, is_conditional)

    def v2_runner_on_ok(self, result):
        host = result._host
        self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result
        self.results[-1]['tasks'][-1]['hosts'][host.name]['epoch'] = time.time()
       	self.module_filter(result)
        return CallbackModule_default.v2_runner_on_ok(self,result)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host
        self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result
        self.results[-1]['tasks'][-1]['hosts'][host.name]['epoch'] = time.time()
        return CallbackModule_default.v2_runner_on_failed(self,result,ignore_errors)

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result
        self.results[-1]['tasks'][-1]['hosts'][host.name]['epoch'] = time.time()
        return CallbackModule_default.v2_runner_on_unreachable(self,result)

    def v2_runner_on_skipped(self, result):
        host = result._host
        self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result
        self.results[-1]['tasks'][-1]['hosts'][host.name]['epoch'] = time.time()
        return CallbackModule_default.v2_runner_on_skipped(self,result)

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
        if self.db:
            self.db.commit()
            self.db.close()
        return CallbackModule_default.v2_playbook_on_stats(self, stats)










