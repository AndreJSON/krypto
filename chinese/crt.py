import fileinput

'''
Let ~ denote congruence in the comments.
The solution mainly builds on the fact that if:
x1~a1(mod n1)
x2~a2(mod n2)

where:
x1=a1m2n2
x2=a2m1n1

then we also have:
(x1+x2)~x(mod n1n2)

where:
x~a1(mod n1)
x~a2(mod n2)

since the above gives us this formula for x:
x=x1+x2+mn1n2

which solves the congruences:
x~x1+x2+mn1n2~x1(mod n1) (as x2 is defined as a2m1n1)
x~x1+x2+mn1n2~x2(mod n2) (as x1 is defined as a1m2n2)

This idea is easily extended to work with any number of congruences provided you treat them pairwise as
will be explained in the alogithm summary below.

The algorithm works by computing the above idea with n1 being one of the moduli q_i each iteration
and n2 being the product of the other moduli. This ensures that after each iteration, the partial sum
will be congruent to that a_i. In the end we will have a number congruent to all a_i:s.

Finding m1 for each iteration is easy with the extended euclidean as long as n1 and n2 are coprime, which
the will always be since all q_i:s are pairwise coprime.
'''

def crt(q, a):
	if len(a) == 1: #If there's only one modulo, the answer will be the a for that one.
		return a[0]
	N = reduce(lambda i, j: i*j, q) #Calculate N (product of all q:s)
	sum = 0
	for i in range(0,len(q)):
		nonQModuli = N / q[i] #q[i] will be n1 and N/q[i] will be n2 from our proof above.
		sum += a[i] * extendedEuclidean(nonQModuli, q[i]) * nonQModuli
	return sum % N

#modified version of the algorithm that finds x such that xu+yv=1 and x > 0
#finding this x is always possible if u and v are coprime, which they will be here.
def extendedEuclidean(u, v):
	v0 = v #initial value of v is kept in case x is negative
	x0 = 0
	x1 = 1

	if v == 1: #if v=1 then xu+yv=1 will always work with x = 1
		return x1
	while u > 1: #perform the euclidean algorithm
		qout = u / v
		u, v = v, u%v
		(x0, x1) = (x1 - qout * x0, x0)
	if x1 < 0:
		#increase x by v still lets the equation hold as long as y is decreased by u
		#(which we dont need to do here since we dont want the value of y).
		x1 += v0
	return x1

for line in fileinput.input(): #read as long as there is more input
	input = map(int, line.split())
	num = input[0] #num of q:s and a:s
	q = input[1:num+1] #extracts q:s from array
	a = input[num+1:2*num+1] #extract a:s from array
	print crt(q, a) #call solver and print result to stdout