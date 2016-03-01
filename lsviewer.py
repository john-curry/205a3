# LSViewer.py
#
#
# B. Bird - 02/09/2016

import sys, os, platform
#Set up import paths for the SDL2 libraries
if platform.system() == 'Linux':
	os.environ['PYSDL2_DLL_PATH'] = os.path.join(os.getcwd(),'lib_linux')
elif platform.system() == 'Darwin':
	os.environ['PYSDL2_DLL_PATH'] = os.path.join(os.getcwd(),'lib_osx')
elif platform.system() == 'Windows':
	os.environ['PYSDL2_DLL_PATH'] = os.path.join(os.getcwd(),'lib_windows')

sys.path.insert(0, 'lib')
  
import sdl2
import sdl2.ext
from sdl2 import *
import sdl2.sdlgfx
import time
import math

import numpy
from numpy.linalg import inv
from transformed_renderer import TransformedRenderer
from LSystem import LSystem, LSystemParseException

def IdentityMatrix(n):
	return numpy.matrix(numpy.identity(n))

def Rotation(radians):
	M = IdentityMatrix(3)
	M[0,0] = M[1,1] = numpy.cos(radians)
	M[1,0] = -numpy.sin(radians)
	M[0,1] = numpy.sin(radians)
	return M

def Translation(tx,ty):
	M = IdentityMatrix(3)
	M[0,2] = tx
	M[1,2] = ty
	return M
	
def Scale(sx,sy):
	M = IdentityMatrix(3)
	M[0,0] = sx
	M[1,1] = sy
	return M

class A3Canvas:
	CANVAS_SIZE_X = 800
	CANVAS_SIZE_Y = 600
	
	def __init__(self, L_system):
		self.LS_iterations = 0
		self.L_system = L_system
		self.ls_string = " "
		self.ops = [ ]

	def draw_leaf(self, tr):
		vx = [0,1.0 ,1.25,   1,  0,  -1,-1.25,-1]
		vy = [0,0.75,1.75,2.75,4.0,2.75, 1.75,0.75]
		numVerts = 8;
		tr.fill_polygon(vx,vy,numVerts, 64,224,0, 255)
		tr.draw_polygon(vx,vy,numVerts, 64,128,0, 255)

	def draw_star(self, tr):
		def dl(x1, y1, x2, y2):
			x1 = 2*x1
			x2 = 2*x2
			y1 = 2*y1
			y2 = 2*y2
			tr.draw_line(x1, y1, x2, y2, 2, 255, 255, 0, 255)

		dl(0, 1, 1, -1)
		dl(1, -1, -1, 1)
		dl(-1, 1, 1, 1)
		dl(1, 1, -1, -1)
		dl(-1, -1, 0, 1)
	

	def on_iteration_change(self, iterations):
		save_states = [ ]
 
	def apply_transformation(self, transform, tr, vt, ss):
		vt *= transform
		ss[-1].append(inv(transform))
		tr.set_transform(vt)

	def draw(self,renderer,frame_delta_seconds):
		self.ls_string = self.L_system.generate_system_string(self.LS_iterations)
		#print "Drawing with %d iterations."%(self.LS_iterations)
		#print "System rules" + str({i.rule:i.substitution for i in self.L_system.rules})
		#print "System string: %s"%self.ls_string

		sdl2.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
		sdl2.SDL_RenderClear(renderer);
		
		tr = TransformedRenderer(renderer)
		viewportTransform = IdentityMatrix(3)
		viewportTransform *= Translation(self.CANVAS_SIZE_X/2,self.CANVAS_SIZE_Y)
		viewportTransform *= Scale(1,-1)
		viewportTransform *= Scale(self.CANVAS_SIZE_X/100.0,self.CANVAS_SIZE_Y/100.0)
    # my code goes here?		
		save_states = [ [ ] ]

		def do_transform(t):
				self.apply_transformation(t, tr, viewportTransform, save_states)
			
		for c in self.ls_string:
			if c == 'T':
				tr.fill_rectangle(-1, 0, 1, 9, 165, 42, 42, 255)	
				do_transform(Translation(0, 9))
			elif c == 't':
				self.draw_star(tr)
			elif c == 'o':
				tr.draw_circle(0, 0, 4, 255, 0, 0, 255)
			elif c == 'r':
				do_transform(Translation(0, 5))
			elif c == 'L':
				self.draw_leaf(tr)
			elif c == '+':
				do_transform(Rotation(numpy.pi/6))
			elif c == '-':
				do_transform(Rotation(-numpy.pi/6))
			elif c == 'b':
				do_transform(Rotation(numpy.pi/2))
			elif c == 'd':
				do_transform(Scale(1, 1.5))
			elif c == 'h':
				do_transform(Scale(0.9, 1))
			elif c == 'H':
				do_transform(inv(Scale(0.9, 1)))
			elif c == 'v':
				do_transform(Scale(1, 0.9))
			elif c == 'V':
				do_transform(inv(Scale(1, 0.9)))
			elif c == 's':
				do_transform(Scale(0.9, 0.9))
			elif c == 'S':
				do_transform(inv(Scale(0.9, 0.9)))
			elif c == '[':
				save_states.append([ ])
			elif c == ']':
				undo = save_states.pop()
				undo.reverse()
				for t in undo:
					viewportTransform *= t
				
		sdl2.SDL_RenderPresent(renderer)

	def frame_loop(self,renderer):
		last_frame = time.time()
		self.draw(renderer,0)
		while True:
			current_frame = time.time()
			frame_time = current_frame - last_frame
			all_events = sdl2.ext.get_events()
			for event in all_events:
				if event.type == sdl2.SDL_QUIT:
					return
				elif event.type == sdl2.SDL_KEYDOWN:
					key_code = event.key.keysym.sym
					if key_code == sdl2.SDLK_UP:
						self.LS_iterations += 1
						self.on_iteration_change(self.LS_iterations)
					elif key_code == sdl2.SDLK_DOWN:
						self.LS_iterations = max(self.LS_iterations-1, 0)
					self.draw(renderer,frame_time)
				elif event.type == sdl2.SDL_MOUSEMOTION:
					pass
				elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
					pass
				elif event.type == sdl2.SDL_MOUSEBUTTONUP:
					pass
			#self.draw(renderer,frame_time)
			last_frame = current_frame


if len(sys.argv) < 2:
	print 'Usage: python %s <input file>'%sys.argv[0]
	sys.exit(0)
	
filename = sys.argv[1]
try:
	L = LSystem(filename)
except LSystemParseException:
	print 'Error parsing %s'%filename
	sys.exit(0)

sdl2.ext.init()

window = sdl2.ext.Window("CSC 205 A3", size=(A3Canvas.CANVAS_SIZE_X, A3Canvas.CANVAS_SIZE_Y))
window.show()

renderer = sdl2.SDL_CreateRenderer(window.window, -1,0, sdl2.SDL_RENDERER_PRESENTVSYNC | sdl2.SDL_RENDERER_ACCELERATED);


sdl2.SDL_SetRenderDrawColor(renderer, 0, 255, 0, 255)
sdl2.SDL_RenderClear(renderer)
sdl2.SDL_RenderPresent(renderer)

canvas = A3Canvas(L)		
canvas.frame_loop(renderer)
		
sdl2.SDL_DestroyRenderer(renderer)
