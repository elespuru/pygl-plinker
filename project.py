#!/usr/bin/env python
#
# A very simple PyGame OpenGL Shooter
#
# Peter R. Elespuru
# 
# Dependencies:
#  Python 2.6+ - http://www.python.org/download/releases/2.6/
#  PyGame      - http://www.pygame.org/
#  PyOpenGL    - http://pyopengl.sourceforge.net/
#
# Controls:
# ------------------------------------------------------------------------------
# space                - begin
# escape               - exit
# left-click           - shoot
# pgup/mousewheel up   - zoom the scope in 
# pgdown/mousewheel dn - zoom the scope out 
#

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
_default_width = 800
_default_height = 600
_screen = None
_elapsed_time = 0
_draw_hud_hit = 0
_hit = 0
_hit_alpha = 1.0
_woohoo_alpha = 1.0
_pixel_at_cursor = None
_target_hit_sound = None
_hit_list = {}
_intro_hud = True
_texture_map = {}
_target_z_pos = {}
_n_targets = 4
_all_targets_shot = 0

#
# it currently uses full screen mode, but development and test
# are still done in a window...
#
def resize((width, height)):
    global _viewport
    if height==0: height=1
    _viewport['minx'] = 0
    _viewport['miny'] = 0
    _viewport['maxx'] = width
    _viewport['maxy'] = height
    return

#
# given a reference name and filename, prepare the texture
# for future use
#
def prepare_texture(name, filename):
    global _textures
    glEnable(GL_TEXTURE_2D)
    _textures[name] = {}
    _textures[name]['img'] = pygame.image.load(os.path.join("textures",filename)).convert()
    _textures[name]['data'] = pygame.image.tostring(_textures[name]['img'], "RGBX", 1)
    _textures[name]['id'] = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, _textures[name]['id'])
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                 _textures[name]['img'].get_width(),
                 _textures[name]['img'].get_height(),
                 0, GL_RGBA, GL_UNSIGNED_BYTE,
                 _textures[name]['data'])
    glDisable(GL_TEXTURE_2D)
    return

#
# prepare all of the textures for future use
#
def prepare_textures():
    prepare_texture('woohoo','woohoo.jpg')
    prepare_texture('intro_hud','intro_hud.jpg')
    prepare_texture('ground','grass9.jpg')
    prepare_texture('backdrop','rockies.jpg')
    prepare_texture('hud_hit','hud_hit.jpg')
    prepare_texture('hud_miss','hud_miss.jpg')
    prepare_texture('target_oval','target_oval.jpg')
    prepare_texture('target_2tblue','target_2tblue.jpg')
    prepare_texture('target_ht','target_ht.jpg')
    prepare_texture('target_idpa','target_idpa.jpg')
    prepare_texture('target_redcenter','target_redcenter.jpg')
    for i in range(2,25,1):
        prepare_texture('hud_scope_'+str(i),'hud_scope_'+str(i)+'.jpg')
    return

#
# initial state is no targets have been hit
#
def inithitlist():
    global _hit_list
    _hit_list = {
        '001': False,
        '010': False,
        '011': False,
        '100': False,
        '101': False,
        '110': False,
        '111': False
    }
    return

#
# initialize z_position mapping
#
def initzpos():
    global _target_z_pos
    _target_z_pos = {
        '001': 0,
        '010': 0,
        '011': 0,
        '100': 0,
        '101': 0,
        '110': 0,
        '111': 0
    }
    return    

#
# prep all the initial configuration
#
def initialize():
    global _target_hit_sound, _gunshot, _display, _default_width, _default_height, _clock
