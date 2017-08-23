import unittest, os, time
from multiprocessing import Queue
import scrape_logger

import scrapeKL_gui


level = "WARNING"
#level = "INFO"
#level = "DEBUG"
logger = scrape_logger.setup_logger(level)


storage_directory = "scrapes"


class Test(unittest.TestCase):

    def test_scrapeThread(self):
        company_names = {
            2048: "talenom",
            1102: "cramo",
            1091: "sanoma",
            1196: "afarak group"
        }
        #company_names = None # For scraping every company
        showProgress = False
        queue = Queue()

        time0 = time.time()
        qThread = scrapeKL_gui.scrapeThread(storage_directory, company_names,
                                            showProgress, queue)
        qThread.start()
        qThread.wait()
        logger.debug("\nScraping time: {:.2f} s".format(time.time() - time0))

        # .get() waits on the next value.
        # Then .join() is not needed for processes.
        metrics_list, failed_company_dict, metricsfilename = queue.get()

        self.assertIsInstance(metricsfilename, str)
        for metrics in metrics_list:
            self.assertIsInstance(metrics, dict)
            self.assertGreater(len(metrics), 1)
            logger.debug("company_name: {}".format(metrics['company_name']))
        for company_id in failed_company_dict:
            logger.debug("Failed list: ({}, {})".format(
                company_id, failed_company_dict[company_id])
            )

        self.assertEqual(len(failed_company_dict), 0)
        self.assertEqual(len(metrics_list), 4)

        os.remove(metricsfilename)


if __name__ == '__main__':
    unittest.main()
