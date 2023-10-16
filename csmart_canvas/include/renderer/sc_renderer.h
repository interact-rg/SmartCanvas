#ifndef SC_OPENGL_H
#define SC_OPENGL_H

#include <stdint.h>
#include <GL/glew.h>

#include "sc_typedef.h"
#include "math/sc_math.h"

#include "stb/stb_truetype.h"

#define SC_CHECK_GL_ERROR() do {                                       \
        GLenum error;                                                   \
        while ((error = glGetError()) != GL_NO_ERROR) {                 \
            switch (error) {                                            \
            case GL_INVALID_ENUM:                                       \
                SC_ERROR("OpenGL Error: Invalid enum");                \
                break;                                                  \
            case GL_INVALID_VALUE:                                      \
                SC_ERROR("OpenGL Error: Invalid value");               \
                break;                                                  \
            case GL_INVALID_OPERATION:                                  \
                SC_ERROR("OpenGL Error: Invalid operation, %s %u", __func__, __LINE__); \
                break;                                                  \
            case GL_STACK_OVERFLOW:                                     \
                SC_ERROR("OpenGL Error: Stack overflow");              \
                break;                                                  \
            case GL_STACK_UNDERFLOW:                                    \
                SC_ERROR("OpenGL Error: Stack underflow");             \
                break;                                                  \
            case GL_OUT_OF_MEMORY:                                      \
                SC_ERROR("OpenGL Error: Out of memory");               \
                break;                                                  \
            case GL_INVALID_FRAMEBUFFER_OPERATION:                      \
                SC_ERROR("OpenGL Error: Invalid framebuffer operation"); \
                break;                                                  \
            default:                                                    \
                SC_ERROR("OpenGL Error: Unknown error");               \
                break;                                                  \
            }                                                           \
        }                                                               \
    } while(0)

/**
********************
* types
********************
*/

enum sc_VertexAttributeTypeFlags {
    SC_VERTEX_ATTRIBUTE_POSITION_BIT     = 0x1,
    SC_VERTEX_ATTRIBUTE_COLOR_BIT        = 0x2,
    SC_VERTEX_ATTRIBUTE_TEX_COORD_0_BIT  = 0x4,
};

enum sc_VertexAttributeTypeLocation {
    SC_VERTEX_ATTRIBUTE_POSITION_LOC     = 0,
    SC_VERTEX_ATTRIBUTE_COLOR_LOC        = 1,
    SC_VERTEX_ATTRIBUTE_TEX_COORD_0_LOC  = 2,
};

typedef uint32_t sc_VertexAttributeTypeMask;

/* TEXTURE */
struct sc_TextureConfig {
    uint32_t width;
    uint32_t height;
    uint32_t depth;
    GLenum   internal_format;
    GLenum   data_format;
    GLenum   data_type;
    void*    data;
    uint32_t data_idx; // if depths is not 1
};

struct sc_Texture {
    GLuint   handle;
    GLenum   type;
    GLenum   format;
    uint32_t width;
    uint32_t height;
    uint32_t depth;
};

/* SHADER */
struct sc_ShaderConfig {
    const char* vertex_src;
    const char* fragment_src;
};

struct sc_Shader {
    GLuint handle;
    GLuint fragment_handle;
    GLuint vertex_handle;
};

/* BUFFER */
struct sc_Buffer {
    GLuint   handle;
    GLenum   type;
    uint32_t size;
    GLenum   usage;
};

/* IMMEDIATE MODE */
struct sc_IM_Vertex {
    float    x, y, z;
    uint32_t color;
    float    uv_0_x, uv_0_y, uv_0_z;
};

struct sc_IM_Cmd {
    sc_VertexAttributeTypeMask vertex_attrib_mask;

    uint32_t vertex_size;
    uint32_t vertex_count;
    uint32_t vertex_count_max;
    void*    p_vertices;

    struct sc_IM_Vertex current_vertex;
};

struct sc_Glyph{
    float   x0, y0, x1, y1;     // Glyph coordinates in the atlas
    int32_t advance_x;          // Horizontal advance
    int32_t width, height;      // Glyph dimensions
    int32_t left_side_bearing;
    int32_t top_side_bearing;
    int32_t x_offset;
    int32_t y_offset;
};

struct sc_Font{
    float              scale;
    int32_t            ascent;
    int32_t            descent;
    int32_t            line_gap;
    struct sc_Texture texture;
    struct sc_Glyph   glyphs[128];
};

sc_bool sc_make_font(
    const char* p_ttf_path,
    uint32_t  font_size,
    struct sc_Font* p_font);

/**
********************
* function prototypes
********************
*/

/* TEXTURE */
sc_bool sc_make_texture(
    const struct sc_TextureConfig* p_in,
    struct sc_Texture*             p_out);

sc_bool sc_free_texture(
    struct sc_Texture* p_in);

sc_bool sc_update_texture(
    const struct sc_TextureConfig* p_in,
    struct sc_Texture*             p_texture);

void sc_set_texture(
    const struct sc_Texture* p_texture);

void sc_unset_texture(
    const struct sc_Texture* p_texture);

/* SHADER */
sc_bool sc_make_shader(
    const struct sc_ShaderConfig* p_in,
    struct sc_Shader*             p_out);

sc_bool sc_free_shader(
    struct sc_Shader* p_in);

void sc_set_shader(
    const struct sc_Shader* p_shader);

void sc_unset_shader(void);

void sc_set_uniform_mat4(
    const struct sc_Shader* p_shader,
    const char* uniform_name,
    struct mat4 mat);

sc_bool sc_shader_module_init(
    GLenum type,
    const char* source,
    GLuint *shader_module);

sc_bool sc_check_shader_link(
    const GLuint shader);

/* BUFFER */
sc_bool sc_make_buffer_index(
    struct sc_Buffer* p_in);

sc_bool sc_make_buffer_vertex(
    struct sc_Buffer* p_in);

sc_bool sc_make_buffer_uniform(
    struct sc_Buffer* p_in);

sc_bool sc_make_buffer_instance(
    struct sc_Buffer* p_in);

sc_bool sc_make_buffer_transfer(
    struct sc_Buffer* p_in);

void sc_free_buffer(
    struct sc_Buffer* p_in);


void sc_set_buffer(const struct sc_Buffer* p_in);
void sc_unset_buffer(const struct sc_Buffer* p_in);
void sc_set_buffer_data(
    uint32_t           size,
    void*              data,
    struct sc_Buffer* p_in);

/* IM */
struct sc_IM_Cmd* sc_im_begin(
    sc_VertexAttributeTypeMask vertex_attrib_mask);

void sc_im_end(
    struct sc_IM_Cmd* p_in);

void sc_im_vertex(
    struct sc_IM_Cmd* p_in,
    float x, float y, float z);

void sc_im_tc_0(
    struct sc_IM_Cmd* p_in,
    float x, float y, float z);

void sc_im_color_u32(
    struct sc_IM_Cmd* p_in,
    uint32_t color);

void sc_im_quad_tc0(
    struct sc_IM_Cmd* p_in,
    float x0, float y0, float z0,
    float tc_x0, float tc_y0, float tc_z0,
    float x1, float y1, float z1,
    float tc_x1, float tc_y1, float tc_z1);

void sc_im_text(
    struct sc_IM_Cmd* p_in,
    const char* text,
    float x0, float y, float z,
    float scale,
    const struct sc_Font* font);

#endif
