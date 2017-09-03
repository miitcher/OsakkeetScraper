import os, json, logging
from datetime import datetime, date

from scraping import datetime_format, date_short_format

logger = logging.getLogger('root')


class StorageException(Exception):
    pass


def store_names(storage_directory, company_names, names_filename=None):
    assert isinstance(company_names, dict)
    for company_id in company_names:
        assert isinstance(company_id, int)
        assert isinstance(company_names[company_id], str)

    datetime_str = datetime.now().strftime(datetime_format)
    if not names_filename:
        names_filename = storage_directory + "\\names_{}.tsv".format(
            datetime_str
        )

    with open(names_filename, "w") as f:
        f.write("source: www.kauppalehti.fi\n" +\
                "stored:\t{}\n###".format(datetime_str))
        for company_id in sorted(company_names, key=company_names.get):
            f.write("\n{}\t{}".format(company_id, company_names[company_id]))

    logger.debug("Stored names into: {}".format(names_filename))
    return names_filename

def load_names(names_filename):
    logger.debug("Loading names from file : {}".format(names_filename))
    company_names = {}
    in_body = False
    line = True
    with open(names_filename, "r") as f:
        while line:
            line = f.readline().strip()
            if not in_body:
                # header
                if line.startswith("###"):
                    in_body = True
            elif in_body and line:
                # body
                try:
                    c_id, c_name = line.split("\t")
                    c_id = int(c_id)
                    company_names[c_id] = c_name
                except ValueError:
                    logger.error("Invalid line [{}] in names file [{}]".format(
                        line, names_filename
                    ))
                    return None
    return company_names

def get_latest_metrics_filename(storage_directory):
    filenames = os.listdir(storage_directory)
    potential_filenames = []
    for filename in filenames:
        if filename.startswith("metrics_"):
            date_str = filename.replace("metrics_", "").replace(".json", "")
            try:
                dt = datetime.strptime(date_str, datetime_format)
                potential_filenames.append((filename, dt))
            except ValueError:
                logger.debug(
                    "{} filename did not match expected datetime format." \
                    .format(filename)
                )

    if not potential_filenames:
        return None

    """
    logger.debug("potential filenames:")
    for filename, dt in potential_filenames:
        logger.debug(filename)
    """

    return storage_directory + "\\" + sorted(potential_filenames,
                                             key=lambda tup: tup[1],
                                             reverse=True)[0][0]

def load_todays_names(storage_directory):
    date_str = date.today().strftime(date_short_format) # YY-MM-DD
    filename_start_today = "names_{}".format(date_str)
    logger.debug("filename_start_today: {}".format(filename_start_today))
    files = os.listdir(storage_directory)
    logger.debug("files: {}".format(files))
    for filename_end in files:
        if filename_end.startswith(filename_start_today):
            filename = storage_directory +'\\'+ filename_end
            company_names = load_names(filename)
            if len(company_names) < 100:
                raise StorageException("Too few companies: {}".format(len(company_names)))
            return company_names
    return None

def store_metrics(storage_directory, metrics_list, metrics_filename=None):
    assert isinstance(metrics_list, list)
    for metrics in metrics_list:
        assert isinstance(metrics, dict), metrics

    datetime_str = datetime.now().strftime(datetime_format)
    if not metrics_filename:
        metrics_filename = storage_directory + "\\metrics_{}.json".format(
            datetime_str
        )

    with open(metrics_filename, "w") as json_file:
        json.dump({"metrics": metrics_list}, json_file, indent=3)

    logger.debug("Stored metrics into: {}".format(metrics_filename))
    return metrics_filename

def load_metrics(metrics_filename):
    logger.debug("Loading metrics from file : {}".format(metrics_filename))
    with open(metrics_filename, "r") as json_file:
        metrics_dict = json.load(json_file)
    metrics_list = metrics_dict["metrics"]
    return metrics_list
