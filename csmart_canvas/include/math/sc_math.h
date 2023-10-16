#ifndef SC_MATH_H
#define SC_MATH_H

#include <stdint.h>

struct vec4 {
    float x,y,z,w;
};

struct mat4 {
    union {
        struct {
            struct vec4 col_0;
            struct vec4 col_1;
            struct vec4 col_2;
            struct vec4 col_3;
        };

        float       a_f[16];
        struct vec4 a_v[4];
    };
};

struct mat4 mat4_identity(void);

/* NDC [-1, 1]*/
struct mat4 mat4_ortho_lh_ndc_n11(
    float l, float r, float b, float t, float ne, float fa);

struct mat4 mat4_ortho_rh_ndc_n11(
    float l, float r, float b, float t, float ne, float fa);

#endif
