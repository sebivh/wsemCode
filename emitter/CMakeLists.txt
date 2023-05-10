cmake_minimum_required(VERSION 3.19)

set(SUB_PROJ_NAME emitter)

add_executable(${SUB_PROJ_NAME}
boot.cpp
dhcpserver/dhcpserver.c
)

target_include_directories(${SUB_PROJ_NAME} PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
    ${CMAKE_CURRENT_LIST_DIR}/dhcpserver
    ${CMAKE_CURRENT_LIST_DIR}/embedded
)

target_link_libraries(${SUB_PROJ_NAME}
pico_cyw43_arch_lwip_threadsafe_background
pico_stdlib
)

pico_add_extra_outputs(${SUB_PROJ_NAME})

pico_enable_stdio_usb(${SUB_PROJ_NAME} 0)
pico_enable_stdio_uart(${SUB_PROJ_NAME} 1)

add_subdirectory(embedded)