#    video_flags = OPENGL|DOUBLEBUF|RESIZABLE|FULLSCREEN
    video_flags = OPENGL|DOUBLEBUF|RESIZABLE
    pygame.mixer.pre_init(channels=1)
    pygame.init()
    _clock = pygame.time.Clock()
    _display = pygame.display.set_mode((_default_width,_default_height), video_flags)
    _target_hit_sound = pygame.mixer.Sound(os.path.join("sounds","hit.wav"))
    _target_hit_sound.set_volume(0.7)
    _gunshot = pygame.mixer.Sound(os.path.join("sounds","sniper.wav"))
    _gunshot.set_volume(1)
    ambient = pygame.mixer.Sound(os.path.join("sounds","forest2.wav"))
    ambient.set_volume(0.3)
    ambient.play(-1)
    resize((_default_width,_default_height))
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE | GLUT_ALPHA | GLUT_STENCIL)
    pygame.mouse.set_visible(False)
    pygame.time.set_timer(pygame.USEREVENT, int(1000.0/30.0))
    glShadeModel(GL_SMOOTH)
    glClearColor(0.5, 0.5, 0.5, 0.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    prepare_textures()
    inithitlist()
    initzpos()
    return

#
# rather than use a skybox, since my scene is static, just draw 
# a backdrop on a planar quad
#
def draw_backdrop():
    global _display
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, _textures['backdrop']['id'])
    glBegin(GL_QUADS)
    glColor3f(1,1,1)
    width, height = _display.get_size()
    glTexCoord2f(1,0); glVertex3f(-width+350,-5,800)
    glTexCoord2f(0,0); glVertex3f(width-350,-5,800)
    glTexCoord2f(0,1); glVertex3f(width-350,(height/1.8)+5,800)
    glTexCoord2f(1,1); glVertex3f(-width+350,(height/1.8)+5,800)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    return

#
# draw the grass/ground
#
def draw_ground():
	# the ground
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, _textures['ground']['id'])
    glBegin(GL_QUADS)
    glColor3f(0, 0.5, 0)
    glTexCoord2f(0,   0);   glVertex3f(-10000, -1, -10000)
    glTexCoord2f(0,   500); glVertex3f(-10000, -1,  10000)
    glTexCoord2f(500, 500); glVertex3f( 10000, -1,  10000)
    glTexCoord2f(500, 0);   glVertex3f( 10000, -1, -10000)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    return
		
#
# draw the basic 4 point/diamond target
#
def draw_basic_target(r,g,b,xoffset=0,zdist=0,sel=0):
    glLoadName(sel)
    glBegin(GL_QUADS)
    glColor3f(r,g,b)
    glVertex3f( 0+xoffset, -3, zdist)
    glVertex3f(-5+xoffset,  2, zdist)
    glVertex3f( 0+xoffset,  7, zdist)
    glVertex3f( 5+xoffset,  2, zdist)
    glEnd()
    return

#
# draw a rectangular target
#
def draw_rectangle_target(r,g,b,xoffset=0,zdist=0,zmodifier=0,xmod=0):
    global _elapsed_time, _target_z_pos
    zmod = (zmodifier*_elapsed_time) / 100
    zdist = 70 + ((zmod/1.5) % 700)
    glBegin(GL_QUADS)
    glColor3f(r,g,b)
    glVertex3f( 0+xoffset, 0, zdist)
    glVertex3f(-5+xoffset, 0, zdist)
    glVertex3f(-5+xoffset, 10, zdist)
    glVertex3f( 0+xoffset, 10, zdist)
    glEnd()
    
#
# draw a triangular target
#
def draw_triangle_target(r,g,b,xoffset=0,zdist=0,orient=0):
    glBegin(GL_QUADS)
    glColor3f(r,g,b)
    if orient:
        glVertex3f( 0+xoffset, 0, zdist)
        glVertex3f(-5+xoffset, 5, zdist)
        glVertex3f( 0+xoffset, 0, zdist)
        glVertex3f( 5+xoffset, 5, zdist)
    else:
        glVertex3f( 0+xoffset, 5, zdist)
        glVertex3f(-5+xoffset, 0, zdist)
        glVertex3f( 0+xoffset, 5, zdist)
        glVertex3f( 5+xoffset, 0, zdist)
    glEnd()

#
# draw a textured rectangular target
#
def draw_rectangle_textured_target(r,g,b,xoffset=0,zdist=0,texture=None,zmodifier=0,xmod=0):
    global _textures, _elapsed_time, _intro_hud
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ZERO)
    glBindTexture(GL_TEXTURE_2D, _textures[texture]['id'])
    glBegin(GL_QUADS)
    glColor4f(1,1,1,1)
    zmod = (zmodifier*_elapsed_time) / 100
    zdist = 70 + ((zmod/1.5) % 700)
    glTexCoord2f(1,0); glVertex3f( 0+xoffset, 0, zdist)
    glTexCoord2f(0,0); glVertex3f(-5+xoffset, 0, zdist)
    glTexCoord2f(0,1); glVertex3f(-5+xoffset, 10, zdist)
    glTexCoord2f(1,1); glVertex3f( 0+xoffset, 10, zdist)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    return
    
