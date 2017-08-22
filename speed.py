import os, time

import scrape_logger
import scrapeKL


storage_directory = "speed"


def main():
    old_avg = 17.93 # s
    times = 1
    check_scrape_speed(old_avg, times)

def check_scrape_speed(old_avg, times):
    assert isinstance(times, int) and times > 0
    expected_time = times * old_avg
    logger.info(
        "Started scraping {} times\n".format(times) + \
        "Old average time per scraping:\t{:6.2f} s\n".format(old_avg) + \
        "Expected time:\t\t\t{:6.2f} s".format(expected_time)
    )
    time0 = time.time()
    c = 0
    while c < times:
        _company_names = scrapeKL.scrape_companies(storage_directory)
        c += 1
    time_diff = time.time() - time0
    time_avg = time_diff / times
    comp = time_avg - old_avg
    comp_percent = 100 * comp / old_avg

    logger.info(
        "- Scraping took:\t\t{:6.2f} s\n".format(time_diff) + \
        "Average time per scraping:\t{:6.2f} s\n".format(time_avg) + \
        "Compared to old average:\t{:+6.2f} s --> {:+.1f} %".format(
            comp, comp_percent
        )
    )


if __name__ == '__main__':
    logger_root = scrape_logger.setup_logger()
    scrape_logger.set_logger_level(logger_root, "WARNING")
    logger = scrape_logger.setup_logger(name="speed")

    # Storage
    if not os.path.isdir(storage_directory):
        os.makedirs(storage_directory)
        logger.debug("speed-folder created: [{}]".format(storage_directory))

    main()

    # Cleanup
    if storage_directory != "scrapes" and False:
        speed_filenames = os.listdir(storage_directory)
        for filename_end in speed_filenames:
            filename = storage_directory + "\\" + filename_end
            os.remove(filename)
