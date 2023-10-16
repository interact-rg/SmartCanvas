#include <stdarg.h>
#include <stdio.h>

#include "sc_typedef.h"
#include "logging/sc_logging.h"

void sc_log(
    enum sc_LogLevel level,
    const char*        format,
    ...)
{
    va_list args;
    va_start(args, format);

    /* Choose an appropriate output stream based on the debug level */
    FILE* output = stdout;

     /* Print the log message */
    static const char* log_level[] = {
        "SC FATL",
        "SC ERR ",
        "SC WARN",
        "SC INFO",
        "SC DBG ",
        "SC TRC "
    };

    fprintf(output, "[%s] ", log_level[level]);
    vfprintf(output, format, args);
    fprintf(output, "\n");

    va_end(args);
}

