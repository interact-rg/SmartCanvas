cmake_minimum_required(VERSION 3.24.3)

set(CMAKE_C_COMPILER clang)

project(c_smart_canvas LANGUAGES C)

find_package(OpenGL REQUIRED)
find_package(X11 REQUIRED)
find_package(SDL2 REQUIRED)
find_package(GLEW REQUIRED)

add_subdirectory(dependencies/sc_video_capture)
add_subdirectory(dependencies/sc_filter)

set(SRC
  src/sc_main.c
  src/logging/sc_logging.c
  src/core/sc_core.c
  src/sm/sc_sm.c
  src/sm/sc_sm_setup.c
  src/renderer/sc_renderer.c
  src/renderer/sc_builtin_shaders.c
  src/renderer/sc_font.c
  src/math/sc_math.c
)

set(INCLUDE_DIRS
  PRIVATE "include/"
  PRIVATE "dependencies/"
  PRIVATE "dependencies/sc_video_capture/include/"
  PRIVATE "dependencies/sc_filter/include/"
)

set(LIBS
  -lGL
  -lX11
  -lm
  -lrt
  -lSDL2
  -lGLEW
  sc_video_capture_release
  sc_filter_release
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
add_library(debug SHARED ${SRC})
target_compile_options(debug PRIVATE ${WARNINGS})
target_compile_options(debug PRIVATE ${DEBUG_COMPILE_OPTIONS})
target_compile_definitions(debug PRIVATE _DEBUG)
target_include_directories(debug PRIVATE ${INCLUDE_DIRS})
set_target_properties(debug PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib/
)
set_target_properties(debug PROPERTIES OUTPUT_NAME "csmartcanvas_debug")
target_link_libraries(debug PRIVATE ${LIBS})

# ========================================
# release build
# ========================================
add_library(release SHARED ${SRC})
target_compile_options(release PRIVATE ${WARNINGS})
target_compile_options(release PRIVATE ${RELEASE_COMPILE_OPTIONS})
target_compile_definitions(release PRIVATE _RELEASE)
target_include_directories(release PRIVATE ${INCLUDE_DIRS})
set_target_properties(release PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib/
)
target_link_options(release PRIVATE "-s")
set_target_properties(release PROPERTIES OUTPUT_NAME "csmartcanvas")
target_link_libraries(release PRIVATE ${LIBS})


# ========================================
# executable build
# ========================================
add_executable(executable ${SRC})
target_compile_options(executable PRIVATE ${WARNINGS})
target_compile_options(executable PRIVATE ${RELEASE_COMPILE_OPTIONS})
target_compile_definitions(executable PRIVATE _DEBUG)
target_include_directories(executable PRIVATE ${INCLUDE_DIRS})
#target_link_options(executable PRIVATE "-s")
set_target_properties(executable PROPERTIES OUTPUT_NAME "csmartcanvas_exe")
target_link_libraries(executable PRIVATE ${LIBS})
