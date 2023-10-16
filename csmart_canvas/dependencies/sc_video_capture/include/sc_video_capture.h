#ifndef SC_VIDEO_CAPTURE_H
#define SC_VIDEO_CAPTURE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {

#endif

    int sc_video_capture_init(uint32_t width, uint32_t height);
    void sc_video_capture_close(void);
    void* sc_video_capture_get_frame(uint32_t* out_width,
                                      uint32_t* out_height);

    void sc_video_capture_release_frame(void);

#ifdef __cplusplus
}
#endif

#endif
