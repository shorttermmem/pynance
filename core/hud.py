import numpy as np
import pygame as pg
import moderngl as mgl
from memory_profiler import profile

class HUD:
    def __init__(self, app):
        self.app = app
        
        # Initialize Pygame font
        pg.font.init()
        self.font = pg.font.SysFont('arial', 24)
        
        self.clear_color = (0.1, 0.1, 0.1, 0.2)
        self.box_color = (0.078, 0.824, 0.431, 0.3)

        # Create Shader Program
        self.shader_program = self.app.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_position;
                in vec2 in_texcoord;
                out vec2 v_texcoord;
                
                void main() {
                    gl_Position = vec4(in_position, 0.0, 1.0);
                    v_texcoord = in_texcoord;
                }
            ''',
            fragment_shader='''
                #version 330
                uniform sampler2D texture0;
                in vec2 v_texcoord;
                out vec4 f_color;
                
                void main() {
                    f_color = texture(texture0, v_texcoord);
                }
            '''
        )
                
        # Define vertices of the box
        self.quad_vertices = np.array([
            -1, -1, 0.0, 1.0,  # Bottom-left corner
            1, -1, 0.0, 1.0,   # Bottom-right corner
            -1,  1, 0.0, 1.0,  # Top-left corner
            1,  1, 0.0, 1.0    # Top-right corner
        ], dtype='f4')

        # Create and bind the Vertex Buffer Object (VBO)
        self.vbo = self.app.ctx.buffer(self.quad_vertices)

        # Vertex Array Object (VAO)
        self.vao = self.app.ctx.simple_vertex_array(
            self.shader_program, self.vbo, 'in_position', 'in_texcoord'
        )
        
    @profile
    def _draw_text(self, text: str):
        """2D render text a texture"""
        
        # Setup HUD rendering state
        self.app.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.app.ctx.enable(mgl.BLEND)
        
        text_surface = self.font.render(text, True, (0, 1, 2))
        text_width, text_height = text_surface.get_size()
        
        # Convert Pygame surface to ModernGL texture
        text_data = pg.image.tostring(text_surface, 'RGBA', True)
        self.texture = self.app.ctx.texture((text_width, text_height), 4)
        self.texture.write(text_data)
        self.texture.filter = (mgl.LINEAR, mgl.LINEAR)
        
        # Calculate position for top right corner with padding
        padding = 10
        scale_x = text_width / self.app.WIN_SIZE[0]
        scale_y = text_height / self.app.WIN_SIZE[1]
        x_pos = 1 - (scale_x * 2) - (padding * 2 / self.app.WIN_SIZE[0])
        y_pos = 1 - (scale_y * 2) - (padding * 2 / self.app.WIN_SIZE[1])
        
        # Update vertex positions for the text quad
        vertices = np.array([
            # positions                                  # texture coords
            x_pos,               y_pos + scale_y * 2,    0.0, 1.0,  # top left
            x_pos + scale_x * 2, y_pos + scale_y * 2,    1.0, 1.0,  # top right
            x_pos,               y_pos,                  0.0, 0.0,  # bottom left
            x_pos + scale_x * 2, y_pos,                  1.0, 0.0,  # bottom right
        ], dtype='f4')
        
        self.vbo.write(vertices.tobytes())
        
        # Bind texture and render
        self.texture.use(0)
        self.vao.render(mgl.TRIANGLE_STRIP)
        
        # Restore previous OpenGL state
        #self.app.ctx.disable(mgl.BLEND)
        #self.app.ctx.enable(mgl.DEPTH_TEST)
        #self.app.ctx.depth_mask = depth_mask
        #self.app.ctx.blend_func = blend_func
        #self.texture.release()
        
    def render(self, text):
        #self.app.ctx.clear(*self.clear_color)
        self._draw_text(text)
        self.vao.render(mgl.TRIANGLE_STRIP)
        
    def destroy(self):
        """release texture objects"""
        self.texture.release()
        