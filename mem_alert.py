#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import time,re,json,requests
import commands,string
from influxdb import client
reload(sys)
sys.setdefaultencoding('utf8')

class Every_list(object):
	def __init__(self,index,line):
		self.index = index
		self.line = line
	def get_host(self):
		every_list = eval(self.line)
		return str(every_list["host"]).split('-')[0]
	def get_ip(self):
		every_list = eval(self.line)
		return str(every_list["host"]).split('-')[2]
	def get_rate(self):
		every_list = eval(self.line)
		return int(every_list["used_percent"])
	def get_time(self):
		every_list = eval(self.line)
		return every_list["time"]
#判断告警主机在告警主机文件列表中出现的次数
def juggle_data(host):
	file_mem = open(memoutputfile).read()
	return len(re.findall(host,file_mem))
#判断文件是否存在output.txt,如果存在,删除
memoutputfile = "/data/influxdb_python/output/mem.txt"
def collector_data():
	if os.path.exists(memoutputfile):
		os.system("rm %s -rf"%(memoutputfile))
	#创建一个连接
	conn = client.InfluxDBClient("192.168.1.2",8086,"admin","xxxxxx","tigk")
	#mem数据获取
	with open(memoutputfile,"w") as f_mem:
		for i in range(1,4):
		        rs = conn.query("SELECT host::tag, used_percent::field FROM mem WHERE time > now() - 10s and used_percent >= 80 group by host limit 1")
		        lens = len(list(rs.get_points()))
		        for l in range(0,lens):
				f_mem.write(str(list(rs.get_points())[l]))
				f_mem.write('\n')
		        time.sleep(10)
#判断数据进行告警
def data_check():
	host_ip_dict = {}
	host_value_dict = {}
	for index,line in enumerate(open(memoutputfile,'r'),1):
		data = Every_list(index,line)
		host = data.get_host()
		ip = data.get_ip()
		rate = data.get_rate()
		if juggle_data(host) == 3:
			host_ip_dict.setdefault(host,ip)
			host_value_dict.setdefault(host,[]).append(rate)
	#print host_ip_dict
	#print host_value_dict
	for (host,ip) in host_ip_dict.items():
		if host_value_dict[host][0] in range(80,90) and host_value_dict[host][1] in range(80,90) and host_value_dict[host][2] in range(80,90):
			alert("wx","warn","华东",host,ip,"80")
		elif host_value_dict[host][0] in range(90,100) and host_value_dict[host][1] in range(90,100) and host_value_dict[host][2] in range(90,100):
			alert("wx","crit","华东",host,ip,"90")
def alert(stype,level,env,host,ip,mem):
	AUTH = ('root','xxxxxxx')
	if stype == "email":
		send_type = "email"
		receiver = "xxxx@xxxx.com"
		content = "Notify alert ： <br> 环境："+env+"<br>"+"服务名："+host+"<br>"+"IP地址："+ip+"<br>"+"内存使用率经过检测三次超过"+mem+"%,请及时处理!  <br> ---丹露运维部Ops"
	elif stype == "wx":
		send_type = "wx"
		receiver = "@all"
		content = "Env:%s,Service:%s,Ipaddr:%s,mem more than %s%%"%(env,host,ip,mem)
	elif stype == "sms":
		send_type = "sms"
		receiver = "18600000000"
		content = "@1@=%s,@2@=%s,@3@=%s"%(env,host,ip)
	else:
		pass

	data = {
		"sender":"danlu_auto_monitor",
		"receiver":receiver,
		"send_type":send_type,
		"send_level":level,
		"send_content":content
	}	
	rsp = requests.post("http://192.168.1.2:9111/mesgpost/%s/"%(send_type),auth=AUTH,headers={'Accept': 'application/json','Content-Type': 'application/json',},data=json.dumps(data,ensure_ascii=False))
	return rsp.text
collector_data()
time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
data = open(memoutputfile).read()
logfile = open("/data/influxdb_python/log/mem_alert.log",'a')
if len(data) == 0:
        print >> logfile,"%s,mem no alert"%(time_now)
else:
        data_check()
        print >> logfile,"%s,mem alert"%(time_now)
