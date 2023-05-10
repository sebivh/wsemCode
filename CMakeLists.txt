cmake_minimum_required(VERSION 3.19)

include(pico_sdk_import.cmake)
include(pico_extras_import.cmake)

pico_sdk_init()

set(PICO_BOARD pico_w)

project(wSeminar)

add_subdirectory(emitter)
add_subdirectory(reciver)