#
# draw a textured target using given parameters
#
def draw_tex_target(r,g,b, tex,x,z,texname,zmod,xmod):
    global _hit_list
    if not _hit_list[str(r)+str(g)+str(b)]:
        if tex: draw_rectangle_textured_target(r,g,b, x,z, texname,zmod,xmod)
        else: draw_rectangle_target(r,g,b, x,z,zmod,xmod)
    return

#
# draw the targets on the scene
#
def draw_targets(tex=0):
    global _n_targets, _intro_hud
    if _intro_hud: return
    r = 0; g = 0; b = 1; x = -10; z = 500; zmod = 3; xmod = 0
    draw_tex_target(r,g,b, tex,x,z,'target_oval',zmod,xmod)
    r = 0; g = 1; b = 0; x = 100; z = 400; zmod = 6; xmod = 1
    draw_tex_target(r,g,b, tex,x,z,'target_2tblue',zmod,xmod)
    r = 0; g = 1; b = 1; x = -50; z = 200; zmod = 2; xmod = 0
    draw_tex_target(r,g,b, tex,x,z,'target_ht',zmod,xmod)
    r = 1; g = 0; b = 0; x = -60; z = 300; zmod = 4; xmod = 1
    draw_tex_target(r,g,b, tex,x,z,'target_idpa',zmod,xmod)
    r = 1; g = 0; b = 1; x = 30; z = 250; zmod = 3; xmod = 0
    draw_tex_target(r,g,b, tex,x,z,'target_redcenter',zmod,xmod)
    r = 1; g = 1; b = 0; x = -30; z = 400; zmod = 8; xmod = 1
    draw_tex_target(r,g,b, tex,x,z,'target_redcenter',zmod,xmod)
    r = 1; g = 1; b = 1; x = 60; z = 300; zmod = 4; xmod = 0
    draw_tex_target(r,g,b, tex,x,z,'target_redcenter',zmod,xmod)
    _n_targets = 7
    return

#
# draw the outdoor scene
#
def draw_outdoor_scene(tex=0):
    draw_backdrop()
    draw_ground()
    draw_targets(tex)
    return

#
# draw the scene, just calls another method at the moment
# in case I made it far enough to have multiple scenes, such
# as an indoor range as well as the outdoor one. Didn't make
# it that far...
#
def draw_scene(tex=0):
    draw_outdoor_scene(tex)
    return

#
# Draw the unmagnified 'real' view of the world
#
def draw_normal_view(sel=0):
    view = glGetIntegerv(GL_VIEWPORT)
    (x,y) = pygame.mouse.get_pos()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if sel: gluPickMatrix(x, view[3]-y, 1, 1, view)
    gluPerspective(_fov, 1.0*_viewport['maxx']/_viewport['maxy'], 0.5, 10000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 10, 0,
              0, 0, 500,
              0, 1, 0)
    draw_scene(1)
    return

#
# draw the larger outer portion of the crosshairs, and the first disk
#
def draw_crosshairs_outer():
    glLineWidth(3.0)
    glColor3f(0,0,0)
    glBegin(GL_LINES)
    glVertex3f(-1.0,  0.0, 0.0)
    glVertex3f(-0.3,  0.0, 0.0)
    glVertex3f(0.3,  0.0, 0.0)
    glVertex3f(1.0,  0.0, 0.0)
    glVertex3f( 0.0, -1.0, 0.0)
    glVertex3f( 0.0,  -0.3, 0.0)
    glVertex3f( 0.0, 0.3, 0.0)
    glVertex3f( 0.0,  1.0, 0.0)
    glEnd()
    return

#
# draw the finer/smaller inner portion of the crosshair
#
def draw_crosshairs_inner():
    glColor3f(1,0,0)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    glVertex3f(-0.3,  0.0, 0.0)
    glVertex3f(0.3,  0.0, 0.0)
    glVertex3f( 0.0, -0.3, 0.0)
    glVertex3f( 0.0, 0.3, 0.0)
    glEnd()
    return

