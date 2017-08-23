import sys, os, time, logging
from datetime import date

import scrape_logger
import scraping
import scrapeKL

logger = logging.getLogger('speed')


storage_directory = "speed"
speed_filename = "speed_run.log"


def main(times):
    assert isinstance(times, int)
    # Storage
    if not os.path.isdir(storage_directory):
        os.makedirs(storage_directory)
        logger.debug("speed-folder created: [{}]".format(storage_directory))

    old_avg_time = get_old_avg_time()
    whole_run_time = check_scrape_speed(old_avg_time, times)

    store_speed_run(times, whole_run_time)

    # Cleanup
    if storage_directory != "scrapes":
        speed_filenames = os.listdir(storage_directory)
        for filename_end in speed_filenames:
            filename = storage_directory + "\\" + filename_end
            os.remove(filename)

def store_speed_run(times, whole_run_time):
    date_str = date.today().strftime(scraping.date_short_format) # YY-MM-DD
    line_str = "{}\t{}\t{:.2f}\n".format(date_str, times, whole_run_time)
    logger.debug("Store line: [{}]".format(line_str))
    with open(speed_filename, "a") as f:
        f.write(line_str)

def get_old_avg_time():
    with open(speed_filename, "r") as f:
        lines = f.readlines()
    time_sum = 0
    all_times = 0
    for line in lines:
        try:
            date, times, whole_run_time = line.strip().split("\t")
            time_sum += float(whole_run_time)
            all_times += int(times)
        except:
            pass
    if all_times:
        return time_sum / all_times
    else:
        return 0

def check_scrape_speed(old_avg_time, times):
    assert isinstance(times, int) and times > 0
    assert isinstance(old_avg_time, float) and old_avg_time > 0, \
        "old_avg_time: {}".format(old_avg_time)
    expected_time = times * old_avg_time
    logger.info(
        "\tScraping {} times\n".format(times) + \
        "Old average time per scraping:\t{:6.2f} s\n".format(old_avg_time) + \
        "Expected time:\t\t\t{:6.2f} s".format(expected_time)
    )

    c = 0
    time0 = time.time()
    while c < times:
        _company_names = scrapeKL.scrape_companies(storage_directory)
        c += 1

    whole_run_time = time.time() - time0

    avg_time = whole_run_time / times
    compared = avg_time - old_avg_time
    compared_percent = 100 * compared / old_avg_time
    logger.info(
        "- Scraping took:\t\t{:6.2f} s\n".format(whole_run_time) + \
        "Average time per scraping:\t{:6.2f} s\n".format(avg_time) + \
        "Compared to old average:\t{:+6.2f} s --> {:+.1f} %".format(
            compared, compared_percent
        )
    )
    return whole_run_time


if __name__ == '__main__':
    logger_root = scrape_logger.setup_logger("WARNING")
    logger = scrape_logger.setup_logger(name="speed")

    times = 5
    if len(sys.argv) == 2:
        try:
            times = int(sys.argv[1])
        except ValueError:
            pass

    main(times)
