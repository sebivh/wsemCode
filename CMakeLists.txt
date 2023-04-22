cmake_minimum_required(VERSION 3.19)

include(pico_sdk_import.cmake)

project(blink_project)

set(PICO_BOARD pico_w)

pico_sdk_init()

add_subdirectory(emitter)
add_subdirectory(reciver)