import os, sys, time, hashlib, json, datetime, shutil


def getDeltaFiles(filepath):
    '''Get data from json file and return 3 lists'''
    deltaDict = {}
    with open(filepath, 'r', encoding='utf-8') as Delta:
        deltaDict = json.load(Delta)
    changed, new, removed = [], [], []
    for delta in deltaDict:
        # checking if and Data and Storage have the file and 
        # that modified date of data file is later than modified date of Storage file
        if deltaDict[delta][0] != [] and deltaDict[delta][1] != []:
            changed.append(deltaDict[delta][0])
        if deltaDict[delta][0] != [] and deltaDict[delta][1] == []:
            new.append(deltaDict[delta][0])
        if deltaDict[delta][0] == [] and deltaDict[delta][1] != []:
            removed.append(deltaDict[delta][1])

    return changed, new, removed
    
def writeListOfFiles(root, doc):
    '''Create json file to save list of elements in the root path recursively'''
    
    dict = {}
    for path, subdirs, files in os.walk(root):
        for name in files:
            filepath = os.path.join(path, name)
            dict[filepath[len(root):]] = [name, path[len(root):], str(time.ctime(os.path.getmtime(filepath)))]
    with open(doc, 'w', encoding="utf-8") as f:
        json.dump(dict, f, sort_keys=True)

def isDataFileLaterStorageFile(datafile, storagefile):
    '''Compare two dates in string format.'''
    
    datafile = datetime.datetime.strptime(datafile, "%a %b %d %H:%M:%S %Y")
    storagefile = datetime.datetime.strptime(storagefile, "%a %b %d %H:%M:%S %Y")
    
    return datafile > storagefile
    
def compareJSONs(storageDoc, backupDoc, outputFile, userFriendlyOutputFile):
    '''Compares dictionaries from two json files
    creates 3rd json file with differences'''
    
    backupDict = {}
    with open(backupDoc, 'r', encoding='utf-8') as backupFile:
        backupDict = json.load(backupFile)
    
    storageDict = {}
    with open(storageDoc, 'r', encoding='utf-8') as storageFile:
        storageDict = json.load(storageFile)
    
    ufoF =  open(userFriendlyOutputFile, 'w', encoding='utf-8')
 
    # comparing keys in dicts:
    changedDict = {}
    for key in backupDict:
        if key in storageDict:
            # changed keys (items in Backup that have time in Storage)
            if backupDict[key] != storageDict[key] and isDataFileLaterStorageFile(backupDict[key][2],storageDict[key][2]):
                changedDict[key] = [backupDict[key],storageDict[key]]
                ufoF.write('--Файл в Данных был изменен--\n')
                ufoF.write('В Хранилище: '+str(storageDict[key])+'\n')
                ufoF.write('В Данных: '+str(backupDict[key])+'\n')

        # new keys (keys in Backup that don't exist in Storage)
        if key not in storageDict:
            changedDict[key] = [backupDict[key], []]
            ufoF.write('--Найден новый файл в Данных--\n')
            ufoF.write(str(backupDict[key])+'\n')
            
    # removed keys (keys in Storage that don't exist in Backup )
    for key in storageDict:
        if key not in backupDict:
            changedDict[key] = [[],storageDict[key]] 
            ufoF.write('--Файл, удаленный из Данных--\n')
            ufoF.write(str(storageDict[key])+'\n')
    
    ufoF.close()
                
    with open(outputFile, 'w', encoding='utf-8') as oF:
        json.dump(changedDict, oF, sort_keys=True)

def copyFilesToStorage(storagePath, dataPath, listOfFiles):
    storagePath = storagePath.replace('/', '\\')
    dataPath = dataPath.replace('/', '\\')
    try:
        os.makedirs(os.path.dirname(storagePath+listOfFiles[1]+'\\'+listOfFiles[0]), exist_ok=True)
        shutil.copy(dataPath+listOfFiles[1]+'\\'+listOfFiles[0], storagePath+listOfFiles[1]+'\\'+listOfFiles[0])
    except:
        print('file ', dataPath+listOfFiles[1]+'\\'+listOfFiles[0], 'wasn\'t copied')

def removeFilesFromStorage(storagePath, dataPath, listOfFiles):
    storagePath = storagePath.replace('/', '\\')
    try:
        os.remove(storagePath+listOfFiles[1]+'\\'+listOfFiles[0])
    except:
        print('file ', storagePath+listOfFiles[1]+'\\'+listOfFiles[0], 'wasn\'t deleted')
        
def replaceFilesInStorage(storagePath, dataPath, listOfFiles):
    storagePath = storagePath.replace('/', '\\')
    dataPath = dataPath.replace('/', '\\')
    try:
        shutil.copy(dataPath+listOfFiles[1]+'\\'+listOfFiles[0], storagePath+listOfFiles[1]+'\\'+listOfFiles[0])
    except:
        print('file ', storagePath+listOfFiles[1]+'\\'+listOfFiles[0], 'wasn\'t replaced')


#def openfile(filepath):
#    '''Opens a file'''
#    
#    os.startfile(filepath)
        
#def getHash(filepath):
#    # BUF_SIZE is totally arbitrary, change for your app!
#    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
#
#
#    sha1 = hashlib.sha1()
#
#    with open(filepath, 'rb') as f:
#        while True:
#            data = f.read(BUF_SIZE)
#            if not data:
#                break
#            sha1.update(data)
#    return sha1.hexdigest()