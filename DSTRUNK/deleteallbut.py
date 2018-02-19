import os
import sys
import glob
import fnmatch

temp = os.getenv("TEMP")
print temp

for path, dirs, files in os.walk(temp):
  for file in [os.path.join(path, filename) for filename in files if (not(fnmatch.fnmatch(filename, 'hudson*.bat')))]:
    try:
      print "deleting temp: ", file
      os.remove(file)
    except:
      print "can't access", file, "skipping", file
for path, dirs, files in os.walk(temp):
  for name in dirs:
    print (os.path.join(path, name))
    try:
      os.rmdir(os.path.join(path, name))
    except:
      print "can't access", name, "skipping", name

print "THIS IS A TEST"