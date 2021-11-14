from array import array

import numpy as np
import moderngl_window as mglw


class Window(mglw.WindowConfig):
    """
    Class that defines OpenGL window.
    More information:
    https://moderngl-window.readthedocs.io/en/latest/reference/context/windowconfig.html#moderngl_window.context.base.window.WindowConfig
    """
    gl_version = (3, 3)
    title = "SmartCanvas"
    window_size = (1280, 720)
    aspect_ratio = 16 / 9
    resizable = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture(Window.window_size, 3)]
        )

        self.program = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                in vec2 in_uv;
                out vec2 uv;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    uv = in_uv;
                }
            ''',
            fragment_shader='''
                #version 330

                uniform sampler2D image;

                out vec4 f_color;
                in vec2 uv;

                void main() {
                    vec4 color = texture(image, uv);
                    f_color = vec4(color.b, color.g, color.r, color.a);
                }
            ''',
        )

        self.vertices = self.ctx.buffer(
            array('f',
                  [
                      -1,  1, 0, 1,  # upper left
                      -1, -1, 0, 0,  # lower left
                      1,  1, 1, 1,  # upper right
                      1, -1, 1, 0,  # lower right
                  ])
        )

        self.quad = self.ctx.vertex_array(
            self.program,
            [
                (self.vertices, '2f 2f', 'in_vert', 'in_uv'),
            ]
        )
        # TODO/TOCHECK: internal parameter format. Might get better performance when using shorter format bc default includes alpha


    @classmethod
    def run(cls):
        mglw.run_window_config(cls)
