cmake_minimum_required(VERSION 3.24.3)

set(CMAKE_C_COMPILER clang++)

project(sc_filter LANGUAGES CXX)

find_package(OpenCV REQUIRED)

set(SRC
  src/sc_filter.cpp
)

set(INCLUDE_DIRS
  PRIVATE "include/"
  PRIVATE "../mediapipe/"
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
add_library(sc_filter_debug SHARED ${SRC})
target_compile_options(sc_filter_debug PRIVATE ${WARNINGS})
target_compile_options(sc_filter_debug PRIVATE ${DEBUG_COMPILE_OPTIONS})
target_compile_definitions(sc_filter_debug PRIVATE _DEBUG)
target_include_directories(sc_filter_debug PRIVATE ${INCLUDE_DIRS})
set_target_properties(sc_filter_debug PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib/
)
set_target_properties(sc_filter_debug PROPERTIES OUTPUT_NAME "sc_filter_debug")
target_link_libraries(sc_filter_debug PRIVATE ${LIBS})

# ========================================
# release build
# ========================================
add_library(sc_filter_release SHARED ${SRC})
target_compile_options(sc_filter_release PRIVATE ${WARNINGS})
target_compile_options(sc_filter_release PRIVATE ${RELEASE_COMPILE_OPTIONS})
target_compile_definitions(sc_filter_release PRIVATE _RELEASE)
target_include_directories(sc_filter_release PRIVATE ${INCLUDE_DIRS})
set_target_properties(sc_filter_release PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib/
)
target_link_options(sc_filter_release PRIVATE "-s")
set_target_properties(sc_filter_release PROPERTIES OUTPUT_NAME "sc_filter")
target_link_libraries(sc_filter_release PRIVATE ${LIBS})

# ========================================
# exe build
# ========================================
add_executable(sc_filter_exe ${SRC})
target_compile_options(sc_filter_exe PRIVATE ${WARNINGS})
target_compile_options(sc_filter_exe PRIVATE ${RELEASE_COMPILE_OPTIONS})
target_compile_definitions(sc_filter_exe PRIVATE _EXE)
target_include_directories(sc_filter_exe PRIVATE ${INCLUDE_DIRS})
set_target_properties(sc_filter_exe PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib/
)
target_link_options(sc_filter_exe PRIVATE "-s")
set_target_properties(sc_filter_exe PROPERTIES OUTPUT_NAME "sc_filter_exe")
target_link_libraries(sc_filter_exe PRIVATE ${LIBS})
