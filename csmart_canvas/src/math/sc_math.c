#include "math/sc_math.h"

struct mat4 mat4_identity(void) {
    struct mat4 m = {
        .a_f = {
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
        }
    };

    return m;
}

/* NDC [-1, 1] */
struct mat4 mat4_ortho_lh_ndc_n11(float left, float right, float bottom, float top, float ne, float fa) {
    struct mat4 m = {
        .a_f = {
            2.0f / (right - left), 0.0f, 0.0f, 0.0f,
            0.0f, 2.0f / (top - bottom), 0.0f, 0.0f,
            0.0f, 0.0f, 2.0f / (fa - ne), 0.0f,
            (-(right + left) / (right - left)), (-(top + bottom) / (top - bottom)), (-(fa + ne) / (fa - ne)), 1
        }
    };

    return m;
}

/* NDC [-1, 1] */
struct mat4 mat4_ortho_rh_ndc_n11(float left, float right, float bottom, float top, float ne, float fa) {
    struct mat4 m = {
        .a_f = {
            2.0f / (right - left), 0.0f, 0.0f, 0.0f,
            0.0f, 2.0f / (top - bottom), 0.0f, 0.0f,
            0.0f, 0.0f, -2.0f / (fa - ne), 0.0f,
            (-(right + left) / (right - left)), (-(top + bottom) / (top - bottom)), (-(fa + ne) / (fa - ne)), 1
        }
    };

    return m;
}
