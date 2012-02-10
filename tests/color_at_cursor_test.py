#!/usr/bin/env python

import pygame, sys, os.path, pygame.time, pygame.mixer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from pygame.locals import *
from math import sqrt

_viewport = {}
_textures = {}
_zoom = 2.0
_gunshot = None
_fov = 45.0
_default_width = 640
_default_height = 480
_screen = None
_elapsed_time = 0
_draw_hud_hit = 0
_hit = 0
_hit_alpha = 1.0

def resize((width, height)):
    global _viewport
    if height==0: height=1
    _viewport['minx'] = 0
    _viewport['miny'] = 0
    _viewport['maxx'] = width
    _viewport['maxy'] = height
    return

def initialize():
    global _gunshot, _display, _default_width, _default_height, _clock
    video_flags = OPENGL|DOUBLEBUF|RESIZABLE#|FULLSCREEN
    pygame.init()
    _display = pygame.display.set_mode((_default_width,_default_height), video_flags)
    resize((_default_width,_default_height))
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE | GLUT_ALPHA);
    pygame.time.set_timer(pygame.USEREVENT, int(1000.0/30.0))
    glShadeModel(GL_FLAT)
    glClearColor(0, 0, 0, 0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    return
    
def drawTriangle (x1, y1, x2, y2, x3, y3, z):
    glBegin(GL_TRIANGLES)
    glVertex3f(x1, y1, z)
    glVertex3f(x2, y2, z)
    glVertex3f(x3, y3, z)
    glEnd()
    return

def drawViewVolume (x1, x2, y1, y2, z1, z2):
    glColor3f (1.0, 1.0, 1.0)
    glBegin (GL_LINE_LOOP)
    glVertex3f (x1, y1, -z1)
    glVertex3f (x2, y1, -z1)
    glVertex3f (x2, y2, -z1)
    glVertex3f (x1, y2, -z1)
    glEnd ()

    glBegin (GL_LINE_LOOP)
    glVertex3f (x1, y1, -z2)
    glVertex3f (x2, y1, -z2)
    glVertex3f (x2, y2, -z2)
    glVertex3f (x1, y2, -z2)
    glEnd ()

    glBegin (GL_LINES)
    glVertex3f (x1, y1, -z1)
    glVertex3f (x1, y1, -z2)
    glVertex3f (x1, y2, -z1)
    glVertex3f (x1, y2, -z2)
    glVertex3f (x2, y1, -z1)
    glVertex3f (x2, y1, -z2)
    glVertex3f (x2, y2, -z1)
    glVertex3f (x2, y2, -z2)
    glEnd ()
    return

def drawScene():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40.0, 4.0/3.0, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(7.5, 7.5, 12.5, 2.5, 2.5, -5.0, 0.0, 1.0, 0.0)
    glColor3f(1, 0, 0)
    drawTriangle(2.0, 2.0, 3.0, 2.0, 2.5, 3.0, -5.0)
    glColor3f(0, 1, 0)
    drawTriangle(2.0, 7.0, 3.0, 7.0, 2.5, 8.0, -5.0)
    glColor3f(0, 0, 1)
    drawTriangle(2.0, 2.0, 3.0, 2.0, 2.5, 3.0, -1.0)
    drawViewVolume(0.0, 5.0, 0.0, 5.0, 0.0, 10.0)
    return

def selectObjects():
    (x,y) = pygame.mouse.get_pos()
    projMatrix = glGetDoublev(GL_PROJECTION_MATRIX)
    modelView = glGetDoublev(GL_MODELVIEW_MATRIX)
    view = glGetIntegerv(GL_VIEWPORT)

#    gluPickMatrix(x, view[3]-y, 1, 1, view)

    pixels = glReadPixels(x, view[3]-y, 1, 1, GL_RGB, GL_UNSIGNED_INT)
    if pixels != None:
        print 'p:' + str(pixels)
    return

def display():
    global _viewport
    glClearColor (0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    drawScene()
    glFlush()
    return

def process_key(key):
    if key == K_ESCAPE:
		sys.exit(0)
    return

def process_mousebtn(button=None,position=None):
    if button == 1:
        selectObjects()
    return

def game_loop():
    while 1:
        event = pygame.event.wait()
        if event.type == QUIT:
            sys.exit(0);
        if event.type == KEYDOWN:
			process_key(event.key)
        if event.type == MOUSEBUTTONDOWN:
			process_mousebtn(event.button, event.pos)
        display()
#        pygame.display.flip()
    return

def main():
	initialize()
	game_loop()
	return

if __name__ == '__main__':
    main()
