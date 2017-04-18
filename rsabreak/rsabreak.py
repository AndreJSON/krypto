import random
import fractions #for gcd
import fileinput

'''
Let ~ denote congruence in the comments of this file.
The algorithm builds on the observation that if we have:
y^2~1(mod N) <=>
y^2-1~0(mod N) <=>
(y-1)(y+1)~0(mod N)

then if N=p*q where p and q are primes, we know for sure through the zero product property that:
y~1(mod p) or y~-1(mod p)
y~1(mod q) or y~-1(mod q)

Now any non trivial solution to the above, say for example:
y~-1(mod p)
y~1(mod q)

gives us p|(y-1), meaning gcd(y-1,N)=p
which is the solution we are looking for. (we get q through N/p)

Now also observe that for k=ed-1 we have k~0(mod phi(N)) by definition of e&d [Def. e,d chosen such that ed~1(mod phi(N))]
So for any random number x, we have x^k~x^0~1(mod N)
So the square root of x^k is a root of 1 mod N, which is just what we were looking for.
If it is non-trivial we are done, otherwise, simply divide k by two if possible and try again.
If not possible, try a new x.

Since half of all roots are non-trivial, we will succeed in a short amount of time.
'''

# Extracts as many factors of two as possible,
# then returns (r, t) such that x = r*2^t and
# t is the largest such value for x.
def extractTwos(x):
	r = x
	t = 0
	while (r % 2) == 0: #keep dividing by 2 as long as possible
		t = t + 1
		r = r / 2
	return (r, t)

#tries to find a root of N using x. Returns the root if it finds one,
#otherwise simply returns None so that we can try with a new x.
def findRoot(x, k, N):
	(r, t) = extractTwos(k)#factor k
	while t != -1:
		g = pow(x, r*pow(2,t), N) #set g = x^k first iteration, then g = x^(k/2) and so on as long as we can.
		t -= 1
		if g > 1: #Could potentially yield a non-trivial factor
			p = fractions.gcd(g-1,N)
			if p > 1: #if non-trivial
				return p
	return None

#factors N given e and d, then returns p and q in the form of a tuple.
def factor(N, e, d):
	k = e*d - 1
	p = None
	while not p:
		x = random.randrange(2, N) #pick a random x that is non-trivial and not unnecessarily large
		p = findRoot(x, k, N)
	q = N / p
	return (p, q)


for line in fileinput.input(): #read as long as there is more input
	input = map(int, line.split())
	N = input[0] #extract N from the array
	e = input[1] #extract e from the array
	d = input[2] #extract d from the array
	(p,q) = factor(N, e, d) #call the solver and print the solution.
	if p > q: #used to make sure we print smallest first for consistent output
		p,q = q,p
	print '%d %d' % (p,q)