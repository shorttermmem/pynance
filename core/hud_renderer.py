import numpy as np
import pygame as pg
import moderngl as mgl
from memory_profiler import profile
from .shader_program import HUDShaderProgram


class FPSLabel:
    def __init__(self, app, renderer):
        self.app = app
        self.font = renderer.font

        self.clear_color = (0.1, 0.1, 0.1, 0.2)
        self.box_color = (0.078, 0.824, 0.431, 0.3)

        # Vertex Buffer Object (VBO)
        self.vbo = self.app.ctx.buffer(np.empty(16, dtype='f4'))
        # Vertex Array Object (VAO)
        self.vao = self.app.ctx.simple_vertex_array(
            renderer.shader_program.programs['hud'], self.vbo, 'in_position', 'in_texcoord'
        )

    # @profile
    def render(self, text):
        # Check if the new text has different dimensions
        text_size = self.font.size(text)
        pg_surface = self.font.render(text, True, (0, 1, 2))

        # Convert Pygame surface to ModernGL texture
        pg_bytes = pg.image.tostring(pg_surface, 'RGBA', True)
        mgl_texture = self.app.ctx.texture(pg_surface.get_size(), 4)
        mgl_texture.filter = (mgl.LINEAR, mgl.LINEAR)
        mgl_texture.write(pg_bytes)

        # Calculate position for top right corner with padding
        padding = 10
        scale_x = text_size[0] / self.app.WIN_SIZE[0]
        scale_y = text_size[1] / self.app.WIN_SIZE[1]
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
        mgl_texture.use(0)

        self.vao.render(mgl.TRIANGLE_STRIP)

    def destroy(self):
        """release texture objects"""
        self.vbo.release()
        self.vao.release()


class HUDRenderer:
    def __init__(self, app):
        self.app = app
        self.shader_program = HUDShaderProgram(app.ctx)

        # Initialize Pygame font
        pg.font.init()
        self.font = pg.font.SysFont('arial', 24)

        self.FPSLabel = FPSLabel(app, self)

    def render(self, text):
        # Setup HUD rendering state
        self.app.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.app.ctx.enable(mgl.BLEND)
        self.FPSLabel.render(text)

    def destroy(self):
        """release texture objects"""
        self.FPSLabel.destroy()
