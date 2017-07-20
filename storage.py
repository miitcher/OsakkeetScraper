""" csv-files separated by: ';' """

import os, datetime, logging

logger = logging.getLogger('root')


def store_company_list(company_list, storage_directory, scrape_type=""):
    if scrape_type != "":
        scrape_type = "_" + scrape_type
    dt = datetime.datetime.today()
    # YY-MM-DD_HH-MM-SS
    datetime_str = "{:2.2}-{:0>2.2}-{:0>2.2}_{:0>2.2}-{:0>2.2}-{:0>2.2}".format( \
                    str(dt.year)[2:], str(dt.month), str(dt.day), \
                    str(dt.hour), str(dt.minute), str(dt.second))
    tsv_filename = storage_directory + "\\scrape{}_{}.tsv".format(scrape_type, datetime_str)

    with open(tsv_filename, "w") as f:
        f.write("Companies scraped from www.kauppalehti.fi\n" +\
                "scrape{}\n".format(scrape_type) +\
                "Date:\t{}\n".format(datetime_str) +\
                "###")
        if scrape_type == "_names":
            for i in company_list:
                f.write("\n{}\t{}".format(i, company_list[i]))
        else:
            for company in company_list:
                f.write(company.tsv_raw)

    logger.debug("Stored scrape{} into: {}".format(scrape_type, tsv_filename))
    return tsv_filename

def get_stored_company_list(filename):
    print(filename)
    pass

def get_today_stored_company_names(storage_directory):
    dt = datetime.datetime.today()
    # YY-MM-DD_
    datetime_str = "{:2.2}-{:0>2.2}-{:0>2.2}_".format( \
                    str(dt.year)[2:], str(dt.month), str(dt.day))
    filename_start_today = "scrape_names_{}".format(datetime_str)

    files = os.listdir(storage_directory)
    for filename in files:
        if filename.startswith(filename_start_today):
            matching_filename = storage_directory +'\\'+ filename
            logger.debug("Using ready company names from file : " + matching_filename)
            company_names = {}
            right_lines = False
            line = True
            with open(matching_filename, "r") as f:
                while line:
                    line = f.readline()
                    if right_lines and line:
                        try:
                            c_id, c_name = line.strip().split("\t")
                            c_id = int(c_id)
                            company_names[c_id] = c_name
                        except ValueError:
                            logger.error("Error in names file on line: [{}]. Will scrape names.".format(line))
                            return None
                    if line.startswith("###"):
                        right_lines = True
            return company_names
    return None
