#ifndef SC_SM_H
#define SC_SM_H

#include <stdint.h>

enum SC_STATE_MACHINE_STATE {
    SC_STATE_MACHINE_STATE_INVALID = 0,
    SC_STATE_MACHINE_STATE_SETUP,
    SC_STATE_MACHINE_STATE_GDPR,
    SC_STATE_MACHINE_STATE_REAL_TIME,
    SC_STATE_MACHINE_STATE_PHOTO,
    SC_STATE_MACHINE_STATE_COUNT,
};

enum SC_STATE_MACHINE_INPUT_MSG {
    SC_STATE_MACHINE_INPUT_MSG_INVALID = 0,
};

struct sc_StateMachineInput {
    enum SC_STATE_MACHINE_INPUT_MSG msg_id;

    union {
        int32_t data_i32;
    };

    struct sc_StateMachineInput* p_next;
};

struct sc_StateMachine {
    enum SC_STATE_MACHINE_STATE  current_state;
    struct sc_StateMachineInput* input_queue;
};

// main SM loop
void sc_sm_update(void);

void sc_sm_state_enter(enum SC_STATE_MACHINE_STATE new_state);

// input message is forwarded to main state handler
void sc_sm_handle_input_in_setup(void);

#endif
