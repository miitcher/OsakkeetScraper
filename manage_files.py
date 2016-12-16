import datetime

"""HUOM
csv-tiedotstot kirjoitetaan ';'-erottimella
"""

def get_dateNtime():
    dt=datetime.datetime.today()
    dateNtime = str(dt.year) +"_"+ str(dt.month) +"_"+ str(dt.day) \
    +"--"+ str(dt.hour) +"_"+ str(dt.minute) +"_"+ str(dt.second) +"_"+ str(dt.microsecond)
    return dateNtime

def DICT_YRITYKSEN_TIEDOT_csv_file_WRITE(DICT_YRITYKSEN_TIEDOT, scraped_IDs, DICT_yritys):
    filename = "Files\\" + "DICT_YRITYKSEN_TIEDOT-"+ get_dateNtime() + ".csv"
    
    f=open(filename, "w")
    f.write("HEADER;DICT_YRITYKSEN_TIEDOT;;;;;INFO:;Tiedot tallennetaan yrityksittain;;Tunnisteita:;ID;HEADER;ScrapedIDs;AllIDs;DATA")
    
    f.write("\nScrapedIDs")
    for ID in scraped_IDs:
        f.write(";{}".format(ID))
    
    f.write("\nAllIDs")
    for ID in DICT_yritys:
        f.write(";{}".format(ID))
    
    for ID in scraped_IDs:
        f.write("\nID;{};{}".format(ID, DICT_yritys[ID]))
        
        YRITYS_OSINKO_write_csv_part(f, DICT_YRITYKSEN_TIEDOT[ID])
        YRITYS_TIEDOT_write_csv_part(f, DICT_YRITYKSEN_TIEDOT[ID])
        YRITYS_TULOSTIEDOT_write_csv_part(f, DICT_YRITYKSEN_TIEDOT[ID])
    
    f.close()
    print("The data has been written to the file named: '{}'".format(filename))

def YRITYS_OSINKO_write_csv_part(f, YRITYKSEN_TIEDOT):
    osinko_mat=YRITYKSEN_TIEDOT[0]
    
    if osinko_mat[0]:
        f.write("\nDATA;0;True")
        c=0
        for r in osinko_mat:
            if c!=0:
                line="\n{};{};{};{};{};{};{}".format(r[0],r[1],r[2],r[3],r[4],r[5],r[6])
                f.write(line)
            c+=1
    else:
        f.write("\nDATA;0;False")

def YRITYS_TIEDOT_write_csv_part(f, YRITYKSEN_TIEDOT):
    kurssi=YRITYKSEN_TIEDOT[1]
    kuvaus=YRITYKSEN_TIEDOT[2]
    perus_dict=YRITYKSEN_TIEDOT[3]
    tunnus_dict=YRITYKSEN_TIEDOT[4]
    
    f.write("\nDATA;1;True")
    f.write("\n{}".format(kurssi))
    
    f.write("\nDATA;2;True")
    try:
        f.write("\n{}".format(kuvaus))
    except UnicodeError as e:
        print("VIRHE TALLENNUKSESSA: ", e)
    
    if perus_dict[0]:
        f.write("\nDATA;3;True")
        for r in perus_dict:
            if r!=0:
                line="\n{};{}".format(r, perus_dict[r])
                f.write(line)
    else:
        f.write("\nDATA;3;False")
    
    if tunnus_dict[0]:
        f.write("\nDATA;4;True")
        for r in tunnus_dict:
            if r!=0:
                line="\n{};{}".format(r, tunnus_dict[r])
                f.write(line)
    else:
        f.write("\nDATA;4;False")

def YRITYS_TULOSTIEDOT_write_csv_part(f, YRITYKSEN_TIEDOT):
    """
    toim_mat=YRITYKSEN_TIEDOT[5]
    kann_mat=YRITYKSEN_TIEDOT[6]
    vaka_mat=YRITYKSEN_TIEDOT[7]
    maks_mat=YRITYKSEN_TIEDOT[8]
    sijo_mat=YRITYKSEN_TIEDOT[9]
    """
    
    for i in range(5,10):
        matrix=YRITYKSEN_TIEDOT[i]
        if matrix[0]:
            f.write("\nDATA;{};True".format(i))
            c=0
            for r in matrix:
                if c!=0:
                    line="\n{};{};{};{};{};{}".format(r[0],r[1],r[2],r[3],r[4],r[5])
                    f.write(line)
                c+=1
        else:
            f.write("\nDATA;{};False".format(i))

