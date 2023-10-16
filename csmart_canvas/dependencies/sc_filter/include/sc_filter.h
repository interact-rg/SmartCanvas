#ifndef SC_FILTER_H
#define SC_FILTER_H

#ifdef __cplusplus
extern "C" {
#endif
    void sc_filter_set_worker_count(
        int count);

    void sc_filter_remove_background(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height);

    void sc_filter_canvas(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height);

    void sc_filter_oil_painting(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height);

    void sc_filter_sketch(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height);

    void sc_filter_watercolor(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height);

    void sc_filter_mosaic(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height);
#ifdef __cplusplus
}
#endif

#endif
