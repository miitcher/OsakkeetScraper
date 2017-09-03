import unittest
import scrape_logger

import speed

level = "WARNING"
#level = "INFO"
#level = "DEBUG"
logger_root  = scrape_logger.setup_logger(level)
logger_speed = scrape_logger.setup_logger(level, name="speed")


class Test(unittest.TestCase):
    def test_speed(self):
        # smoketest
        speed.run_speedtest(1)


if __name__ == '__main__':
    unittest.main()
