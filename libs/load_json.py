import json
import sys
import re
import pprint

def load_file(file):
    data = {}
    status = {}
    left = {}
    skipped = {}
    status['changed'] = 0
    status['failures'] = 0
    status['ok'] = 0
    status['skipped'] = 0
    status['unreachable'] = 0
    data['servers'] = {}
    data['id'] = {}
    sep = "<br>"
    pp = pprint.PrettyPrinter(indent=4)

    try:
        with open(file) as json_file:
            json_data_brut = json_file.read()
            tmp_data = re.sub(r"^(.*\n)*^{",r"{",json_data_brut,1,re.MULTILINE)
            json_data = json.loads(tmp_data)
    except IOError:
        print "\n  Please specify Ansible json output file as first argument\n"
        sys.exit(1)
    print "Load file :", file
    for server in json_data['stats']:
        status['changed'] += json_data['stats'][server]['changed']
        status['failures'] += json_data['stats'][server]['failures']
        status['ok'] += json_data['stats'][server]['ok']
        status['skipped'] += json_data['stats'][server]['skipped']
        status['unreachable'] += json_data['stats'][server]['unreachable']
        data['servers'][server] = {}
        left[server] = 0
        skipped[server] = 0
    for tasks in json_data['plays'][0]['tasks']:
        for mydata in tasks:
            if mydata=="task":
                name=tasks[mydata]['name']
                id=tasks[mydata]['id']
                data['id'][id] = name

            if mydata=="hosts":
                for server in tasks[mydata]:
                    data['servers'][server][id] = {}
                    if 'invocation' in tasks[mydata][server]:
                        if 'module_name' in tasks[mydata][server]['invocation']:
                            if tasks[mydata][server]['invocation']['module_name'] == "setup" :
                                del data['servers'][server][id]
                                continue
                            data['servers'][server][id]['module_name'] = tasks[mydata][server]['invocation']['module_name']
                    else :
                        data['servers'][server][id]['module_name'] = "undef"
                    msg = json.dumps(tasks[mydata][server],sort_keys=True, indent=4, separators=(',', ': '))
                    msg = msg.replace('\n',sep)
                    data['servers'][server][id]['msg'] = msg
                    if 'epoch' in tasks[mydata][server]:
                        data['servers'][server][id]['epoch'] = tasks[mydata][server]['epoch']
                    if 'start' in tasks[mydata][server]:
                        data['servers'][server][id]['start'] = tasks[mydata][server]['start']
                        data['servers'][server][id]['delta'] = tasks[mydata][server]['delta']
                    ## set status
                    data['servers'][server][id]['status'] = "bs-callout-info"
                    if 'changed' in tasks[mydata][server] and tasks[mydata][server]['changed'] == True:
                        data['servers'][server][id]['status'] = "bs-callout-success"
                        if left[server] < 2:
                            left[server] = 2
                    if 'unreachable' in tasks[mydata][server] and tasks[mydata][server]['unreachable'] == True:
                        data['servers'][server][id]['status'] = "bs-callout-danger"
                        left[server] = 4
                    if 'failed' in tasks[mydata][server] and tasks[mydata][server]['failed'] == True:
                        data['servers'][server][id]['status'] = "bs-callout-danger"
                        left[server] = 3
                    if 'skipped' in tasks[mydata][server] and tasks[mydata][server]['skipped'] == True:
                        data['servers'][server][id]['status'] = "bs-callout-default"
                    else:
                        skipped[server] = 1
                        if left[server] < 1:
                            left[server] = 1

    status['nb_servers'] = len(data['servers'])
    data['status'] = status
    data['left'] = left
    data['skipped'] = skipped
    #print pp.pprint(data)
    return data

