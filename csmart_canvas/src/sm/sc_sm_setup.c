#include <stdio.h>
#include <unistd.h>
#include <libgen.h>

#include "sc_video_capture.h"
#include "sc_filter.h"

#include "core/sc_core.h"
#include "sm/sc_sm.h"
#include "logging/sc_logging.h"
#include "sc_typedef.h"
#include "renderer/sc_builtin_shaders.h"
#include "renderer/sc_font.h"

/* declarations */
SC_LOCAL void sc_sm_setup_set_cwd(void);
SC_LOCAL sc_bool sc_sm_setup_create_window(void);
SC_LOCAL sc_bool sc_sm_setup_resource_init(void);

/* definitions */
SC_LOCAL void sc_sm_setup_set_cwd(void) {
    char current_path[1024] = {0};
    readlink("/proc/self/exe", current_path, sizeof(current_path) - 1);
    dirname(current_path);
    char current_directory[1024];

    if (chdir(current_path) != 0) {
        SC_FATAL("Failed to set working directory to '%s'", current_path);
    } else {
        if (getcwd(current_directory, sizeof(current_directory)) != NULL) {
            SC_TRC("Current working directory: %s", current_directory);
        }
    }

    if (chdir("../") != 0) {
        SC_FATAL("Failed to set working directory back");
    } else {
        if (getcwd(current_directory, sizeof(current_directory)) != NULL) {
            SC_TRC("Current working directory: %s", current_directory);
        }
    }
}

SC_LOCAL sc_bool sc_sm_setup_create_window(void) {

    /* Create a window */
    sc_bool       result  = SC_TRUE;
    SDL_Window*   window  = NULL;

    SC_TRC("Create window");

    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        SC_FATAL("SDL initialization failed: %s", SDL_GetError());
        result = SC_FALSE;
    }

    if (SC_TRUE == result) {
        const int flags = SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE;

        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3);
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);

        g_sc_context.window_width = 800;
        g_sc_context.window_height = 600;

        window = SDL_CreateWindow(
            "SmartCanvas",
            SDL_WINDOWPOS_UNDEFINED,
            SDL_WINDOWPOS_UNDEFINED,
            g_sc_context.window_width,
            g_sc_context.window_height,
            flags);

        g_sc_context.window = window;

        if (NULL == window) {
            SC_FATAL("Window creation failed: %s", SDL_GetError());
            result = SC_FALSE;
        }

        if (SC_TRUE == result) {
            g_sc_context.sdl_context = SDL_GL_CreateContext(window);

            glewExperimental = GL_TRUE;

            if (GLEW_OK != glewInit()) {
                SC_FATAL("GLEW init failed");
                result = SC_FALSE;
            }
        }
    }

    return result;
}

SC_LOCAL sc_bool sc_sm_setup_video_capture_init(void)
{
    sc_bool result = SC_TRUE;
    /* Open video capture */
    if (SC_TRUE == result) {
        SC_TRC("Open video capture");

        const uint32_t wanted_width = 1080;
        const uint32_t wanted_height = 720;
        result = sc_video_capture_init(wanted_width, wanted_height);

        SC_TRC("Open video capture result: %d", result);
    }

    sc_filter_set_worker_count(15);
    return result;
}

SC_LOCAL sc_bool sc_sm_setup_resource_init(void)
{
    sc_bool result = SC_TRUE;

    glGenVertexArrays(1, &g_sc_context.vao);
    glBindVertexArray(g_sc_context.vao);

    if (SC_TRUE == result) {
        SC_TRC("create video capture texture");

        struct sc_TextureConfig config =
            {
                .width           = 1,
                .height          = 1,
                .depth           = 1,
                .data            = NULL,
                .internal_format = GL_RGB8,
                .data_format     = GL_RED,
                .data_type       = GL_UNSIGNED_BYTE,
            };

        result = sc_make_texture(&config,
                                  &g_sc_context.texture_vc);

        SC_TRC("create result: %d", result);
    }

    if (SC_TRUE == result) {
        SC_TRC("create flat shader");
        struct sc_ShaderConfig config =
            {
                .vertex_src =  g_flat_shader_vert,
                .fragment_src = g_flat_shader_frag,
            };

        result = sc_make_shader(&config,
                                 &g_sc_context.shader_flat);
        SC_TRC("create result: %d", result);
    }

    if (SC_TRUE == result) {
        SC_TRC("create flat shader");
        struct sc_ShaderConfig config =
            {
                .vertex_src =  g_text_shader_vert,
                .fragment_src = g_text_shader_frag,
            };

        result = sc_make_shader(&config,
                                 &g_sc_context.shader_text);
        SC_TRC("create result: %d", result);
    }

    if (SC_TRUE == result) {
        SC_TRC("create font");

        result = sc_make_font("./data/ttf/OpenSans-Regular.ttf",
                               128,
                               &g_sc_context.font);
        SC_TRC("create result: %d", result);
    }
    return result;
}

void sc_sm_handle_input_in_setup(void)
{
    sc_sm_setup_set_cwd();
    sc_sm_setup_create_window();
    sc_sm_setup_video_capture_init();
    sc_sm_setup_resource_init();
    sc_sm_state_enter(SC_STATE_MACHINE_STATE_REAL_TIME);
}
