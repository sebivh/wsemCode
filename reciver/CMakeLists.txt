cmake_minimum_required(VERSION 3.19)

add_executable(reciver_boot
        boot.c
)

target_include_directories(reciver_boot PRIVATE ${CMAKE_CURRENT_LIST_DIR} )

target_link_libraries(reciver_boot
        pico_cyw43_arch_lwip_threadsafe_background
        pico_stdlib
        )

pico_add_extra_outputs(reciver_boot)