/**
 * Code for the Embedded Laser Interface
*/

#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"

class Laser
{
private:
    const uint* pin;
public:
    Laser(uint pin);
    void send(char data[]);
    ~Laser();
};

Laser::Laser(uint pin)
{
    this->pin = &pin;
}

void Laser::send(char data[]) {
    
}

Laser::~Laser()
{
}

