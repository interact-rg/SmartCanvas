#ifndef SC_LOGGING_H
#define SC_LOGGING_H

#include "sc_config.h"

enum sc_LogLevel {
    SC_LOG_LEVEL_FATAL = 0,
    SC_LOG_LEVEL_ERROR,
    SC_LOG_LEVEL_WARNING,
    SC_LOG_LEVEL_INFO,
    SC_LOG_LEVEL_DEBUG,
    SC_LOG_LEVEL_TRACE,
};

void sc_log(
    enum sc_LogLevel level,
    const char*        format,
    ...);


#define SC_FATAL(msg, ...) do {sc_log(SC_LOG_LEVEL_FATAL, msg, ##__VA_ARGS__);} while(0)
#define SC_ERROR(msg, ...) do {sc_log(SC_LOG_LEVEL_ERROR, msg, ##__VA_ARGS__);} while(0)

#ifdef SC_LOG_LEVEL_WARNING_ENABLE
#define SC_WARN(msg, ...) do {sc_log(SC_LOG_LEVEL_WARNING, msg, ##__VA_ARGS__);} while(0)
#else
#define SC_WARN(msg, ...)
#endif /* SC_LOG_LEVEL_WARNING_ENABLE */

#ifdef SC_LOG_LEVEL_INFO_ENABLE
#define SC_INFO(msg, ...) do {sc_log(SC_LOG_LEVEL_INFO, msg, ##__VA_ARGS__);} while(0)
#else
#define SC_INFO(msg, ...)
#endif /* #if SC_LOG_LEVEL_INFO_ENABLE */

#ifdef SC_LOG_LEVEL_DEBUG_ENABLE
#define SC_DEBUG(msg, ...) do {sc_log(SC_LOG_LEVEL_DEBUG, msg, ##__VA_ARGS__);} while(0)
#else
#define SC_DEBUG(msg, ...)
#endif /* #if SC_LOG_LEVEL_DEBUG_ENABLE */

#ifdef SC_LOG_LEVEL_TRACE_ENABLE
#define SC_TRC(msg, ...) do {sc_log(SC_LOG_LEVEL_TRACE, msg, ##__VA_ARGS__);} while(0)
#else
#define SC_TRC(msg, ...)
#endif /* #if SC_LOG_LEVEL_TRACE_ENABLE */

#endif
