#ifndef SC_CORE_H
#define SC_CORE_H

#include <stdint.h>
#include <SDL2/SDL.h>
#include <GL/glew.h>

#include "sc_typedef.h"

#include "renderer/sc_renderer.h"
#include "sm/sc_sm.h"

enum SC_FILTER_TYPE {
    SC_FILTER_TYPE_NONE = 0,
    SC_FILTER_TYPE_OIL_PAINTING,
    SC_FILTER_TYPE_CANVAS,
    SC_FILTER_TYPE_SKETCH,
    SC_FILTER_TYPE_WATER_COLOR,
    SC_FILTER_TYPE_MOSAIC,
    SC_FILTER_TYPE_COUNT,
};

struct sc_Config {
    sc_bool is_debug;
};

struct sc_Context {
    uint64_t      frame_count;
    SDL_Window*   window;
    uint32_t      window_width;
    uint32_t      window_height;
    SDL_GLContext sdl_context;

    struct sc_StateMachine core_sm;
    enum SC_FILTER_TYPE    current_filter;

    struct {
        uint64_t filter;
    } timing;
    /* resources */
    GLuint vao;

    struct sc_Texture texture_vc; // texture for video capture
    struct sc_Font    font;

    struct sc_Shader shader_composite;
    struct sc_Shader shader_text;
    struct sc_Shader shader_flat;
};

extern struct sc_Context g_sc_context;

/**
 * Initialize C SmartCanvas api
 * returns SC_FALSE if initialization is fail
 * returns SC_TRUE if initialization if pass
 */
sc_bool sc_init(
    const struct sc_Config* p_config);

/**
 * Do current frame
 * returns SC_TRUE if quit event was detected
 */
sc_bool sc_do_frame(void);

#endif
