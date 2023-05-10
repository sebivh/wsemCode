cmake_minimum_required(VERSION 3.19)

set(SUB_PROJ_NAME reciver)

add_executable(${SUB_PROJ_NAME}
        boot.c
)

target_include_directories(${SUB_PROJ_NAME} PRIVATE ${CMAKE_CURRENT_LIST_DIR} )

target_link_libraries(${SUB_PROJ_NAME}
        pico_cyw43_arch_lwip_threadsafe_background
        pico_stdlib
        )

pico_add_extra_outputs(${SUB_PROJ_NAME})