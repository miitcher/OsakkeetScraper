KNOWN_MISSING_tunnuslukuja_table_tag_LIST=[2048,1025,2050,2055,2025,2045,1953,2040,2026,2027,2033,2034,2035,2042,2046]
KNOWN_MISSING_KURSSI_TULOSTIEDOT_table_TAG=[1971,1083,1089,1104,1105,1970]  #Nama ovat pankkeja, ja niilla on erilaiset tunnusluvut.
c_KM_tulostiedot=30

ERROR_count=0   #ERROR voi olla MINOR ERROR!!!
MINOR_ERROR_count=0
EXPECTED_SERIOUS_ERROR_count= len(KNOWN_MISSING_tunnuslukuja_table_tag_LIST) + c_KM_tulostiedot
PRINTED_ERROR_count=0

ERROR_catch_list=[]


def matrix_print(matrix):
    for i in matrix:
        print(i)

def dictionary_print(dictionary):
    print("ID\tKEY")
    for ID in dictionary:
        print("[{}]\t[{}]".format(ID, dictionary[ID]))
    

def kurssi_tiedot_print(YRITYKSEN_TIEDOT):
    print("\n+++++TIEDOT PRINT\n+ KURSSI: {}\n\n+ KUVAUS YRITYKSESTA:\n{}\n\n+ PERUSTIEDOT DICTIONARY:".format(YRITYKSEN_TIEDOT[1], YRITYKSEN_TIEDOT[2]))
    dictionary_print(YRITYKSEN_TIEDOT[3])
    print("\n+ TUNNUSLUKUJA DICTIONARY:")
    dictionary_print(YRITYKSEN_TIEDOT[4])
    print("+++++\n")

def kurssi_tulostiedot_print(YRITYKSEN_TIEDOT):
    print("\n+++++TULOSTIEDOT PRINT\n+ TOIMINNAN LAAJUUS MATRIISI:")
    matrix_print(YRITYKSEN_TIEDOT[5])
    print("\n+ KANNATTAVUUS MATRIISI:")
    matrix_print(YRITYKSEN_TIEDOT[6])
    print("\n+ VAKAVARAISUUS MATRIISI:")
    matrix_print(YRITYKSEN_TIEDOT[7])
    print("\n+ MAKSUVALMIUS MATRIISI:")
    matrix_print(YRITYKSEN_TIEDOT[8])
    print("\n+ SIJOITTAJAN TUNNUSLUKUJA MATRIISI:")
    matrix_print(YRITYKSEN_TIEDOT[9])
    print("+++++\n")


def LOG_print(ID, success, f, description, is_minor_error=False):
    global ERROR_count
    global MINOR_ERROR_count
    global PRINTED_ERROR_count
    global ERROR_catch_list
    
    if success:
        suc="VALID"
    else:
        suc="ERROR"
        ERROR_count +=1
    
    if is_minor_error:
        miEr=" MINOR"
        MINOR_ERROR_count +=1
    else:
        miEr=""
    
    cond1 = (ID in KNOWN_MISSING_tunnuslukuja_table_tag_LIST) and description=="tunnuslukuja_table_TAG EI LOYTYNYT"
    cond2 = (ID in KNOWN_MISSING_KURSSI_TULOSTIEDOT_table_TAG) and f=="get_KURSSI_TULOSTIEDOT_table_TAG"
    
    msg='ID={},{}\t{},\tFunktion="{}",\tDescription="{}"'.format(ID, miEr, suc, f, description)
    if (not success) and (not is_minor_error):
        if cond1:
            #print(msg + "\tWAS EXPECTED")
            pass
        elif cond2:
            pass
        else:
            #if f=="get_KURSSI_TULOSTIEDOT_table_TAG" and ID not in ERROR_catch_list:
            #    ERROR_catch_list.append(ID)
            
            print(msg)
            PRINTED_ERROR_count +=1

def ERROR_LOG(ID, f, description, is_minor_error=False):
    global ERROR_count
    global MINOR_ERROR_count
    global PRINTED_ERROR_count
    global ERROR_catch_list
    
    ERROR_count +=1
    
    if is_minor_error:
        miEr=" MINOR"
        MINOR_ERROR_count +=1
    else:
        miEr=""
    
    cond1 = (ID in KNOWN_MISSING_tunnuslukuja_table_tag_LIST) and description=="tunnuslukuja_table_TAG EI LOYTYNYT"
    cond2 = (ID in KNOWN_MISSING_KURSSI_TULOSTIEDOT_table_TAG) and f=="get_KURSSI_TULOSTIEDOT_table_TAG"
    
    msg='ID={},{}\tERROR,\tFunction="{}",\tDescription="{}"'.format(ID, miEr, f, description)
    if not is_minor_error:
        if not cond1 and not cond2:
            print(msg)
            PRINTED_ERROR_count +=1

def errors_counts_print():
    SER_c = ERROR_count - MINOR_ERROR_count
    UNEXP_c = SER_c - EXPECTED_SERIOUS_ERROR_count
    print("***\n*TOTAL ERRORS\t{}\n**\n*MINOR ERRORS\t{}\n*SERIOUS ERRORS\t{}\n*PRINTED ERRORS\t{}"\
          .format(ERROR_count, MINOR_ERROR_count, SER_c, PRINTED_ERROR_count))
    print("**\n**\tCounts bellow applys only when scraping all ID:s!\n*EXPECTED SERIOUS ERRORS\t{}\n*UNEXPECTED SERIOUS ERRORS\t{}\n***"\
          .format(EXPECTED_SERIOUS_ERROR_count, UNEXP_c))
    if len(ERROR_catch_list) >0:
        print("\n***\n**\tERROR_catch_list:")
        for i in ERROR_catch_list:
            print(i)
        print("***")








