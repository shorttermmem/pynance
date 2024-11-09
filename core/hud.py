import numpy as np
import moderngl as mgl

class HUD:
    def __init__(self, app):
        self.app = app
        
        self.clear_color = (0.1, 0.1, 0.1, 1)
        self.box_color = (0.078, 0.824, 0.431, 1.0)

        # Define vertices of the box
        self.quad_vertices = np.array([
            -1, -1, 0.0, 1.0,  # Bottom-left corner
            1, -1, 0.0, 1.0,   # Bottom-right corner
            -1,  1, 0.0, 1.0,  # Top-left corner
            1,  1, 0.0, 1.0    # Top-right corner
        ], dtype='f4')

        # Create and bind the Vertex Buffer Object (VBO)
        self.vbo = self.app.ctx.buffer(self.quad_vertices)

        # Create Shader Program
        self.shader_program = self.app.ctx.program(
            vertex_shader='''
            #version 330 core
            in vec4 in_vert;
            void main() {
                gl_Position = in_vert;
            }
            ''',
            fragment_shader='''
            #version 330 core
            out vec4 fragColor;
            uniform vec4 u_color;
            void main() {
                fragColor = u_color;
            }
            '''
        )

        # Vertex Array Object (VAO)
        self.vao = self.app.ctx.simple_vertex_array(
            self.shader_program, self.vbo, 'in_vert'
        )

    def render(self):
        self.app.ctx.clear(*self.clear_color)
        self.app.ctx.enable(mgl.BLEND)
        self.app.ctx.blend_func = (mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA)
        self.shader_program['u_color'].value = self.box_color
        self.vao.render(mgl.TRIANGLE_STRIP)