# -*- encoding=utf-8 -*-

import json
import subprocess

def get_list():
  cmd_str = """ps -ef|grep -o "app=.*"|grep -v "\.\*"|awk '{print $1}'"""
  c2 = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  retcode = c2.wait()
  data = []
  if retcode == 0:
    stdo = c2.stdout.readlines()
    for line in stdo:
      if not line or line.strip() == "": continue
      appname = line.replace('app=','').strip('\n')
      item = {"{#APPNAME}":appname}
      data.append(item)
  else:
    stde = c2.stderr.readlines()
    print('ERROR: %s'%(stde))
    exit()

  print(json.dumps({'data':data}, sort_keys=True, indent=7, separators=(",", ":")))

if __name__ == '__main__':
  get_list()
