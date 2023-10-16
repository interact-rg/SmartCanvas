#include <opencv2/opencv.hpp>
#include <thread>
#include <deque>
#include <mutex>
#include <condition_variable>

struct sc2_video_capture_context {
    bool                         is_quit;
    int32_t                      width;
    int32_t                      height;
    cv::VideoCapture             cap;
    std::thread                  thread;
    std::deque<cv::Mat>          buffer;
    std::mutex                   buffer_mutex;
    std::condition_variable      buffer_not_empty;
} g_sc2_vc_context;

void sc2_thread_proc(void* p_data)
{
    cv::VideoCapture cap = g_sc2_vc_context.cap;

    while (g_sc2_vc_context.is_quit == false) {
        cv::Mat frame;
        cap >> frame;

        if (frame.empty()) {
            std::cerr << "Error: Empty frame." << std::endl;
            break;
        }

        // Lock the mutex before accessing the circular buffer
        g_sc2_vc_context.buffer_mutex.lock();
        g_sc2_vc_context.buffer.push_back(frame);

        const int max_buffer_size = 1;

        while (g_sc2_vc_context.buffer.size() > max_buffer_size) {
            g_sc2_vc_context.buffer.pop_front();
        }

        // Notify that the buffer is not empty
        g_sc2_vc_context.buffer_not_empty.notify_all();

        // Unlock the mutex
        g_sc2_vc_context.buffer_mutex.unlock();

    }

    cap.release();
}

int sc2_video_capture_init(uint32_t width, uint32_t height) {

    g_sc2_vc_context.cap = cv::VideoCapture(0);
    g_sc2_vc_context.cap.set(cv::CAP_PROP_BUFFERSIZE, 2);
    g_sc2_vc_context.cap.set(cv::CAP_PROP_FPS, 60);
    g_sc2_vc_context.cap.set(cv::CAP_PROP_FOURCC, cv::VideoWriter::fourcc('M', 'J', 'P', 'G'));


    bool result = true;
    if (g_sc2_vc_context.cap.isOpened() == 0) {
        std::cerr << "Error: Could not open camera." << std::endl;
        result = false;
    } else {
        // Try to set the desired capture resolution
        g_sc2_vc_context.cap.set(cv::CAP_PROP_FRAME_WIDTH, width);
        g_sc2_vc_context.cap.set(cv::CAP_PROP_FRAME_HEIGHT, height);

        g_sc2_vc_context.width  = g_sc2_vc_context.cap.get(cv::CAP_PROP_FRAME_WIDTH);
        g_sc2_vc_context.height = g_sc2_vc_context.cap.get(cv::CAP_PROP_FRAME_HEIGHT);
    }

    if (true == result) {
        g_sc2_vc_context.thread = std::thread(sc2_thread_proc, nullptr);
    }

    return result == true;
}

void sc2_video_capture_close(void) {
    g_sc2_vc_context.is_quit = true;
    g_sc2_vc_context.thread.join();
}

void* sc2_video_capture_get_frame(void)
{
    while(g_sc2_vc_context.buffer.empty())
    {
    }

    g_sc2_vc_context.buffer_mutex.lock();
    return g_sc2_vc_context.buffer.front().data;
}

void sc2_video_capture_release_frame(void)
{
    g_sc2_vc_context.buffer_mutex.unlock();
}

int main(void)
{
    return 1;
}

extern "C" {
    int sc_video_capture_init(uint32_t width, uint32_t height) {
        return sc2_video_capture_init(width, height) == true;
    }

    void sc_video_capture_close(void) {
        sc2_video_capture_close();
    }

    void* sc_video_capture_get_frame(uint32_t* out_width,
                                      uint32_t* out_height)
    {
        *out_width  = g_sc2_vc_context.width;
        *out_height = g_sc2_vc_context.height;

        return sc2_video_capture_get_frame();
    }

    void sc_video_capture_release_frame(void)
    {
        sc2_video_capture_release_frame();
    }

}
