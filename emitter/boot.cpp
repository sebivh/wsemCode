#include "pico/stdlib.h"
#include "stdio.h"
#include "pico/cyw43_arch.h"
#include "Laser.hpp"

bool led_active = false;
void toggle_led() {
    if(led_active) {
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
        led_active = false;
    } else {
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
        led_active = true;
    }
}

int main() {
    stdio_init_all();
    if (cyw43_arch_init()) {
        printf("Wi-Fi init failed");
        return -1;
    }

    toggle_led();

    Laser dataLaser = Laser(2, 1000);
    dataLaser.sendByte('h');

    toggle_led();
}