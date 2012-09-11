#!/usr/bin/env python

import sys
import numpy
from time import time

start = time()

GRID_SIZE = 4

# Can fill 1..g**2 blocks in a grid of size g

# If you increase g->g+1, all new pieces must contain a block
# in at least every row or every column

# Nested dicts holding pieces
#  first-level key is grid size
#  second-level key is number of blocks
pieces = {}

def pretty_list(l):
	for p in l:
		for y in xrange(p.shape[1]):
			sys.stdout.write(' ')
			for x in xrange(p.shape[0]):
				if p[x][y]:
					sys.stdout.write('X')
				else:
					sys.stdout.write('.')
			sys.stdout.write('\n')
		sys.stdout.write('\n')

def gen_blocks(size):
	def a_to_n(a):
		n = 0
		for x in reversed(xrange(size)):
			for y in reversed(xrange(size)):
				if a[x][y]:
					n |= 1
				n <<= 1
		n >>= 1
		return n

	def n_to_a(a, n):
		for x in xrange(size):
			for y in xrange(size):
				a[x][y] = n & 1
				n = n >> 1


	def is_cand(a):
		a0 = a.sum(axis=0)
		a1 = a.sum(axis=1)
		fail = 0
		if a0[0] == 0:
			fail += 1
		if a0[-1:] == 0:
			fail += 1
		if a1[0] == 0:
			fail += 1
		if a1[-1:] == 0:
			fail += 1
		if fail > 1:
			return False
		return True

	def is_rot(a, b):
		if numpy.array_equal(a,b):
			return True
		for x in xrange(3):
			a = numpy.rot90(a)
			if numpy.array_equal(a,b):
				return True

	def is_trans(a, b):
		a = a.transpose()
		#if numpy.array_equal(a,b):
			#return True
		if numpy.any(a != b):
			return False
		return True

	def invalid_rot(a):
		for x in xrange(3):
			a = numpy.rot90(a)
			n = a_to_n(a)
			trans_ign.add(n)
	
	def invalid_flips(a):
		invalid_rot(a)
		a = numpy.flipud(a)
		invalid_rot(a)
		a = numpy.fliplr(a)
		invalid_rot(a)
		a = numpy.flipud(a)
		invalid_rot(a)

	def add(a):
		if is_cand(a):
			try:
				pieces[size][int(a.sum())].append(a.copy())
			except:
				print a
				print a.sum()
				raise
			invalid_flips(a)
			# Safe to mutate as both last col and last row
			# necessarily cannot be empty (o/w smaller grid)
			while (a.sum(axis=0)[-1:] == 0):
				a = numpy.roll(a, 1)
				invalid_flips(a)
			while (a.sum(axis=1)[-1:] == 0):
				a = numpy.roll(a, 1, 0)
				invalid_flips(a)

	trans_ign = set()
	grid = numpy.zeros(shape=(size,size), dtype='bool')
	for g in xrange(1,2**(size**2)):
		"""
		if not g % 2**15:
			print str(g)+" ("+str(float(g)/2**(size**2) *100) + "%)",
			print "\t(%f elapsed)" % (round(time() - start, 1))
			for b,l in pieces[size].iteritems():
				print str(b) + " Block Cnt: " + str(len(l))
				if b == 4 and False:
					print pretty_list(l)
			sys.stdout.flush()
		"""
		if g in trans_ign:
			continue
		n_to_a(grid, g)
		if grid.sum() >= size:
			add(grid)

for g in xrange(1,GRID_SIZE+1):
	pieces[g] = {}
	for s in xrange(g, g**2+1):
		pieces[g][s] = []
	gen_blocks(g)
	print "Grid %d Complete. Elapsed %f" % (g, round(time() - start, 1))
	sys.stdout.flush()

###############################################################

def is_contiguous(pts, p):
	p = p.astype(int).copy()
	any_found = False
	for x in xrange(p.shape[0]):
		for y in xrange(p.shape[1]):
			if p[x][y]:
				good = False
				for pt in pts:
					try:
						if any_found:
							if p[x+pt[0]][y+pt[1]] == 2:
								good = True
								break
						else:
							if p[x+pt[0]][y+pt[1]]:
								good = True
								break
					except IndexError:
						continue
				if not good:
					return False
				p[x][y] = 2
				any_found = True
	return True

def is_corner_contiguous(p):
	pts = (\
			(-1, -1), (-1, 1), (1, 1), (1, -1),\
			(-1, 0), (1, 0), (0, -1), (0, 1)\
	      )
	return is_contiguous(pts, p)

def is_mixed_contiguous(p):
	pts = (\
			(-1, 0), (1, 0), (0, -1), (0, 1)\
	      )
	return is_contiguous(pts, p)

def is_pure_contiguous(p):
	# pure contiguous is defined as a subset of mixed contiguous as a piece
	# that contains no holes. The assumption is that any piece passed to this
	# function has already been established to be mixed contiguous
	p = p.copy()
	pts = (\
			(-1, 0), (1, 0), (0, -1), (0, 1)\
	      )
	for x in xrange(p.shape[0]):
		for y in xrange(p.shape[1]):
			if not p[x][y]:
				good = False
				for pt in pts:
					try:
						if not p[x+pt[0]][y+pt[1]]:
							good = True
							break
					except IndexError:
						# Gaps against wall okay
						good = True
						break
				if not good:
					return False
				# Filling in holes finds holes > 1 in size
				p[x][y] = 1
	return True


def write_piece(o, pc_id, p):
	o.write('id=%d,size=%d\n' % (pc_id, p.shape[0]))
	root_written = False
	for x in xrange(p.shape[0]):
		for y in xrange(p.shape[1]):
			if p[x][y]:
				if root_written:
					o.write('X')
				else:
					o.write('O')
					root_written = True
			else:
				o.write('.')
		o.write('\n')

pure = open("pure_contiguous", 'w')
pure_id = 0
mixed = open("mixed_contiguous", 'w')
mixed_id = 0
corner = open("corner_contiguous", 'w')
corner_id = 0
allpc = open("all_pieces", 'w')
allpc_id = 0

print "================================================================"
for c,d in pieces.iteritems():
	print "Writing Grid %d. Elapsed %f" % (c, round(time() - start, 1))
	for b,l in d.iteritems():
		print "\tPieces with %2d Blocks: %d" % (b, len(l))
		sys.stdout.flush()
		for p in l:
			write_piece(allpc, allpc_id, p)
			allpc_id += 1
			if is_corner_contiguous(p):
				write_piece(corner, corner_id, p)
				corner_id += 1
				if is_mixed_contiguous(p):
					write_piece(mixed, mixed_id, p)
					mixed_id += 1
					if is_pure_contiguous(p):
						write_piece(pure, pure_id, p)
						pure_id += 1

print "================================================================"
print "Done. Elapsed %f" % (round(time() - start, 1))
