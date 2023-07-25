/**
 * Code for the Embedded Laser Interface
*/

#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"

class Laser
{
private:
    uint pin;
    uint32_t syncDelay;
    void openConnc();
    void closeConnc();
public:
    Laser(uint pin, uint32_t syncDelay);
    void sendBit(bool data);
    void sendByte(char data);
    void send(char data[]);
};

Laser::Laser(uint pin, uint32_t syncDelay)
{
    this->pin = pin;
    gpio_init(pin);
    gpio_set_dir(pin, GPIO_OUT);
    this->syncDelay = syncDelay;
}

//Send 1 for 2 Seconds and opens Connection
void Laser::openConnc() {
    gpio_put(pin, 0);
    gpio_put(pin, 1);
    sleep_ms(2 * 1000);
    gpio_put(pin, 0);
    sleep_ms(syncDelay);
}

//Send 1 for 2 Seconds and Closes Connection
void Laser::closeConnc() {
    gpio_put(pin, 0);
    gpio_put(pin, 1);
    sleep_ms(2 * 1000);
    gpio_put(pin, 0);
}

void Laser::sendBit(bool data) {
    openConnc();
    gpio_put(pin, 1);
    sleep_ms(syncDelay);
    gpio_put(pin, 0);
    closeConnc();
}

void Laser::sendByte(char data) {
    openConnc();
    for (size_t i = 0; i < sizeof(char); i++)
    {
        //Sets the Bit according to the Data
        gpio_put(pin, (data >> i) & 1);
        sleep_ms(syncDelay);
    }
    gpio_put(pin, 0);
    closeConnc();
}

void Laser::send(char data[]) {
    openConnc();
    for (size_t i = 0; i < strlen(data); i++)
    {
        //Byte of Byte Array
        char c = data[i];
        //Send Bits of Byte
        for (size_t ii = 0; ii < sizeof(char); ii++)
        {
            //Sets the Bit according to the Data
            gpio_put(pin, (c >> ii) & 1);
            sleep_ms(syncDelay);
        }
    }
    closeConnc();
}