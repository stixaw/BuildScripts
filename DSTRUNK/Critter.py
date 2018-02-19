# We Learn Chapter 8
#Simple Critter

# Demonstrate a basic class and object


class Critter(object):
	"""a virtual pet"""
	def __init__(self, name):
		print "A new Critter has been born!"
		self.name = name
	def __str__(self):
		rep = "Critter object\n"
		rep += "name: " + self.name + "\n"
		return rep

	def talk(self):
		print "\nHi, I am ", self.name, "\n"

#main
crit1 = Critter("Poopie")
crit1.talk()

crit2 = Critter("Loopie")
crit2.talk()

print "Printing crit1: "
print crit1

print "Directly accessing crit2.name: "
print crit2.name

raw_input("\n\nPress the enter key to exit.")