cmake_minimum_required(VERSION 3.19)

add_executable(emitter_boot
        boot.c
        dhcpserver/dhcpserver.c
)

target_include_directories(emitter_boot PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}
        ${CMAKE_CURRENT_LIST_DIR}/dhcpserver
        )

target_link_libraries(emitter_boot
        pico_cyw43_arch_lwip_threadsafe_background
        pico_stdlib
        )

pico_add_extra_outputs(emitter_boot)

pico_enable_stdio_usb(emitter_boot 0)
pico_enable_stdio_uart(emitter_boot 1)