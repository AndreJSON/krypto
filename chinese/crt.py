import fileinput

def crt(q, a):
	if len(a) == 1: #If there's only one modulo, the answer will be the a for that one.
		return a[0]
	N = reduce(lambda i, j: i*j, q) #Calculate N (product of all q:s)
	sum = 0
	for i in range(0,len(q)):
		nonQModuli = N / q[i]
		sum += a[i] * extendedEuclidean(nonQModuli, q[i]) * nonQModuli
	return sum % N

def extendedEuclidean(u, v):
	v0 = v
	x0 = 0
	x1 = 1

	if v == 1: #if v=1 then xu+yv=1 will always work with x = 1
		return x1
	while u > 1:
		qout = u / v
		u, v = v, u%v
		(x0, x1) = (x1 - qout * x0, x0)
	if x1 < 0:
		x1 += v0
	return x1

for line in fileinput.input():
	input = map(int, line.split())
	num = input[0]
	q = input[1:num+1]
	a = input[num+1:2*num+1]
	print crt(q, a)