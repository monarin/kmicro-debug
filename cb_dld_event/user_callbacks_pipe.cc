#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <scTDC.h>
#include <inttypes.h>
#include <time.h>
#include <pthread.h>
#include <inttypes.h>

struct sc_DeviceProperties3 sizes;

struct PrivData {
    int cn_measures;
    int cn_tdc_events;
    int cn_dld_events;
    double total_time;
};

pthread_mutex_t pulseIdMutex = PTHREAD_MUTEX_INITIALIZER;

uint64_t lastPulseId = 0;
size_t totalEvents = 0;
size_t intervalEvents = 0;
size_t totalCorrupt = 0;
size_t intervalCorrupt = 0;
struct timespec startTime, lastIntervalTime;
bool hasPrintedStartTime = false;
struct timespec startWallTime;

void print_interval_report() {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    // Also get wall-clock time
    time_t wallNow = time(NULL);
    struct tm* tm_info = localtime(&wallNow);

    if (!hasPrintedStartTime) {
        char buffer[64];
        strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", tm_info);
        printf("\nMonitoring started — Date: %s\n", buffer);
        printf("Press Ctrl+C to stop.\n\n");
        printf("%-8s | %-10s | %-10s | %-10s\n", "Time", "Rate (kHz)", "Corrupt", "Corrupt %");
        printf("------------------------------------------------------\n");
        hasPrintedStartTime = true;
    }

    double elapsedInterval = (now.tv_sec - lastIntervalTime.tv_sec) +
                             (now.tv_nsec - lastIntervalTime.tv_nsec) / 1e9;

    if (elapsedInterval >= 3.0) {
        double rate = intervalEvents / elapsedInterval;
        double kHz = rate / 1000.0;
        double corruptPercent = (intervalEvents > 0) ? (100.0 * intervalCorrupt / intervalEvents) : 0.0;

        char buffer[16];
        strftime(buffer, sizeof(buffer), "%H:%M:%S", tm_info);
        printf("%-8s | %10.4f | %10lu | %9.6f%%\n",
               buffer, kHz, intervalCorrupt, corruptPercent);

        intervalEvents = 0;
        intervalCorrupt = 0;
        lastIntervalTime = now;
    }
}

void cb_dld_event(void *priv, const struct sc_DldEvent *const event_array, size_t event_array_len) {
    // Set this to true for Yves's test (constant all-1s pulse ID)
    // Set to false for normal advancing pulse ID test
    const bool checkAllOnes = true;

    struct PrivData *priv_data = (struct PrivData *)priv;
    priv_data->cn_dld_events++;

    const char *buffer = (const char *)event_array;
    for (size_t j = 0; j < event_array_len; ++j) {
        const struct sc_DldEvent *obj =
            (const struct sc_DldEvent *)(buffer + j * sizes.dld_event_size);

        uint64_t pulseId = obj->time_tag;

        // Lock mutex to protect shared state
        pthread_mutex_lock(&pulseIdMutex);

        // Case 1: Check against expected value (Yves's test)
        if (checkAllOnes) {
            if (pulseId != 0xFFFFFFFFFFFFFFFF) {
                time_t wallNow = time(NULL);
                struct tm* tm_info = localtime(&wallNow);
                char timeStr[16];
                strftime(timeStr, sizeof(timeStr), "%H:%M:%S", tm_info);

                printf("[%s] ❌ Non-all-1 PulseId Detected! PulseId: 0x%016" PRIx64 "\n", timeStr, pulseId);
                totalCorrupt++;
                intervalCorrupt++;
            }
        }

        // Case 2: Advancing Pulse ID check (your original logic)
        else {
            uint64_t maskedPulseId = pulseId & 0x00FFFFFFFFFFFFFF;

            if (maskedPulseId < lastPulseId) {
                int64_t pulseDiff = static_cast<int64_t>(maskedPulseId) - static_cast<int64_t>(lastPulseId);

                time_t wallNow = time(NULL);
                struct tm* tm_info = localtime(&wallNow);
                char timeStr[16];
                strftime(timeStr, sizeof(timeStr), "%H:%M:%S", tm_info);

                printf("[%s] 🔁 Corrupt Event! Last PulseId: %" PRIx64 ", Current PulseId: %" PRIx64 ", Difference: %" PRId64 "\n",
                       timeStr, lastPulseId, maskedPulseId, pulseDiff);

                totalCorrupt++;
                intervalCorrupt++;
            }

            lastPulseId = maskedPulseId;
        }

        totalEvents++;
        intervalEvents++;

        // Unlock mutex
        pthread_mutex_unlock(&pulseIdMutex);
    }

    print_interval_report();
}

int main() {
    int dd, ret;
    struct PrivData priv_data = {0, 0, 0, 0.0};
    char *buffer;
    struct sc_pipe_callbacks *cbs;
    struct sc_pipe_callback_params_t params;
    int pd;

    // Initialize device
    dd = sc_tdc_init_inifile("config/tdc_gpx3.ini");
    if (dd < 0) {
        char error_description[ERRSTRLEN];
        sc_get_err_msg(dd, error_description);
        printf("Error! Code: %d, Message: %s\n", dd, error_description);
        return dd;
    }

    ret = sc_tdc_get_device_properties(dd, 3, &sizes);
    if (ret < 0) {
        char error_description[ERRSTRLEN];
        sc_get_err_msg(ret, error_description);
        printf("Error! Code: %d, Message: %s\n", ret, error_description);
        return ret;
    }

    // Allocate callback structure
    buffer = (char *)calloc(1, sizes.user_callback_size);
    cbs = (struct sc_pipe_callbacks *)buffer;
    cbs->priv = &priv_data;
    cbs->dld_event = cb_dld_event;
    params.callbacks = cbs;

    pd = sc_pipe_open2(dd, USER_CALLBACKS, &params);
    if (pd < 0) {
        char error_description[ERRSTRLEN];
        sc_get_err_msg(pd, error_description);
        printf("Error! Code: %d, Message: %s\n", pd, error_description);
        return pd;
    }
    free(buffer);

    // Start measurement
    ret = sc_tdc_start_measure2(dd, 0);
    if (ret < 0) {
        char error_description[ERRSTRLEN];
        sc_get_err_msg(ret, error_description);
        printf("Error! Code: %d, Message: %s\n", ret, error_description);
        return dd;
    }

    // Start the timers
    clock_gettime(CLOCK_MONOTONIC, &startTime);
    lastIntervalTime = startTime;

    // Run for n seconds
    while (1) {
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);

        double elapsed = (now.tv_sec - startTime.tv_sec) +
                         (now.tv_nsec - startTime.tv_nsec) / 1e9;

        if (elapsed >= 300.0) {
            break;
        }
    }

    // Stop measurement
    sc_pipe_close2(dd, pd);
    sc_tdc_deinit2(dd);

    // Final report
    double elapsed = (lastIntervalTime.tv_sec - startTime.tv_sec) +
                     (lastIntervalTime.tv_nsec - startTime.tv_nsec) / 1e9;
    double avgRate = totalEvents / elapsed / 1000.0;
    printf("\n===== Test Summary =====\n");
    printf("Processed %lu events in %.1f seconds. Avg Rate: %.4f kHz\n",
           totalEvents, elapsed, avgRate);
    printf("Total Corrupted Events: %lu\n", totalCorrupt);
    printf("========================\n");

    // Destroy mutex before exiting
    pthread_mutex_destroy(&pulseIdMutex);

    return 0;
}
