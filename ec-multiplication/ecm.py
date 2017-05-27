import fileinput #to be able to read from files

'''
@author André Josefsson
My implementation of basic arithmetics on the standard elliptic curve prime192v3.
Takes a scalar e as input and outputs x and y coordinates such that (x,y)=eG,
where G is the standard generator for the curve.
'''

gx = 0x7d29778100c65a1da1783716588dce2b8b4aee8e228f1896 #x-coord of standard generator
gy = 0x38a90f22637337334b49dcb66a6dc8f9978aca7648a943b0 #y-coord of standard generator
p =  0xfffffffffffffffffffffffffffffffeffffffffffffffff #we work in z_p
a =  0xfffffffffffffffffffffffffffffffefffffffffffffffc #coefficient of x in the curve

class ECP: #Elliptic Curve Point
	
	#constructor, uses globally specified gx and gy if nothing else is specified.
	def __init__(self, x=gx, y=gy):
		self.x = long(x)
		self.y = long(y)

	#Create an identical instance of self and return that one
	def copy(self):
		return ECP(self.x, self.y)

	#The toString method. Prints the values on the format "x y" where:
	#x is the x-coordinate of the ECP written in hexadecimal
	#y is the x-coordinate of the ECP written in hexadecimal
	def __str__(self):
		resX,resY = self.x, self.y
		resX,resY = hex(resX), hex(resY)
		resX,resY = resX[0:len(resX)-1], resY[0:len(resY)-1] #remove the "L" at the end of the string
		return resX + " " + resY

	#Doubles the point (i.e. self multiplies)
	#Works similar to addition but uses tangent line instead of the line between points.
	def dub(self):
		s = 3*self.x*self.x + a
		s = s * self.mulInv(2 * self.y)
		resX = (s * s - 2 * self.x) % p
		resY = (s * (self.x-resX) - self.y) % p
		self.x, self.y = resX, resY

	#Adds the specified ECP to self.
	#Addition works by following the intersecting line to its third intersection.
	def add(self, ecp):
		if self.x == ecp.x and self.y == ecp.y: #Use dub if points are equal, otherwise we get divByZero
			self.dub()
			return
		#find slope of the line between the points. Modulo used inside to make sure its in z_p.
		s = ((self.y-ecp.y) * self.mulInv((self.x - ecp.x)%p)) % p
		resX = (s * s - self.x - ecp.x) % p
		resY = (s * (self.x - resX) - self.y) % p
		self.x, self.y = resX, resY #Update self to reflect the new point

	#Finds the multiplicative inverse of u in z_p
	#example input:  u=5, p=7
	#example output: x=3   (since 5*3%7=1)
	def mulInv(self, u,p=p):
		p0 = p #initial value of p is kept in case x is negative.
		x0 = 0
		x1 = 1

		if p == 1: #if p=1 then xu+yp=1 will always work with x = 1
			return x1
		while u > 1: #perform the euclidean algorithm
			qout = u / p
			u, p = p, u%p
			(x0, x1) = (x1 - qout * x0, x0)
		if x1 < 0:
			#increase x by p0 still lets the equation hold as long as y is decreased by u
			#(which we dont need to do here since we dont want the value of y).
			x1 += p0
		return x1


for line in fileinput.input():
	n = int(line.rstrip(),16) #strip of newline and convert to integer.
	ecp = ECP() #Automatically initializes to gx and gy
	res = ECP() #value will be changed, so doesn't matter what we initialize to
	while n > 0: #This loop just gets the initial value of res, so that we can use add later
		if n % 2 == 1:
			res = ecp.copy()
			ecp.dub()
			n = n >> 1
			break
		else:
			ecp.dub()
			n = n >> 1

	#Calculate result using the shift and double approach.
	#Basically works by calculating 5*7 as (5)+(2*5)+(4*5)
	#by working from the lowest bit and doubling and shifting,
	#the whole calculation can be done in log(n) number of
	#multiplications.
	while n > 0: 
		if n % 2 == 1: #add current value of ecp if lowest current bit is set.
			res.add(ecp)
		ecp.dub()
		n = n >> 1 #shift out lowest bit
	print res
