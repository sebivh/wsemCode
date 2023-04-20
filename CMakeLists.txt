cmake_minimum_required(VERSION 3.19)

include(pico_sdk_import.cmake)

project(blink_project)

set(PICO_BOARD pico_w)

pico_sdk_init()

add_executable(blink
        blink.c
)

target_include_directories(blink PRIVATE ${CMAKE_CURRENT_LIST_DIR} )

target_link_libraries(blink
        pico_cyw43_arch_lwip_threadsafe_background
        pico_stdlib
        )

pico_add_extra_outputs(blink)

add_subdirectory(emitter)
add_subdirectory(reciver)