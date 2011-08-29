#!/usr/bin/env python

import os,psutil,signal,daemon,time,sys
from psutil import Process

class WatchDog(daemon.Daemon):
	def __init__(self,name,threshold,wait):
		super(WatchDog, self).__init__('/tmp/watch_%s.pid'%name)
		self.name=name
		self.threshold=float(threshold)
		self.wait=int(wait)#seconds
	
	def run(self):
		while True:
		#cmdline is tokenized, potentially empty
			for p in [ Process(pid) for pid in psutil.get_pid_list() if self.name in ' '.join(Process(pid).cmdline)]:
				if p.get_memory_percent() > self.threshold:
					try:
						tp = (p.name,p.pid)
						p.send_signal(signal.SIGKILL)
						if p.wait(5) == None:
							print 'killed %s (%d)'%tp
					except psutil.TimeoutExpired, t:
						print 'kill timed out on %s'%str(p)
					except psutil.AccessDenied, g:
						print 'need to be uid %d to kill %s'%(p.uid,str(p))
					except psutil.NoSuchProcess, v:
						print '%s vanished'%str(p)
			time.sleep(self.wait)


if __name__=='__main__':
	try:
		name=sys.argv[1]
		threshold=float(sys.argv[2])
		wait=int(sys.argv[3])#seconds
	except:
		print 'using defaults'
		name='tumbler'
		threshold=.0001
		wait=10#seconds
	dog=WatchDog(name,threshold,wait)
	#dog.run()#run fg
	dog.start()#run daemonized