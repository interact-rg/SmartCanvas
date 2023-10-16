#include "assert/sc_assert.h"
#include "sm/sc_sm.h"
#include "core/sc_core.h"
#include "logging/sc_logging.h"

void sc_sm_update(void) {
    sc_bool is_sm_proc_done = SC_TRUE;

    for (;;) {
        enum SC_STATE_MACHINE_STATE current_state = g_sc_context.core_sm.current_state;

        switch (current_state) {
        case SC_STATE_MACHINE_STATE_SETUP:
            sc_sm_handle_input_in_setup();
            is_sm_proc_done = SC_TRUE;
            break;
        case SC_STATE_MACHINE_STATE_REAL_TIME:
            is_sm_proc_done = SC_TRUE;
            break;
        case SC_STATE_MACHINE_STATE_PHOTO:
            is_sm_proc_done = SC_TRUE;
            break;
        default:
            SC_FATAL("Invalid state: %u\n", current_state);
            SC_ASSERT(0);
            is_sm_proc_done = SC_TRUE;
            break;
        }

        if (SC_TRUE == is_sm_proc_done) {
            break;
        }
    }
};

SC_LOCAL const char* sc_sm_state_as_string(enum SC_STATE_MACHINE_STATE state) {
    switch (state) {
    case SC_STATE_MACHINE_STATE_INVALID:
        return "SC_STATE_MACHINE_STATE_INVALID";
        break;
    case SC_STATE_MACHINE_STATE_SETUP:
        return "SC_STATE_MACHINE_STATE_SETUP";
        break;
    case SC_STATE_MACHINE_STATE_REAL_TIME:
        return "SC_STATE_MACHINE_STATE_REAL_TIME";
        break;
    default:
        return "string not found";
        break;
    }
    return NULL;
}

void sc_sm_state_enter(enum SC_STATE_MACHINE_STATE new_state)
{
    SC_TRC("leave state: '%s'", sc_sm_state_as_string(g_sc_context.core_sm.current_state));
    SC_TRC("enter state: '%s'", sc_sm_state_as_string(new_state));
    g_sc_context.core_sm.current_state = new_state;
}
