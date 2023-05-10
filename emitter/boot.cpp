#include "pico/stdlib.h"
#include "stdio.h"
#include "pico/cyw43_arch.h"
#include "dhcpserver.h"
#include "lwip/udp.h"
#include "Laser.hpp"

typedef struct {
    uint8_t op; // message opcode
    uint8_t htype; // hardware address type
    uint8_t hlen; // hardware address length
    uint8_t hops;
    uint32_t xid; // transaction id, chosen by client
    uint16_t secs; // client seconds elapsed
    uint16_t flags;
    uint8_t ciaddr[4]; // client IP address
    uint8_t yiaddr[4]; // your IP address
    uint8_t siaddr[4]; // next server IP address
    uint8_t giaddr[4]; // relay agent IP address
    uint8_t chaddr[16]; // client hardware address
    uint8_t sname[64]; // server host name
    uint8_t file[128]; // boot file name
    uint8_t options[312]; // optional parameters, variable, starts with magic
} dhcp_msg_t;

void openAccessesPoint() {
    cyw43_arch_enable_ap_mode("pico-test", "1234", CYW43_AUTH_OPEN);

    ip4_addr_t mask;
    ip4_addr_t gw;
    IP4_ADDR(ip_2_ip4(&gw), 192, 168, 4, 1);
    IP4_ADDR(ip_2_ip4(&mask), 255, 255, 255, 0);

    // Start the dhcp server
    dhcp_server_t dhcp_server;
    dhcp_server_init(&dhcp_server, &gw, &mask);
}


static uint8_t *opt_find(uint8_t *opt, uint8_t cmd) {
    for (int i = 0; i < 308 && opt[i] != 255;) {
        if (opt[i] == cmd) {
            return &opt[i];
        }
    }
}
/**
 * Adapting udp_recv_fn function prototype
 * 
 * @param arg user supplied argument (udp_pcb.recv_arg)
 * @param pcb the udp_pcb which received data
 * @param p the packet buffer that was received
 * @param addr the remote IP address from which the packet was received
 * @param port the remote port from which the packet was received
 */
static void respond(void *arg, udp_pcb *pcb, pbuf *p, const ip_addr_t *addr, u16_t port) {
    printf("Received response");

    dhcp_msg_t dhcp_msg;
    //Copies the buffer from the UDP Packatge into the dhcp_msg_t Structure for easier accsess.
    pbuf_copy_partial(p, &dhcp_msg, sizeof(dhcp_msg), 0);

    uint8_t *opt = (uint8_t *)&dhcp_msg.options;
    opt += 4; // assume magic cookie: 99, 130, 83, 99

    uint8_t *msgtype = opt_find(opt, 53);

        switch (msgtype[2]) {
            //DHCPDISCOVER
            case 1: {

            }
        }
}

class DhcpServer
{
private:
struct dhcp_args
{
    int lol;
};

public:
    DhcpServer();
    ~DhcpServer();
};

DhcpServer::DhcpServer()
{
    dhcp_args* args;

    udp_pcb* pcb = udp_new();

    udp_recv(pcb, (udp_recv_fn) &respond, args);
}

DhcpServer::~DhcpServer()
{
}

bool led_active = false;
bool toggle_led() {
    if(led_active) {
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
    } else {
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
    }
}

int main() {
    stdio_init_all();
    if (cyw43_arch_init()) {
        printf("Wi-Fi init failed");
        return -1;
    }

    while (true) {
        // cyw43_arch_poll();
        toggle_led();
        sleep_ms(250);
    }
}