import unittest, logging, os, time
from multiprocessing import Queue

import scrapeKL_gui


SHOW_DEBUG = False

logger = logging.getLogger('root')
logging.basicConfig(
    format="%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s"
)
if not SHOW_DEBUG:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)


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
        json_metrics_list, failed_company_dict, metricsfilename = queue.get()

        self.assertIsInstance(metricsfilename, str)
        for json_metrics in json_metrics_list:
            self.assertIsInstance(json_metrics, str)
            self.assertGreater(len(json_metrics), 35)
            if len(json_metrics) < 100:
                logger.debug("Failed: " + json_metrics[1:])
            else:
                logger.debug(json_metrics[1:80] + "...")
        for company_id in failed_company_dict:
            logger.debug("Failed list: ({}, {})".format(
                company_id, failed_company_dict[company_id])
            )

        self.assertEqual(len(failed_company_dict), 0)
        self.assertEqual(len(json_metrics_list), 4)

        os.remove(metricsfilename)


if __name__ == '__main__':
    unittest.main()
