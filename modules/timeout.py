import threading
import _thread   # import thread in python2
import time
class timeout():
  def __init__(self, time):
    self.time= time
    self.exit=False

  def __enter__(self):
    threading.Thread(target=self.callme).start()

  def callme(self):
    time.sleep(self.time)
    if self.exit==False:
       _thread.interrupt_main()  # use thread instead of _thread in python2
  def __exit__(self, a, b, c):
       self.exit=True