#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "hardware/adc.h"

// between 0V and 3.3V (Maximum) at a resolution of 0.81mV (3.3 / 4095)
const float conversion_factor = 3.3f / (1 << 12);
const float threshhold = 0.007f;

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

    uint sensor_adc_pin = 0;


    adc_init();


    // Make sure GPIO is high-impedance, no pullups etc
    adc_gpio_init(26);

    // Select ADC input 0 (GPIO26)
    adc_select_input(0);

    uint led = 14;
    gpio_init(led);
    gpio_set_dir(led, GPIO_OUT);

    toggle_led();

    while (true)
    {
        uint16_t result = adc_read();

        //Converts the ADC reading into Voltage
        result *= conversion_factor;

        gpio_put(led, (result >= 0.2f));
        
        toggle_led();

        sleep_ms(100);
    }
}