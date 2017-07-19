# Can maby use the ID:s below to something, in some form...
KNOWN_MISSING_tunnuslukuja_table_tag_LIST=[2048,1025,2050,2055,2025,2045,1953,2040,2026,2027,2033,2034,2035,2042,2046]
KNOWN_MISSING_KURSSI_TULOSTIEDOT_table_TAG=[1971,1083,1089,1104,1105,1970]  #Nama ovat pankkeja, ja niilla on erilaiset tunnusluvut.
c_KM_tulostiedot=30

ERROR_count=0   #ERROR voi olla MINOR ERROR!!!
MINOR_ERROR_count=0
EXPECTED_SERIOUS_ERROR_count= len(KNOWN_MISSING_tunnuslukuja_table_tag_LIST) + c_KM_tulostiedot
PRINTED_ERROR_count=0

# The printing could be added to the classes
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
