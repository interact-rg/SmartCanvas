#include "sc_typedef.h"
#include "core/sc_core.h"

#include "sc_video_capture.h"
#include "sc_filter.h"

#include "logging/sc_logging.h"
#include "renderer/sc_builtin_shaders.h"
#include "renderer/sc_font.h"

struct sc_Context g_sc_context;


#include <time.h>
#include <sys/times.h>

uint64_t sc_util_get_time_ms(void){
    struct timespec time;
    clock_gettime(CLOCK_REALTIME, &time);
    uint64_t result = (uint64_t)(time.tv_sec * 1000) + (uint64_t)(time.tv_nsec / 1000000);
    return result;
}

SC_LOCAL void sc_apply_filter(
    void* p_data,
    uint32_t width,
    uint32_t height);

sc_bool sc_init(
    const struct sc_Config* p_config)
{

    sc_sm_state_enter(SC_STATE_MACHINE_STATE_SETUP);
    return SC_TRUE;
}

void* old_frame_data;

SC_LOCAL const char* sc_get_current_filter_name(void)
{
    enum SC_FILTER_TYPE filter = g_sc_context.current_filter;

    switch (filter) {
    case SC_FILTER_TYPE_NONE:         return "None";
    case SC_FILTER_TYPE_OIL_PAINTING: return "Oil painting";
    case SC_FILTER_TYPE_CANVAS:       return "Canvas";
    case SC_FILTER_TYPE_SKETCH:       return "Sketch";
    case SC_FILTER_TYPE_WATER_COLOR:  return "Water color";
    case SC_FILTER_TYPE_MOSAIC:       return "Mosaic";
    default:                          return "None";
    }
}

SC_LOCAL void sc_apply_filter(
    void* p_data,
    uint32_t width,
    uint32_t height)
{

    uint64_t start_ms = sc_util_get_time_ms();

    enum SC_FILTER_TYPE filter = g_sc_context.current_filter;

    sc_filter_remove_background(p_data, width, height);

    switch (filter) {
    case SC_FILTER_TYPE_NONE:
        break;
    case SC_FILTER_TYPE_OIL_PAINTING:
        sc_filter_oil_painting(p_data, width, height);
        break;
    case SC_FILTER_TYPE_CANVAS:
        sc_filter_canvas(p_data, width, height);
        break;
    case SC_FILTER_TYPE_SKETCH:
        sc_filter_sketch(p_data, width, height);
        break;
    case SC_FILTER_TYPE_WATER_COLOR:
        sc_filter_watercolor(p_data, width, height);
        break;
    case SC_FILTER_TYPE_MOSAIC:
        sc_filter_mosaic(p_data, width, height);
        break;
    default:
        g_sc_context.current_filter = SC_FILTER_TYPE_NONE;
        break;
    }

    g_sc_context.timing.filter = sc_util_get_time_ms() - start_ms;
}

