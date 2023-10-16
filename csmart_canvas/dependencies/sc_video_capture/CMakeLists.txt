cmake_minimum_required(VERSION 3.24.3)

set(CMAKE_C_COMPILER clang++)

project(sc_video_capture LANGUAGES CXX)

find_package(OpenCV REQUIRED)

set(SRC
  src/sc_video_capture.cpp
)

set(INCLUDE_DIRS
  PRIVATE "include/"
)

set(LIBS
  ${OpenCV_LIBS}
)

set(DEBUG_COMPILE_OPTIONS
  -g -O0
)

set(RELEASE_COMPILE_OPTIONS
  -O2
)

set(WARNINGS
  -Wformat=2
  -Wall
  -Wextra
  -Wmain
  -Wparentheses
  -Wuninitialized
  -Wsign-compare
  -Werror
  -Wreturn-type
  -Wshadow
  -Wundef
  -Wformat-security
  -Wno-unused-parameter
  -Wno-unused-function
  -Wno-unused-command-line-argument
  -Wno-format-nonliteral
  -Wno-array-bounds
)

file(MAKE_DIRECTORY "lib")

# ========================================
# debug build
# ========================================
add_library(sc_video_capture_debug SHARED ${SRC})
target_compile_options(sc_video_capture_debug PRIVATE ${WARNINGS})
target_compile_options(sc_video_capture_debug PRIVATE ${DEBUG_COMPILE_OPTIONS})
target_compile_definitions(sc_video_capture_debug PRIVATE _DEBUG)
target_include_directories(sc_video_capture_debug PRIVATE ${INCLUDE_DIRS})
set_target_properties(sc_video_capture_debug PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib/
)
set_target_properties(sc_video_capture_debug PROPERTIES OUTPUT_NAME "sc_video_capture_debug")
target_link_libraries(sc_video_capture_debug PRIVATE ${LIBS})

# ========================================
# release build
# ========================================
add_library(sc_video_capture_release SHARED ${SRC})
target_compile_options(sc_video_capture_release PRIVATE ${WARNINGS})
target_compile_options(sc_video_capture_release PRIVATE ${RELEASE_COMPILE_OPTIONS})
target_compile_definitions(sc_video_capture_release PRIVATE _RELEASE)
target_include_directories(sc_video_capture_release PRIVATE ${INCLUDE_DIRS})
set_target_properties(sc_video_capture_release PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib/
)
target_link_options(sc_video_capture_release PRIVATE "-s")
set_target_properties(sc_video_capture_release PROPERTIES OUTPUT_NAME "sc_video_capture")
target_link_libraries(sc_video_capture_release PRIVATE ${LIBS})

add_executable(sc_video_capture_exe ${SRC})
target_compile_options(sc_video_capture_exe PRIVATE ${WARNINGS})
target_compile_options(sc_video_capture_exe PRIVATE ${RELEASE_COMPILE_OPTIONS})
target_compile_definitions(sc_video_capture_exe PRIVATE _EXE)
target_include_directories(sc_video_capture_exe PRIVATE ${INCLUDE_DIRS})
set_target_properties(sc_video_capture_exe PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib/
)
target_link_options(sc_video_capture_exe PRIVATE "-s")
set_target_properties(sc_video_capture_exe PROPERTIES OUTPUT_NAME "sc_video_capture_exe")
target_link_libraries(sc_video_capture_exe PRIVATE ${LIBS})