#
# overlay a texture on the crosshair, to provide a slightly different
# view than vanilla, such as night vision, or thermal etc.
#
def overlay_texture():
    global _textures
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE)
    glBindTexture(GL_TEXTURE_2D, _textures['scopemask']['id'])
    glBegin(GL_QUADS)
    glColor4f(1,1,1,1)
    glTexCoord2f(0,0); glVertex3f(-1,-1,0)
    glTexCoord2f(1,0); glVertex3f( 1,-1,0)
    glTexCoord2f(1,1); glVertex3f( 1, 1,0)
    glTexCoord2f(0,1); glVertex3f(-1, 1,0)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    return

#
# draw the entire crosshair
#
def draw_crosshairs():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    draw_crosshairs_outer()
    draw_crosshairs_inner()
    return

#
# get an r,g,b triplet from a given pixel
#
def normalize_pixel(pixel=None):
    if pixel is None: return
    i = 16777216
    try: 
        r = (pixel[0][0][0]/i)
        g = (pixel[0][0][1]/i)
        b = (pixel[0][0][2]/i)
    except IndexError:
        r = 0; g = 0; b = 0
    return [r,g,b]

#
# draw a disk of given diameter
#
def draw_disk(diameter=0):
    glPushMatrix()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-10.0, 10.0, -10.0, 10.0, -10.0, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glColor3f(1,1,1)
    gluDisk(gluNewQuadric(),diameter-2,diameter,64,64)
    glPopMatrix()
    return
    
#
# draw a square of given dim, which is both width and height
#
def draw_rect(dim=0):
    glPushMatrix()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-10.0, 10.0, -10.0, 10.0, -10.0, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glColor3f(1,1,1)
    glRecti(-dim,-dim,dim,dim)
    glPopMatrix()
    return

#
# Draw the zoomed/scope view of the world in a smaller region centered
# on the mouse cursor
#
def draw_zoomed(sel=None):
    global _viewport, _zoom, _fov, _pixel_at_cursor
    (x,y) = pygame.mouse.get_pos()
    projMatrix = glGetDoublev(GL_PROJECTION_MATRIX)
    modelViewMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    view = glGetIntegerv(GL_VIEWPORT)
    glViewport(x-50, (_viewport['maxy']-y)-50, 100, 100)
    glScissor(x-50, (_viewport['maxy']-y)-50, 100, 100)
    glEnable(GL_SCISSOR_TEST)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if sel: gluPickMatrix(x, view[3]-y, 1, 1, view)
    adjustment = sqrt(2.0)/2.0
    gluPerspective((_fov/(float(_viewport['maxx'])/100.0))/(adjustment*_zoom), 1.0, 0.1*_zoom, 1000.0*_zoom)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    (objx,objy,objz) = gluUnProject(float(x),(_viewport['maxy']-float(y)),1.0,modelViewMatrix,projMatrix,view)
    gluLookAt(0, 10, 0, objx, objy, objz, 0, 1, 0)
    draw_scene(0)
    _pixel_at_cursor = normalize_pixel(glReadPixels(x, view[3]-y, 1, 1, GL_RGB, GL_UNSIGNED_INT))
    draw_scene(1)
    draw_crosshairs()
    glDisable(GL_SCISSOR_TEST)
    return

#
# 
#
def draw_scoped_view(sel=0):
    glPushMatrix()
    draw_zoomed()
    glPopMatrix()
    return

#
# draw the circular mask that hides the corners of the zoomed 
# viewport, so that it's more akin to an actual scope reticle
#
def draw_mask():
    glPushMatrix()
    glDisable(GL_DEPTH_TEST)
    (x,y) = pygame.mouse.get_pos()
    glViewport(x-75, (_viewport['maxy']-y)-75, 150, 150)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-25.0, 25.0, -25.0, 25.0, -25.0, 25.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glColor3f(0,0,0)
    gluDisk(gluNewQuadric(),16,20,64,64)
    glColor3f(1,1,1)
    gluDisk(gluNewQuadric(),20,24,64,64)
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)
    return

#
# display the text in the lower left corner
# with 'hit' or 'miss' appropriately
#
def draw_hud_hit_miss(alpha=None):
    global _hit, _textures, _draw_hud_hit
    if not _draw_hud_hit: return
    hud_tex = ''
    glPushMatrix()
    x_offset = 50
    y_offset = -165
    if _hit: 
        hud_tex = 'hud_hit'
    else:
        hud_tex = 'hud_miss'
    glTranslate(x_offset,y_offset,0)
    glBindTexture(GL_TEXTURE_2D, _textures[hud_tex]['id'])
    glBegin(GL_QUADS)
    glColor4f(1,1,0,alpha)
    glTexCoord2f(1,0); glVertex3f(25,50,300)
    glTexCoord2f(0,0); glVertex3f(125,50,300)
    glTexCoord2f(0,1); glVertex3f(125,74,300)
    glTexCoord2f(1,1); glVertex3f(25,74,300)
    glEnd()
    glPopMatrix()
    return

