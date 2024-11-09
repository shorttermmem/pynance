# 3D-Graphics-Engine
OpenGL Graphics Engine in Python ( Pygame, ModernGL ) 

![opengl](/screenshot/0.jpg)

## Pre-requisite

#### moderngl module requires OpenGL runtime. 
```shell
sudo apt install libgl1-mesa-dev libglu1-mesa-dev libglew-dev
```

#### Setup
```shell
python -m pip install -e .
```

#### Appmap code visualization
```shell
pip install --require-virtualenv appmap 
appmap-python --record process python -m main
```