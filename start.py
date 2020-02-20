import subprocess
import os
import time
import sys
import platform

system = platform.system()

eta_path = os.path.normpath("../eta")
bw_path = os.path.dirname(os.path.abspath(__file__))

params = []

if '-bo' not in sys.argv:
	os.chdir(eta_path)
	if system == 'Windows':
		os.system("start cmd.exe /c sbcl --load start.lisp")
	else:
		os.system("sbcl --load start.lisp &")

	os.system("start cmd.exe /c python C:\\Users\\user\\quicklisp\\local-projects\\ulf2english\\python-repl-server.py 8080 \"g:g\"")

	time.sleep(5.0)
	os.chdir(bw_path)
else:
	params.append('-bo')

if '-s' in sys.argv:
	params.append('-s')

if '-d' in sys.argv:
	params.append('-d')

if '-bg' not in sys.argv:
	command = ['blender', 'bw_scene.blend', '-P', 'main.py', '--'] + params	
else:
	command = ['blender', '--background', 'bw_scene.blend', '-P', 'main.py', '--'] + params

subprocess.call(command)