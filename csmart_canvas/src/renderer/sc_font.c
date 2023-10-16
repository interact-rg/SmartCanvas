#include <stdio.h>
#include <stdlib.h>

#include "renderer/sc_font.h"
#include "logging/sc_logging.h"

#define STB_TRUETYPE_IMPLEMENTATION
#include "stb/stb_truetype.h"

sc_bool sc_make_font(
    const char*      p_ttf_path,
    uint32_t         font_size,
    struct sc_Font* p_font)
{
    sc_bool result = SC_TRUE;

    FILE* font_file =
        fopen(p_ttf_path, "rb");

    if (font_file != NULL) {

        // Determine the file size
        fseek(font_file, 0, SEEK_END);
        size_t file_size = ftell(font_file);
        fseek(font_file, 0, SEEK_SET);

        void* ttf_buffer = malloc(file_size);

        // Read the font data into ttf_buffer
        if (fread(ttf_buffer, 1, file_size, font_file) != file_size) {
            // Handle error: Unable to read the font data
            SC_FATAL("Failed to read font file");
            result = SC_FALSE;
        }

        fclose(font_file);

        if (SC_TRUE == result) {
            stbtt_fontinfo fontinfo;

            if(0 == stbtt_InitFont(&fontinfo,
                                   ttf_buffer,
                                   stbtt_GetFontOffsetForIndex(ttf_buffer, 0))) {
                SC_ERROR("stbttt_initFont failed");
                result = SC_FALSE;

            } else {
                const float scale = stbtt_ScaleForPixelHeight(&fontinfo, font_size);
                p_font->scale = scale;

                stbtt_GetFontVMetrics(&fontinfo,
                                      &p_font->ascent,
                                      &p_font->descent,
                                      &p_font->line_gap);

                p_font->ascent   *= scale;
                p_font->descent  *= scale;
                p_font->line_gap *= scale;

                /* extact glyphs */
                struct sc_TextureConfig config = {
                    .width                      = 0,
                    .height                     = 0,
                    .depth                      = 128,
                    .internal_format            = GL_R8,
                    .data_format                = GL_RED,
                    .data_type                  = GL_UNSIGNED_BYTE,
                    .data                       = NULL,
                };

                for (int codepoint = 32; codepoint < 160; ++codepoint) {
                    int width, height, x_off, y_off;
                    unsigned char* bitmap = stbtt_GetCodepointBitmap(&fontinfo,
                                                                     0,
                                                                     stbtt_ScaleForPixelHeight(&fontinfo,
                                                                                               font_size),
                                                                     codepoint,
                                                                     &width,
                                                                     &height,
                                                                     &x_off,
                                                                     &y_off);

                    if (width > (int)config.width) {
                        config.width = width;
                    }

                    if (height > (int)config.height) {
                        config.height = height;
                    }

                    // Free the bitmap memory
                    stbtt_FreeBitmap(bitmap, NULL);
                }

                /* texture sizes should be 2^n */
                uint32_t nextp2 = 2;
                while(1){
                    if (nextp2 >= config.width) {
                        config.width = nextp2;
                        break;
                    }
                    nextp2 *= 2;
                }

                nextp2 = 2;
                while(1){
                    if (nextp2 >= config.height) {
                        config.height = nextp2;
                        break;
                    }
                    nextp2 *= 2;
                }

                struct sc_Texture font_texture;

                sc_make_texture(&config,
                                 &font_texture);

                SC_TRC("Texture size: %u, %u, %u", config.width, config.height, config.depth);
                sc_set_texture(&font_texture);

                glTexParameteri(font_texture.type, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
                glTexParameteri(font_texture.type, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

                glTexParameteri(font_texture.type, GL_TEXTURE_SWIZZLE_A, GL_RED);
                glTexParameteri(font_texture.type, GL_TEXTURE_SWIZZLE_R, GL_ONE);
                glTexParameteri(font_texture.type, GL_TEXTURE_SWIZZLE_G, GL_ONE);
                glTexParameteri(font_texture.type, GL_TEXTURE_SWIZZLE_B, GL_ONE);

                unsigned char* temp_bitmap = malloc(config.width * config.height);

                for (int i = 32; i < 160; ++i) { // Load ASCII range
                    int glyph_index = stbtt_FindGlyphIndex(&fontinfo, i);

                    if (glyph_index == 0) {
                        continue;
                    }

                    unsigned char* bitmap =
                        stbtt_GetGlyphBitmap(&fontinfo,
                                             scale,
                                             scale,
                                             glyph_index,
                                             &p_font->glyphs[i - 32].width,
                                             &p_font->glyphs[i - 32].height,
                                             &p_font->glyphs[i - 32].x_offset,
                                             &p_font->glyphs[i - 32].y_offset);

                    memset(temp_bitmap, 0, config.width * config.height);
                    for (int y = 0; y < p_font->glyphs[i - 32].height; y++) {
                        for (int x = 0; x < p_font->glyphs[i - 32].width; x++) {
                            temp_bitmap[x + y * config.width] = bitmap[x + y * p_font->glyphs[i - 32].width];
                        }
                    }
                    glTexSubImage3D(GL_TEXTURE_2D_ARRAY,
                                    0,
                                    0,
                                    0,
                                    i - 32,
                                    config.width,
                                    config.height,
                                    1,
                                    GL_RED,
                                    GL_UNSIGNED_BYTE,
                                    temp_bitmap);

                    SC_CHECK_GL_ERROR();

                    stbtt_FreeBitmap(bitmap, NULL);

                    stbtt_GetGlyphHMetrics(&fontinfo,
                                           glyph_index,
                                           &p_font->glyphs[i - 32].advance_x,
                                           NULL);

                    p_font->glyphs[i - 32].advance_x *= scale;

                    stbtt_GetGlyphBitmapBox(&fontinfo,
                                            glyph_index,
                                            scale,
                                            scale,
                                            &p_font->glyphs[i - 32].width,
                                            &p_font->glyphs[i - 32].height,
                                            NULL,
                                            NULL);

                    p_font->glyphs[i - 32].left_side_bearing =
                        stbtt_GetGlyphKernAdvance(&fontinfo, glyph_index, 0); // Store kerning info

                    p_font->glyphs[i - 32].top_side_bearing =
                        stbtt_GetGlyphKernAdvance(&fontinfo, 0, glyph_index); // Store kerning info
                }

                sc_unset_texture(&font_texture);
                free(temp_bitmap);
                p_font->texture = font_texture;
            }
        }

    } else {
        SC_ERROR("Failed to open font file\n");
        result = SC_FALSE;
    }
    return result;
}