sc_bool sc_do_frame(
    void)
{
    // Main loop
    sc_bool  quit = SC_FALSE;
    SDL_Event event;

    g_sc_context.frame_count++;

    while (SDL_PollEvent(&event)) {
        switch (event.type)
        {
        case SDL_QUIT:
        {
            quit = SC_TRUE;
            SC_TRC("Should quit!");
            break;
        }
        case SDL_WINDOWEVENT:
        {
            switch (event.window.event) {
            case SDL_WINDOWEVENT_SIZE_CHANGED:
            {
                g_sc_context.window_width = event.window.data1;
                g_sc_context.window_height = event.window.data2;
                SC_TRC("Window Resize: w:%u h:%u", event.window.data1, event.window.data2);
                break;
            }
            }
            break;
        }
        case SDL_KEYDOWN:
        {
            // A key has been pressed
            // You can check the event.key.keysym.sym to identify which key
            if (event.key.keysym.sym == SDLK_a) {
                g_sc_context.current_filter = (g_sc_context.current_filter + (SC_FILTER_TYPE_COUNT - 1)) % SC_FILTER_TYPE_COUNT;
            }

            if (event.key.keysym.sym == SDLK_d) {
                g_sc_context.current_filter = (g_sc_context.current_filter + 1) % SC_FILTER_TYPE_COUNT;
            }

            break;
        }
        }
    }

    sc_sm_update();

    if (quit == SC_FALSE) {
        glViewport(0, 0, g_sc_context.window_width, g_sc_context.window_height);
        glClearColor(g_sc_context.frame_count % 255 / 255.0f, 0, 0, 0);
        glClear(GL_COLOR_BUFFER_BIT);

        /* get camera frame */
        uint32_t frame_width = 0;
        uint32_t frame_height = 0;

        void* frame_data =
            sc_video_capture_get_frame(&frame_width, &frame_height);

        sc_set_texture(&g_sc_context.texture_vc);
        if (old_frame_data != frame_data) {
            old_frame_data = frame_data;

            void* data = malloc(frame_width * frame_height * 3);
            memcpy(data, frame_data, frame_width * frame_height * 3);

            sc_apply_filter(data, frame_width, frame_height);

            struct sc_TextureConfig config =
                {
                    .width       = frame_width,
                    .height      = frame_height,
                    .depth       = 1,
                    .data_format = GL_BGR,
                    .data_type   = GL_UNSIGNED_BYTE,
                    .data        = data,
                };

            sc_update_texture(&config,
                               &g_sc_context.texture_vc);
            free(data);
        } else {

        }

        sc_video_capture_release_frame();

        sc_set_shader(&g_sc_context.shader_flat);
        sc_set_uniform_mat4(&g_sc_context.shader_flat,
                             "projection",
                             mat4_identity());

        {
            struct sc_IM_Cmd* im =
                sc_im_begin(SC_VERTEX_ATTRIBUTE_POSITION_BIT | SC_VERTEX_ATTRIBUTE_COLOR_BIT | SC_VERTEX_ATTRIBUTE_TEX_COORD_0_BIT);

            sc_im_color_u32(im, 0xffffffff);

            // 1 bl, tl, tr
            sc_im_tc_0(im, 0, 1, 0);
            sc_im_vertex(im, -1, -1, 1);

            sc_im_tc_0(im, 0, 0, 0);
            sc_im_vertex(im, -1, 1, 1);

            sc_im_tc_0(im, 1, 0, 0);
            sc_im_vertex(im, 1, 1, 1);

            // 2
            sc_im_tc_0(im, 0, 1, 0);
            sc_im_vertex(im, -1, -1, 1);

            sc_im_tc_0(im, 1, 0, 0);
            sc_im_vertex(im, 1, 1, 1);

            sc_im_tc_0(im, 1, 1, 0);
            sc_im_vertex(im, 1, -1, 1);

            sc_im_end(im);
        }
        sc_unset_texture(&g_sc_context.font.texture);
        sc_unset_shader();

        sc_set_texture(&g_sc_context.font.texture);
        sc_set_shader(&g_sc_context.shader_text);

        {
            struct sc_IM_Cmd* im =
                sc_im_begin(SC_VERTEX_ATTRIBUTE_POSITION_BIT | SC_VERTEX_ATTRIBUTE_COLOR_BIT | SC_VERTEX_ATTRIBUTE_TEX_COORD_0_BIT);

            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
            glBlendEquation(GL_FUNC_ADD);

            sc_im_color_u32(im, 0xffffffff);
            sc_set_uniform_mat4(&g_sc_context.shader_flat,
                                "projection",
                                mat4_ortho_lh_ndc_n11(
                                    0, (float)g_sc_context.window_width,
                                    0, (float)g_sc_context.window_height,
                                    0.00001f, 10000.0f));

            const float pad = 20;
            sc_im_text(im,
                       sc_get_current_filter_name(),
                       pad, pad, 1,
                       1,
                       &g_sc_context.font);


            char buffer[1024];
            sprintf(buffer, "filter: %zu ms", g_sc_context.timing.filter);

            sc_im_text(im,
                       buffer,
                       pad,
                       g_sc_context.window_height - 100,
                       1,
                       1,
                       &g_sc_context.font);

            sc_im_end(im);
            glDisable(GL_BLEND);
        }

        sc_unset_texture(&g_sc_context.font.texture);
        sc_unset_shader();


        SDL_GL_SwapWindow(g_sc_context.window);

    } else {
        // Clean up and exit
        SC_TRC("Close video capture");
        sc_video_capture_close();

        SC_TRC("Close window");
        SDL_GL_DeleteContext(g_sc_context.sdl_context);
        SDL_DestroyWindow(g_sc_context.window);
        SDL_Quit();
    }

    return quit;
}