#
# draw the text in the lower right corner
# which displays the current zoom/power level
#
def draw_hud_scope_power():
    global _zoom, _textures
    glPushMatrix()
    x_offset = -140
    y_offset = -130
    texture = 'hud_scope_'+str(int(_zoom))
    glTranslate(x_offset,y_offset,0)
    glBindTexture(GL_TEXTURE_2D, _textures[texture]['id'])
    glBegin(GL_QUADS)
    glColor4f(1,1,0,1)
    glTexCoord2f(1,0); glVertex3f(25,50,200)
    glTexCoord2f(0,0); glVertex3f(125,50,200)
    glTexCoord2f(0,1); glVertex3f(125,74,200)
    glTexCoord2f(1,1); glVertex3f(25,74,200)
    glEnd()
    glPopMatrix()
    return

#
# display text in the center of the screen
# when all targets are gone
#
def draw_hud_woohoo(alpha=None):
    global _zoom, _textures, _all_targets_shot
    if _all_targets_shot == 0: return
    glPushMatrix()
    x_offset = -75
    y_offset = -50
    glTranslate(x_offset,y_offset,0)
    glBindTexture(GL_TEXTURE_2D, _textures['woohoo']['id'])
    glBegin(GL_QUADS)
    glColor4f(1,1,0,alpha)
    glTexCoord2f(1,0); glVertex3f(25,50,100)
    glTexCoord2f(0,0); glVertex3f(125,50,100)
    glTexCoord2f(0,1); glVertex3f(125,74,100)
    glTexCoord2f(1,1); glVertex3f(25,74,100)
    glEnd()
    glPopMatrix()
    return

#
# draw the text shown initially after starting the game
#
def draw_intro_hud():
    global _textures, _intro_hud
    if not _intro_hud: return
    glPushMatrix()
    x_offset = -200
    y_offset = -180
    texture = 'intro_hud'
    view = glGetIntegerv(GL_VIEWPORT)
    glTranslate(x_offset,y_offset,0)
    glColor4f(1,1,0,1)
    glBindTexture(GL_TEXTURE_2D, _textures[texture]['id'])
    glBegin(GL_QUADS)
    glTexCoord2f(1,0); glVertex3f(0,0,350)
    glTexCoord2f(0,0); glVertex3f(view[2]/2,0,350)
    glTexCoord2f(0,1); glVertex3f(view[2]/2,view[3]/2,350)
    glTexCoord2f(1,1); glVertex3f(0,view[3]/2,350)
    glEnd()
    glPopMatrix()
    return

#
# the HUD will use textured quads so that they can be manipulated using
# normal OpenGL calls
#
def draw_hud():
    global _hit_alpha, _woohoo_alpha
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE)
    draw_hud_scope_power()
    draw_hud_hit_miss(_hit_alpha)
    draw_intro_hud()
    draw_hud_woohoo(_woohoo_alpha)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    return

#
# perform the after a target hit tasks
#
def hit_hud(hit=None):
    global _hit, _draw_hud_hit, _hit_alpha
    _hit = hit
    _hit_alpha = 1
    _draw_hud_hit = pygame.time.get_ticks()
    return

#
# the hit or miss hud needs to fade out gradually
# this function modifies the alpha value of the element
# until a 3s timer elapses, after which the hud element
# is removed entirely
#
def update_hit_hud(elapsed_time=None):
    global _draw_hud_hit, _hit_alpha
    hit_duration = elapsed_time - _draw_hud_hit
    hit_duration = hit_duration / 1000.0
    if hit_duration > 3: _draw_hud_hit = 0
    else: _hit_alpha -= 0.025
    return

