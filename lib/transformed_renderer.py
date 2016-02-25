# transformed_renderer.py
#
#
# B. Bird - 02/11/2016

import sdl2
import sdl2.ext
from sdl2 import *
import sdl2.sdlgfx
import numpy
import ctypes

def sint16_array(n):
	return (ctypes.c_short*n)()

CIRCLE_POINTS = 16
class TransformedRenderer:

	def __init__(self,renderer):
		self.renderer = renderer
		self.transform = numpy.matrix(numpy.identity(3))
	
	def set_transform(self, transform):
		self.transform = numpy.matrix(transform)
		
	def transform_vector(self,x,y):
		V = numpy.matrix((x,y,1)).T
		W = self.transform*V
		return int(W[0]), int(W[1])
	
	def draw_line(self,x1,y1,x2,y2,width, r, g, b, a):
		ix1, iy1 = self.transform_vector(x1,y1)
		ix2, iy2 = self.transform_vector(x2,y2)
		sdl2.sdlgfx.thickLineRGBA(self.renderer,ix1,iy1,ix2,iy2,width,r,g,b,a)
		
	def draw_circle(self,x,y,radius,r,g,b,a):
		theta = 2*numpy.pi/CIRCLE_POINTS
		M = numpy.matrix( ( (numpy.cos(theta), numpy.sin(theta)), (-numpy.sin(theta), numpy.cos(theta))))
		V = numpy.matrix( (radius,0) ).T
		vx = numpy.zeros(CIRCLE_POINTS)
		vy = numpy.zeros(CIRCLE_POINTS)
		for i in xrange(CIRCLE_POINTS):
			vx[i] = x+float(V[0])
			vy[i] = y+float(V[1])
			V = M*V
		self.draw_polygon(vx,vy,CIRCLE_POINTS,r,g,b,a)
		
	def fill_circle(self,x,y,radius,r,g,b,a):
		theta = 2*numpy.pi/CIRCLE_POINTS
		M = numpy.matrix( ( (numpy.cos(theta), numpy.sin(theta)), (-numpy.sin(theta), numpy.cos(theta))))
		V = numpy.matrix( (radius,0) ).T
		vx = numpy.zeros(CIRCLE_POINTS)
		vy = numpy.zeros(CIRCLE_POINTS)
		for i in xrange(CIRCLE_POINTS):
			vx[i] = x+float(V[0])
			vy[i] = y+float(V[1])
			V = M*V
		self.fill_polygon(vx,vy,CIRCLE_POINTS,r,g,b,a)
		
	def draw_rectangle(self,x1,y1,x2,y2,r,g,b,a):
		vx = [x1,x2,x2,x1]
		vy = [y1,y1,y2,y2]
		self.draw_polygon(vx,vy,4,r,g,b,a)
		
	def fill_rectangle(self,x1,y1,x2,y2,r,g,b,a):
		vx = [x1,x2,x2,x1]
		vy = [y1,y1,y2,y2]
		self.fill_polygon(vx,vy,4,r,g,b,a)
		
	def draw_polygon(self,vx,vy,n,r,g,b,a):
		new_vx = sint16_array(n)
		new_vy = sint16_array(n)
		for i in xrange(n):
			new_vx[i],new_vy[i] = self.transform_vector(vx[i],vy[i])
		sdl2.sdlgfx.polygonRGBA(self.renderer,new_vx,new_vy,n,r,g,b,a)
		
		
	def fill_polygon(self,vx,vy,n,r,g,b,a):
		new_vx = sint16_array(n)
		new_vy = sint16_array(n)
		for i in xrange(n):
			new_vx[i],new_vy[i] = self.transform_vector(vx[i],vy[i])
		sdl2.sdlgfx.filledPolygonRGBA(self.renderer,new_vx,new_vy,n,r,g,b,a)
		
