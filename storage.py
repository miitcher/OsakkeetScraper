""" csv-files separated by: ';' """

import os, datetime, logging

import scraping

logger = logging.getLogger('root')


def store_company_list(company_list, storage_directory, scrape_type):
    dt = datetime.datetime.today()
    # YY-MM-DD_HH-MM-SS
    datetime_str = "{:2.2}-{:0>2.2}-{:0>2.2}_{:0>2.2}-{:0>2.2}-{:0>2.2}".format( \
                    str(dt.year)[2:], str(dt.month), str(dt.day), \
                    str(dt.hour), str(dt.minute), str(dt.second))
    tsv_filename = storage_directory + "\\scrape_{}_{}.tsv".format(scrape_type, datetime_str)

    with open(tsv_filename, "w") as f:
        f.write("Companies scraped from www.kauppalehti.fi\n" +\
                "scrape_{}\n".format(scrape_type) +\
                "Date:\t{}\n".format(datetime_str) +\
                "###")
        if scrape_type == "names":
            for i in company_list:
                f.write("\n{}\t{}".format(i, company_list[i]))
        else:
            for company in company_list:
                f.write(company.tsv_raw)

    logger.debug("Stored scrape_{} into: {}".format(scrape_type, tsv_filename))
    return tsv_filename

def get_stored_company_list(filename):
    logger.debug("Reading from file: " + filename)
    company_list = []
    scrape_type = None
    body_lines = False
    line = True
    company = None
    sub_header = None # e.g. Osingot, Perustiedot
    with open(filename, "r") as f:
        while line:
            line = f.readline()

            if body_lines and line:
                try:
                    parts = line.strip().split("\t")
                except ValueError:
                    logger.error("Error in file [{}] with line [{}].".format(filename, line))
                    return None, None
                print(parts)

                if parts[0].startswith("##"):
                    print("-------Next company")
                    if company:
                        company_list.append(company)
                    company = scraping.Company(int(parts[1]))
                elif parts[0].startswith("#"):
                    print("-------Next sub_header")
                    if sub_header:
                        pass
                    sub_header = parts[0].strip("# ")

            elif body_lines and not line:
                if company:
                    company_list.append(company)

            if not body_lines:
                print(line.rstrip())
                if line.startswith("scrape"):
                    type_parts = line.strip().split("_")
                    if len(type_parts) == 1:
                        scrape_type = "metrics"
                    else:
                        scrape_type = type_parts[1]
                elif line.startswith("###"):
                    body_lines = True
                    if not scrape_type:
                        logger.error("No scrape_type")
                        return None, None

    return company_list, scrape_type

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
            body_lines = False
            line = True
            with open(matching_filename, "r") as f:
                while line:
                    line = f.readline()
                    if body_lines and line:
                        try:
                            c_id, c_name = line.strip().split("\t")
                            c_id = int(c_id)
                            company_names[c_id] = c_name
                        except ValueError:
                            logger.error("Error in names file [{}] with line [{}]. Will scrape names.".format(matching_filename, line))
                            return None
                    if line.startswith("###"):
                        body_lines = True
            return company_names
    return None
