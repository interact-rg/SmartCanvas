#include <stdlib.h>
#include <string.h>

#include "renderer/sc_renderer.h"
#include "assert/sc_assert.h"
#include "logging/sc_logging.h"

/* TEXTURES */
sc_bool sc_make_texture(
    const struct sc_TextureConfig* p_in,
    struct sc_Texture*             p_out)
{
    if (NULL == p_in ||
        NULL == p_out) {
        return SC_FALSE;
    }

    sc_bool result = SC_TRUE;
    GLuint   texture_id;

    glGenTextures(1, &texture_id);

    if (p_in->depth == 1) {
        p_out->type = GL_TEXTURE_2D;
    } else {
        SC_ASSERT(0 != p_in->depth);
        p_out->type = GL_TEXTURE_2D_ARRAY;
    }

    glBindTexture(p_out->type, texture_id);
    glTexParameteri(p_out->type, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(p_out->type, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexParameteri(p_out->type, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(p_out->type, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

    p_out->handle = texture_id;
    p_out->width  = p_in->width;
    p_out->height = p_in->height;
    p_out->depth  = p_in->depth;
    p_out->format = p_in->internal_format;

    result = sc_update_texture(p_in,
                                p_out);

    glBindTexture(p_out->type, 0);

    SC_CHECK_GL_ERROR();
    return result;
}

sc_bool sc_free_texture(
    struct sc_Texture* p_in)
{
    if (NULL == p_in) {
        return SC_FALSE;
    }

    sc_bool result = SC_FALSE;

    SC_CHECK_GL_ERROR();
    return result;
}

sc_bool sc_update_texture(
    const struct sc_TextureConfig* p_in,
    struct sc_Texture* p_texture)
{
    if (p_texture->type == GL_TEXTURE_2D) {

        p_texture->width  = p_in->width;
        p_texture->height = p_in->height;

        glTexImage2D(GL_TEXTURE_2D,
                     0,
                     p_texture->format,
                     p_in->width,
                     p_in->height,
                     0,
                     p_in->data_format,
                     p_in->data_type,
                     p_in->data);

    } else {

        p_texture->width  = p_in->width;
        p_texture->height = p_in->height;
        p_texture->depth  = p_in->depth;

        glTexImage3D(GL_TEXTURE_2D_ARRAY,
                     p_in->data_idx,
                     p_texture->format,
                     p_in->width,
                     p_in->height,
                     p_in->depth,
                     0,
                     p_in->data_format,
                     p_in->data_type,
                     p_in->data);

    }

    SC_CHECK_GL_ERROR();
    return SC_TRUE;
}

void sc_set_texture(
    const struct sc_Texture* p_texture)
{
    glBindTexture(p_texture->type, p_texture->handle);
    SC_CHECK_GL_ERROR();
}

void sc_unset_texture(
    const struct sc_Texture* p_texture)
{
    glBindTexture(p_texture->type, 0);
    SC_CHECK_GL_ERROR();
}


/* SHADER */
sc_bool sc_make_shader(
    const struct sc_ShaderConfig* p_in,
    struct sc_Shader*             p_out)
{
    if (NULL == p_in ||
        NULL == p_out) {
        return SC_FALSE;
    }

    sc_bool result = SC_TRUE;

    if (NULL != p_in->vertex_src && NULL != p_in->fragment_src) {

        p_out->handle = glCreateProgram();

        if (SC_TRUE == result &&
            SC_FALSE == sc_shader_module_init(GL_VERTEX_SHADER,
                                                p_in->vertex_src,
                                                &p_out->vertex_handle)) {
            result = SC_FALSE;
        }

        if (SC_TRUE == result &&
            SC_FALSE == sc_shader_module_init(GL_FRAGMENT_SHADER,
                                                p_in->fragment_src,
                                                &p_out->fragment_handle)) {
            result = SC_FALSE;
        }
    }

    if (SC_TRUE == result) {

        /* link */
        glAttachShader(p_out->handle, p_out->vertex_handle);
        glAttachShader(p_out->handle, p_out->fragment_handle);

        glLinkProgram(p_out->handle);
        sc_set_shader(p_out);

        if (SC_FALSE == sc_check_shader_link(p_out->handle)) {
            result = SC_FALSE;
        }
    }

    SC_CHECK_GL_ERROR();
    return result;
}

sc_bool sc_free_shader(
    struct sc_Shader* p_in)
{
    if (NULL == p_in) {
        return SC_FALSE;
    }

    sc_bool result = SC_TRUE;

    if (p_in->vertex_handle) {
        glDeleteShader(p_in->vertex_handle);
    }

    if (p_in->fragment_handle) {
        glDeleteShader(p_in->fragment_handle);
    }

    if (p_in->handle) {
        glDeleteProgram(p_in->handle);
    }

    SC_CHECK_GL_ERROR();
    return result;
}

void sc_set_shader(
    const struct sc_Shader* p_shader)
{
    glUseProgram(p_shader->handle);
    SC_CHECK_GL_ERROR();
}

void sc_unset_shader(void)
{
    glUseProgram(0);
    SC_CHECK_GL_ERROR();
}

void sc_set_uniform_mat4(
    const struct sc_Shader* p_shader,
    const char* uniform_name,
    struct mat4 mat)
{
    if (NULL != p_shader) {
        GLint loc = glGetUniformLocation(
            p_shader->handle,
            uniform_name);

        if (-1 != loc) {
            glUniformMatrix4fv(loc,
                               1,
                               GL_FALSE,
                               mat.a_f);
        } else {
            SC_WARN("Invalid uniform location for '%s'", uniform_name);
        }
    } else {
        SC_WARN("p_shader is NULL");
    }

    SC_CHECK_GL_ERROR();
}

sc_bool sc_check_shader_module(
    const GLuint module,
    const char* desc)
{
    int result;
    glGetShaderiv(module, GL_COMPILE_STATUS, &result);

    if (0 == result) {
        char buffer[1024];
        glGetShaderInfoLog(module, 1024, NULL, buffer);

        SC_ERROR("error in stage: '%s'\n", desc);
        SC_ERROR("%s\n", buffer);
        SC_ERROR("\n");
    }

    return result ? SC_TRUE : SC_FALSE;
}

sc_bool sc_check_shader_link(
    const GLuint shader)
{
    int result;
    glGetProgramiv(shader, GL_LINK_STATUS, &result);

    if (0 == result) {
        char buffer[1024];
        glGetProgramInfoLog(shader, 1024, NULL, buffer);

        SC_ERROR("link failed: %s\n", buffer);
        SC_ERROR("\n");
    }

    return result ? SC_TRUE : SC_FALSE;
}

sc_bool sc_shader_module_init(
    GLenum type,
    const char* source,
    GLuint *shader_module)
{
    sc_bool result = SC_TRUE;

    if (NULL != source) {
        const GLuint module_id = glCreateShader(type);

        glShaderSource(module_id, 1, &source, NULL);
        glCompileShader(module_id);

        if (SC_FALSE == sc_check_shader_module(module_id, "")) {
            result = SC_FALSE;
        }

        if (SC_FALSE == result) {
            glDeleteShader(module_id);
        } else {
            *shader_module = module_id;
        }
    }
    return result;
}

/* BUFFER */
sc_bool sc_make_buffer_index(
    struct sc_Buffer* p_in)
{
    p_in->type  = GL_ELEMENT_ARRAY_BUFFER;
    p_in->usage = GL_STATIC_DRAW;
    p_in->size  = 0;

    glGenBuffers(1, &p_in->handle);

    SC_CHECK_GL_ERROR();
    return SC_TRUE;
}

sc_bool sc_make_buffer_vertex(
    struct sc_Buffer* p_in)
{
    p_in->type  = GL_ARRAY_BUFFER;
    p_in->usage = GL_STATIC_DRAW;
    p_in->size  = 0;

    glGenBuffers(1, &p_in->handle);

    SC_CHECK_GL_ERROR();
    return SC_TRUE;
}

sc_bool sc_make_buffer_uniform(
    struct sc_Buffer* p_in)
{
    p_in->type  = GL_UNIFORM_BUFFER;
    p_in->usage = GL_STATIC_DRAW;
    p_in->size  = 0;

    glGenBuffers(1, &p_in->handle);

    SC_CHECK_GL_ERROR();
    return SC_TRUE;
}

sc_bool sc_make_buffer_instance(
    struct sc_Buffer* p_in)
{
    p_in->type  = GL_ARRAY_BUFFER;
    p_in->usage = GL_STATIC_DRAW;
    p_in->size  = 0;

    glGenBuffers(1, &p_in->handle);

    SC_CHECK_GL_ERROR();
    return SC_TRUE;
}

sc_bool sc_make_buffer_transfer(
    struct sc_Buffer* p_in)
{
    p_in->type  = GL_COPY_READ_BUFFER;
    p_in->usage = GL_DYNAMIC_DRAW;
    p_in->size  = 0;

    glGenBuffers(1, &p_in->handle);

    SC_CHECK_GL_ERROR();
    return SC_TRUE;
}

void sc_free_buffer(
    struct sc_Buffer* p_in)
{
    if (NULL != p_in &&
        0 != p_in->handle) {
        glDeleteBuffers(1, &p_in->handle);
        SC_CHECK_GL_ERROR();
    }
}

void sc_set_buffer(const struct sc_Buffer* p_in) {
    glBindBuffer(p_in->type,
                 p_in->handle);
    SC_CHECK_GL_ERROR();
}

void sc_unset_buffer(const struct sc_Buffer* p_in) {
    glBindBuffer(p_in->type,
                 0);
    SC_CHECK_GL_ERROR();
}

void sc_set_buffer_data(
    uint32_t size,
    void* data,
    struct sc_Buffer* p_in)
{
    SC_CHECK_GL_ERROR();
    glNamedBufferData(p_in->handle,
                      size,
                      data,
                      p_in->usage);
    p_in->size = size;
    SC_CHECK_GL_ERROR();
}

/* IM */
struct sc_IM_Cmd* sc_im_begin(
    sc_VertexAttributeTypeMask vertex_attrib_mask)
{
    struct sc_IM_Cmd* p_cmd = malloc(sizeof(*p_cmd));
    memset(p_cmd, 0, sizeof(*p_cmd));

    /* vertices */
    p_cmd->vertex_attrib_mask = vertex_attrib_mask;
    const sc_VertexAttributeTypeMask mask = vertex_attrib_mask;
    if (SC_VERTEX_ATTRIBUTE_POSITION_BIT & mask) {
        p_cmd->vertex_size += sizeof(float) * 3;
    }
    if (SC_VERTEX_ATTRIBUTE_COLOR_BIT & mask) {
        p_cmd->vertex_size += sizeof(uint32_t);
    }
    if (SC_VERTEX_ATTRIBUTE_TEX_COORD_0_BIT & mask) {
        p_cmd->vertex_size += sizeof(float) * 3;
    }

    p_cmd->vertex_count_max = 256;
    p_cmd->vertex_count     = 0;
    p_cmd->p_vertices = malloc(p_cmd->vertex_count_max * p_cmd->vertex_size);


    return p_cmd;
}

void sc_im_end(
    struct sc_IM_Cmd* p_in)
{
    if (NULL != p_in)
    {
        SC_CHECK_GL_ERROR();

        const sc_VertexAttributeTypeMask mask        = p_in->vertex_attrib_mask;
        void*                             offset      = 0;
        const uint32_t                    vertex_size = p_in->vertex_size;

        struct sc_Buffer vertex_buffer;
        sc_make_buffer_vertex(&vertex_buffer);
        sc_set_buffer(&vertex_buffer);
        sc_set_buffer_data(
            vertex_size * p_in->vertex_count,
            p_in->p_vertices,
            &vertex_buffer);

        if (SC_VERTEX_ATTRIBUTE_POSITION_BIT & mask) {
            const GLuint loc =  SC_VERTEX_ATTRIBUTE_POSITION_LOC;
            glEnableVertexAttribArray(loc);
            glVertexAttribPointer(loc,
                                  3,
                                  GL_FLOAT,
                                  GL_FALSE,
                                  vertex_size,
                                  offset);

            offset += sizeof(float) * 3;
        }

        if (SC_VERTEX_ATTRIBUTE_COLOR_BIT & mask) {

            const GLuint loc = SC_VERTEX_ATTRIBUTE_COLOR_LOC;
            glEnableVertexAttribArray(loc);
            glVertexAttribPointer(loc,
                                  4,
                                  GL_UNSIGNED_BYTE,
                                  GL_TRUE,
                                  vertex_size,
                                  offset);

            offset += sizeof(uint32_t);
        }

        if (SC_VERTEX_ATTRIBUTE_TEX_COORD_0_BIT & mask) {

            const GLuint loc = SC_VERTEX_ATTRIBUTE_TEX_COORD_0_LOC;
            glEnableVertexAttribArray(loc);
            glVertexAttribPointer(loc,
                                  3,
                                  GL_FLOAT,
                                  GL_FALSE,
                                  vertex_size,
                                  offset);

            offset += sizeof(float) * 3;
        }
        SC_CHECK_GL_ERROR();

        // draw
        glDrawArrays(GL_TRIANGLES, 0, p_in->vertex_count);
        SC_CHECK_GL_ERROR();

        /* disable */
        if (SC_VERTEX_ATTRIBUTE_POSITION_BIT & mask) {
            glDisableVertexAttribArray(SC_VERTEX_ATTRIBUTE_POSITION_LOC);
        }
        if (SC_VERTEX_ATTRIBUTE_COLOR_BIT & mask) {
            glDisableVertexAttribArray(SC_VERTEX_ATTRIBUTE_COLOR_LOC);
        }
        if (SC_VERTEX_ATTRIBUTE_TEX_COORD_0_BIT & mask) {
           glDisableVertexAttribArray(SC_VERTEX_ATTRIBUTE_TEX_COORD_0_BIT);
        }

        sc_unset_buffer(&vertex_buffer);

        /* free */
        sc_free_buffer(&vertex_buffer);
        free(p_in->p_vertices);
        free(p_in);
    }
}

void sc_im_vertex(
    struct sc_IM_Cmd* p_in,
    float x, float y, float z)
{
    if (NULL != p_in) {
        p_in->current_vertex.x = x;
        p_in->current_vertex.y = y;
        p_in->current_vertex.z = z;

        if (p_in->vertex_count == p_in->vertex_count_max) {
            p_in->vertex_count_max *= 2;
            p_in->p_vertices = realloc(p_in->p_vertices, p_in->vertex_count_max * p_in->vertex_size);
        }

        const sc_VertexAttributeTypeMask mask = p_in->vertex_attrib_mask;
        uint32_t offset = 0;

        void* p_data = p_in->p_vertices + p_in->vertex_size * p_in->vertex_count;
        if (SC_VERTEX_ATTRIBUTE_POSITION_BIT & mask) {
            memcpy(p_data + offset, &p_in->current_vertex.x, sizeof(float) * 3);
            offset += sizeof(float) * 3;
        }

        if (SC_VERTEX_ATTRIBUTE_COLOR_BIT & mask) {
            memcpy(p_data + offset, &p_in->current_vertex.color, sizeof(uint32_t));
            offset += sizeof(uint32_t);
        }

        if (SC_VERTEX_ATTRIBUTE_TEX_COORD_0_BIT & mask) {
            memcpy(p_data + offset, &p_in->current_vertex.uv_0_x, sizeof(float) * 3);
            offset += sizeof(float) * 3;
        }

        p_in->vertex_count++;
    }
}

void sc_im_tc_0(
    struct sc_IM_Cmd* p_in,
    float x, float y, float z)
{
    if (NULL != p_in) {
        p_in->current_vertex.uv_0_x = x;
        p_in->current_vertex.uv_0_y = y;
        p_in->current_vertex.uv_0_z = z;
    }
}

void sc_im_color_u32(
    struct sc_IM_Cmd* p_in,
    uint32_t color)
{
    if (NULL != p_in) {
        p_in->current_vertex.color = color;
    }
}

void sc_im_quad_tc0(
    struct sc_IM_Cmd* im,
    float x0, float y0, float z0,
    float tc_x0, float tc_y0, float tc_z0,
    float x1, float y1, float z1,
    float tc_x1, float tc_y1, float tc_z1)
{
    if (NULL != im) {
        sc_im_tc_0(im, tc_x0, tc_y1, tc_z0);
        sc_im_vertex(im, x0, y0, z1);

        sc_im_tc_0(im, tc_x0, tc_y0, tc_z0);
        sc_im_vertex(im, x0, y1, z1);

        sc_im_tc_0(im, tc_x1, tc_y0, tc_z0);
        sc_im_vertex(im, x1, y1, z1);

        // 2
        sc_im_tc_0(im, tc_x0, tc_y1, tc_z0);
        sc_im_vertex(im, x0, y0, z1);

        sc_im_tc_0(im, tc_x1, tc_y0, tc_z0);
        sc_im_vertex(im, x1, y1, z1);

        sc_im_tc_0(im, tc_x1, tc_y1, tc_z0);
        sc_im_vertex(im, x1, y0, z1);
    }
}
void sc_im_text(
    struct sc_IM_Cmd* p_in,
    const char* text,
    float x, float y, float z,
    float scale,
    const struct sc_Font* font)
{
    float cursor_x = x;
    float cursor_y = y;
    float cursor_z = z;

    cursor_y -= (font->ascent - font->descent) * scale;

    if (NULL != text && NULL != p_in) {
        const char* at = text;
        while (0 != *at) {
            if ('\n' == *at) {
                cursor_y -= (font->ascent - font->descent + font->line_gap) * scale;
                cursor_x = x;
            } else {

                if (*at >= 32) {
                    struct sc_Glyph glyph = font->glyphs[*at - 32];

                    const float x0 = cursor_x + (glyph.x_offset) * scale;
                    const float y0 = cursor_y - glyph.y_offset * scale;

                    sc_im_quad_tc0(
                        p_in,
                        x0,
                        y0,
                        cursor_z,
                        0,
                        0,
                        *at - 32,
                        x0 + font->texture.width * scale,
                        y0 + font->texture.height * scale,
                        cursor_z,
                        1, 1,
                        *at - 32);

                    cursor_x = (glyph.advance_x + x0) * scale;
                }
            }
            at++;
        }
    }
}
