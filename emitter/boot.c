#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "dhcpserver.h"

int main() {
    stdio_init_all();
    if (cyw43_arch_init()) {
        printf("Wi-Fi init failed");
        return -1;
    }

    cyw43_arch_enable_ap_mode("pico-test", "1234", CYW43_AUTH_OPEN);

    ip4_addr_t mask;
    ip4_addr_t gw;
    IP4_ADDR(ip_2_ip4(&gw), 192, 168, 4, 1);
    IP4_ADDR(ip_2_ip4(&mask), 255, 255, 255, 0);

    // Start the dhcp server
    dhcp_server_t dhcp_server;
    dhcp_server_init(&dhcp_server, &gw, &mask);

    while (true) {
        // cyw43_arch_poll();
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
        sleep_ms(250);
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
        sleep_ms(250);
    }
}