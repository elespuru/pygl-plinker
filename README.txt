A very simple PyGame OpenGL shooter

By: Peter R. Elespuru
License: APL v2.0

Controls:
------------------------------------------------------------------------------
space                - begin
escape               - exit
left-click           - shoot
pgup/mousewheel up   - zoom the scope in 
pgdown/mousewheel dn - zoom the scope out 


Summary:
------------------------------------------------------------------------------
Developed on OS X, tested/confirmed on Ubuntu Linux. No idea if it'll have any
issues on Windows...

Interesting Things:
- the crosshair scope view (the zoom in/out aspect)

- circular viewport to support scope view
-- alpha blending vs. stencil buffer vs. multi-pass render

- the HUD (fading by alpha)

- hit detection: ray casting vs. selection buffer vs. color at cursor

Dependencies:
  Python 2.6+ - http://www.python.org/download/releases/2.6/
  PyGame      - http://www.pygame.org/
  PyOpenGL    - http://pyopengl.sourceforge.net/

To start the application, after installing the dependencies, issue
'python project.py' from within the directory. It opens in full screen
mode, and the control summary is above.