#
# the woohoo hud needs to fade out gradually
# this function modifies the alpha value of the element
# until a 3s timer elapses, after which the hud element
# is removed entirely
#
def update_woohoo_hud(elapsed_time=None):
    global _all_targets_shot, _woohoo_alpha
    if _all_targets_shot == 0: return
    hit_duration = elapsed_time - _all_targets_shot
    hit_duration = hit_duration / 1000.0
    if hit_duration > 3:
        _all_targets_shot = 0
        _woohoo_alpha = 1.0
        inithitlist()
    else: _woohoo_alpha -= 0.01
    return

#
# update each hud component that has a time component
#
def update_hud(elapsed_time=None):
    update_hit_hud(elapsed_time)
    update_woohoo_hud(elapsed_time)
    return

#
# initial display function, calls the others after clearing
#
def display():
    global _viewport, _intro_hud
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glViewport(_viewport['minx'], _viewport['miny'],_viewport['maxx'], _viewport['maxy'])
    draw_normal_view()
    draw_hud()
    if not _intro_hud:
        draw_scoped_view()
        draw_mask()
    return
    
#
# check to see if there are any targets remaining un-shot
#
def checkhits():
    global _hit_list, _n_targets, _all_targets_shot
    hit_count = 0
    for target,state in _hit_list.iteritems():
        if state == True: hit_count +=1
    if hit_count == _n_targets:
        _all_targets_shot = pygame.time.get_ticks()
    return

#
# there are several ways to do this including ray cast,
# opengl selection/picking, and pixel color at mouse cursor
# I didn't try ray casting and selection/picking is deprecated
# so I went with color at mouse cursor. 
#
def checkhit(hit=None):
    global _hit_list, _target_hit_sound
    if hit != None:
        if hit[0] == 255 or hit[1] == 255 or hit[2] == 255:
            if hit[0] == 255: r = 1
            else: r = 0
            if hit[1] == 255: g = 1
            else: g = 0
            if hit[2] == 255: b = 1
            else: b = 0
            _hit_list[str(r)+str(g)+str(b)] = True
            _target_hit_sound.play()
            checkhits()
            return 1
    return 0

#
# call display, flip the double buffer
#
def refresh():
    display()
    pygame.display.flip()
    return

#
# modify the scope's zoom
#
def scope_zoom_in():
    global _zoom
    _zoom += 1.0
    if _zoom > 24.0:
    	_zoom = 24.0
    return
    
#
# modify the scope's zoom
#
def scope_zoom_out():
    global _zoom
    _zoom -= 1.0
    if _zoom < 2.0:
    	_zoom = 2.0
    return

#
# appropriately respond to keyboard input
#
def process_key(key):
    global _intro_hud
    if key == 280:
        scope_zoom_in()
    elif key == K_ESCAPE:
		sys.exit(0)
    elif key == 281:
        scope_zoom_out()
    elif key == 32:
        _intro_hud = False
    else:
        pass
        #print 'key:' + str(key)
    return

#
# handle a mouse left-click
#
def left_click():
    global _gunshot, _pixel_at_cursor
    _gunshot.play()
    if checkhit(_pixel_at_cursor): hit_hud(1)
    else: hit_hud(0)
    return

#
# appropriately respond to mouse input
#
def process_mousebtn(button=None,position=None):
    if button == 1:
        left_click()
    elif button == 4:
        scope_zoom_in()
    elif button == 5:
        scope_zoom_out()
    else:
        pass
        #print 'mouse:' + str(button)
    return

#
# currently runs fullscreen, but test and development run/ran
# in window mode and need to properly honor resize
#
def process_resize(width,height):
    resize((width,height))
    refresh()
    return

#
# the main game loop, farms out to appropriate functions based 
# on what has taken place
#
def game_loop():
    global _elapsed_time, _clock, _hit
    while 1:
        _elapsed_time = pygame.time.get_ticks()
        update_hud(_elapsed_time)
        event = pygame.event.wait()
        if event.type == QUIT:
            sys.exit(0);
        if event.type == KEYDOWN:
			process_key(event.key)
        if event.type == USEREVENT:
            refresh()
        if event.type == MOUSEMOTION:
            refresh()
        if event.type == MOUSEBUTTONDOWN:
			process_mousebtn(event.button, event.pos)
        if event.type == VIDEORESIZE:
			process_resize(event.w,event.h)
        if event.type == VIDEOEXPOSE:
            refresh()
    return

#
# here. we. go.
#
def main():
	initialize()
	game_loop()
	return

if __name__ == '__main__':
    main()
