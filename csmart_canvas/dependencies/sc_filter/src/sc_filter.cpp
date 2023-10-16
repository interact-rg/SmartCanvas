#include <opencv2/opencv.hpp>
#include <opencv2/xphoto.hpp>

#include <stdint.h>

/* Declarations */
void sc2_filter_remove_background(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height);

void sc2_filter_canvas(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height);

void sc2_filter_oil_painting(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height);

void sc2_filter_sketch(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height);

void sc2_filter_watercolor(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height);

void sc2_filter_mosaic(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height);

/* Definitions */

void sc2_filter_remove_background(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height)
{

}

void sc2_filter_canvas(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height)
{
    cv::Mat tile = cv::imread(
        "data/filters/canvas/struc.pgm");

    const int x_count = (width / tile.cols) + 1;
    const int y_count = (height / tile.rows) + 1;

    /* Create image */
    cv::Mat image = cv::Mat(height, width, CV_8UC3, p_image);

    /* Create a tiled image */
    cv::Mat tiled;
    cv::repeat(tile, y_count, x_count, tiled);

    // Crop the tiled image to match the size of the frame
    cv::Rect roi(0, 0, width, height);
    cv::Mat canvas_bg = tiled(roi);

    /* Define the kernel */
    cv::Mat kernel = (cv::Mat_<float>(2, 2) << 0.5, 0, 0, 0.5);

    cv::filter2D(canvas_bg, canvas_bg, -1, kernel);

    // Blend the frame and the filtered background
    double alpha = 0.85;
    cv::addWeighted(image,
                    alpha,
                    canvas_bg,
                    1.0 - alpha,
                    0,
                    image);
}

void sc2_filter_oil_painting(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height)
{
    cv::Mat image = cv::Mat(height, width, CV_8UC3, p_image);

    void*   p_temp = malloc(width * height * 3);
    cv::Mat temp   = cv::Mat(height, width, CV_8UC3, p_temp);

    cv::xphoto::oilPainting(image, temp, 7, 1, 2);

    memcpy(p_image, p_temp, width * height * 3);
    free(p_temp);
}

void sc2_filter_sketch(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height)
{
    cv::Mat image = cv::Mat(height, width, CV_8UC3, p_image);

    void*   p_temp_0 = malloc(width * height * 3);
    cv::Mat temp_0   = cv::Mat(height, width, CV_8UC3, p_temp_0);

    void*   p_temp_1 = malloc(width * height * 3);
    cv::Mat temp_1   = cv::Mat(height, width, CV_8UC3, p_temp_1);

#if 0
    const float sigma_s = 10.0f;
    const float sigma_r = 0.01f;
    const float shade_factor = 0.03f;
#endif

    cv::pencilSketch(image, temp_0, temp_1);//, sigma_s, sigma_r, shade_factor);
    memcpy(p_image, p_temp_1, width * height * 3);

    free(p_temp_0);
    free(p_temp_1);
}

void sc2_filter_watercolor(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height)
{
    cv::Mat image = cv::Mat(height, width, CV_8UC3, p_image);

    void*   p_temp = malloc(width * height * 3);
    cv::Mat temp   = cv::Mat(height, width, CV_8UC3, p_temp);

    const float sigma_s = 60.0f;
    const float sigma_r = 0.4f;
    cv::stylization(image, temp, sigma_s, sigma_r);

    memcpy(p_image, p_temp, width * height * 3);
    free(p_temp);
}
void sc2_filter_mosaic(
    uint8_t* p_image,
    uint32_t width,
    uint32_t height)
{
    const uint32_t randomness = 500;

    cv::Mat image = cv::Mat(height, width, CV_8UC3, p_image);

    cv::Rect rect(0, 0, width, height);
    cv::Subdiv2D subdiv(rect);


    for (uint32_t n = 0; n < randomness; ++n) {
        int x = rand() % (width - 1);
        int y = rand() % (height - 1);
        subdiv.insert(cv::Point2f(static_cast<float>(x), static_cast<float>(y)));
    }

    std::vector<std::vector<cv::Point2f>> facets;
    std::vector<cv::Point2f> centers;
    subdiv.getVoronoiFacetList(std::vector<int>(), facets, centers);

    for (size_t i = 0; i < facets.size(); ++i) {
        std::vector<cv::Point> ifacet_arr;
        for (size_t j = 0; j < facets[i].size(); ++j) {
            ifacet_arr.push_back(facets[i][j]);
        }
        std::vector<cv::Point> ifacet = ifacet_arr;

        cv::Mat mask = cv::Mat::zeros(height, width, CV_8U);
        std::vector<std::vector<cv::Point>> ifacets(1, ifacet);
        cv::fillPoly(mask, ifacets, cv::Scalar(255, 255, 255));

        cv::Mat res = cv::Mat::zeros(image.size(), image.type());
        image.copyTo(res, mask);
        cv::Scalar col_mean = cv::mean(res, mask);

        cv::fillPoly(image, ifacets, col_mean);
    }

}
/* C API */
extern "C" {
    void sc_filter_set_worker_count(int count) {
        cv::setNumThreads(count); // Adjust the number of threads as needed
    }

    void sc_filter_remove_background(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height) {
        sc2_filter_remove_background(p_image, width, height);
    }

    void sc_filter_canvas(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height)
    {
        sc2_filter_canvas(p_image, width, height);
    }

    void sc_filter_oil_painting(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height)
    {
        sc2_filter_oil_painting(p_image, width, height);
    }

    void sc_filter_sketch(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height)
    {
        sc2_filter_sketch(p_image, width, height);
    }

    void sc_filter_watercolor(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height)
    {
        sc2_filter_watercolor(p_image, width, height);
    }

    void sc_filter_mosaic(
        uint8_t* p_image,
        uint32_t width,
        uint32_t height)
    {
        sc2_filter_mosaic(p_image, width, height);
    }
}

int main() {
    return 1;
}