def DICT_YRITYKSEN_TIEDOT_csv_file_READ(filename):
    DICT_YRITYKSEN_TIEDOT={}
    scraped_IDs=[]
    DICT_yritys={}
    
    f=open(filename, "r")
    
    ID=False
    DATA=False
    DATA_bool=None
    
    for r in f:
        strs=r.strip().split(";")
        #print(strs)
        
        if strs[0]=="HEADER":
            pass
        elif strs[0]=="AllIDs":
            c=0
            for i in strs:
                if c!=0:
                    try:
                        DICT_yritys[int(i)]=""
                    except:
                        pass
                c+=1
        elif strs[0]=="ScrapedIDs":
            c=0
            for i in strs:
                if c!=0:
                    try:
                        scraped_IDs.append(int(i))
                    except:
                        pass
                c+=1
        elif strs[0]=="ID":
            ID=int(strs[1])
            DICT_yritys[ID]=strs[2]
            
            DICT_YRITYKSEN_TIEDOT[ID]={}
            DICT_YRITYKSEN_TIEDOT[ID][0]=[]
            DICT_YRITYKSEN_TIEDOT[ID][3]={}
            DICT_YRITYKSEN_TIEDOT[ID][4]={}
            DICT_YRITYKSEN_TIEDOT[ID][5]=[]
            DICT_YRITYKSEN_TIEDOT[ID][6]=[]
            DICT_YRITYKSEN_TIEDOT[ID][7]=[]
            DICT_YRITYKSEN_TIEDOT[ID][8]=[]
            DICT_YRITYKSEN_TIEDOT[ID][9]=[]
            
        elif strs[0]=="DATA":
            DATA=int(strs[1])
            if strs[2]=="True":
                DATA_bool=True
                
                if DATA==0 or DATA>4:
                    DICT_YRITYKSEN_TIEDOT[ID][DATA].append(True)
                elif DATA==3 or DATA==4:
                    DICT_YRITYKSEN_TIEDOT[ID][DATA][0]=True
            else:
                DATA_bool=False
                
                if DATA==0 or DATA>4:
                    DICT_YRITYKSEN_TIEDOT[ID][DATA].append(False)
                elif DATA==3 or DATA==4:
                    DICT_YRITYKSEN_TIEDOT[ID][DATA][0]=False
                else:
                    DICT_YRITYKSEN_TIEDOT[ID][DATA]=False
        else:
            if DATA_bool:
                if DATA==0:
                    RIVI=[]
                    c=0
                    for i in strs:
                        if c==0:
                            try:
                                i=int(i)
                            except:
                                pass
                        elif c==2 or c==3 or c==5:
                            try:
                                i=float(i)
                            except:
                                pass
                        RIVI.append(i)
                        c+=1
                    DICT_YRITYKSEN_TIEDOT[ID][0].append(RIVI)
                elif DATA==1:
                    DICT_YRITYKSEN_TIEDOT[ID][1]=float(strs[0])
                elif DATA==2:
                    DICT_YRITYKSEN_TIEDOT[ID][2]=strs[0]
                elif DATA==3:
                    val=strs[1]
                    if strs[0]=='Osakkeet (KPL)':
                        try:
                            val=int(val)
                        except:
                            pass
                    DICT_YRITYKSEN_TIEDOT[ID][3][strs[0]]=val
                elif DATA==4:
                    val=strs[1]
                    try:
                        val=float(val)
                    except:
                        pass
                    DICT_YRITYKSEN_TIEDOT[ID][4][strs[0]]=val
                elif DATA>=5:
                    RIVI=[]
                    c=0
                    for i in strs:
                        if c!=0:
                            try:
                                i=float(i)
                            except:
                                pass
                        RIVI.append(i)
                        c+=1
                    DICT_YRITYKSEN_TIEDOT[ID][DATA].append(RIVI)
    
    
    """
    print(DICT_yritys)
    print(scraped_IDs)
    
    ID=2048
    for i in DICT_YRITYKSEN_TIEDOT[ID]:
        print(i)
        print(DICT_YRITYKSEN_TIEDOT[ID][i])
    """
    f.close()
    
    return DICT_YRITYKSEN_TIEDOT, scraped_IDs, DICT_yritys










