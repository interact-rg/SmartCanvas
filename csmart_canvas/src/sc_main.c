/* includes all *.c files to be compiled. Reduces compile times*/

#include "sc_typedef.h"
#include "sc_config.h"

#include "core/sc_core.h"

int main(void){
    sc_bool res = sc_init(NULL);

    if (SC_TRUE == res) {
        while(!sc_do_frame());
        return 0;
    } else {
        return 1;
    }
}
