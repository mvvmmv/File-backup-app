import os, sys, time, hashlib, json, datetime, shutil
from this import d
from pathlib import Path


def getDeltaFiles(filepath):
    '''Get data from json file and return 3 lists
    for changed, new and removed files'''
    
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
            dict[filepath[len(root):]] = [name, path[len(root):], 
                            str(time.ctime(os.path.getmtime(filepath)))]
    with open(doc, 'w', encoding="utf-8") as f:
        json.dump(dict, f, sort_keys=True)

def isDataFileLaterStorageFile(datafile, storagefile):
    '''Compare two dates in string format.'''
    
    datafile = datetime.datetime.strptime(datafile, "%a %b %d %H:%M:%S %Y")
    storagefile = datetime.datetime.strptime(storagefile, "%a %b %d %H:%M:%S %Y")
    
    return datafile > storagefile
    
def compareJSONs(storageDoc, backupDoc, outputFile, userFriendlyOutputFile):
    '''Compares dictionaries from two json files
    creates 3rd json file with the differences'''
    
    # Open jsons with Data and Storage lists of files
    backupDict = {}
    with open(backupDoc, 'r', encoding='utf-8') as backupFile:
        backupDict = json.load(backupFile)
    
    storageDict = {}
    with open(storageDoc, 'r', encoding='utf-8') as storageFile:
        storageDict = json.load(storageFile)
    
    # Open file to export user friendly output
    ufoF =  open(userFriendlyOutputFile, 'w', encoding='utf-8')
 
    # comparing keys in dicts
    # adding changes to other dictionary
    # writing changes to user friendly output file
    changedDict = {}
    
    for key in backupDict:
        if key in storageDict:
            # changed keys (items in Backup that have time in Storage)
            if backupDict[key] != storageDict[key] and \
            isDataFileLaterStorageFile(backupDict[key][2],storageDict[key][2]):
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
    
    # Export changes dictionary to json file            
    with open(outputFile, 'w', encoding='utf-8') as oF:
        json.dump(changedDict, oF, sort_keys=True)

def duration_decorator(func):
    '''Decorator to count duration of function processing'''
    
    def wrapper(*args):
        # Timer starts
        timer = time.time()
        func(*args)
        duration = time.time() - timer
        return duration
    return wrapper

@duration_decorator    
def copyFilesToStorage(storagePath, dataPath, listOfFiles, logFilePathNew):
    '''Copies changes to Storage and writes Logfile'''
    
    logfile = open(logFilePathNew, 'w', encoding='utf-8')
        
    storagePath = storagePath.replace('/', '\\')
    dataPath = dataPath.replace('/', '\\')
    
    for file in listOfFiles:
        absoluteStoragePath = storagePath+file[1]+'\\'+file[0]
        absoluteDataPath = dataPath+file[1]+'\\'+file[0]

        try:
            os.makedirs(os.path.dirname(absoluteStoragePath), exist_ok=True)
            shutil.copy(absoluteDataPath, absoluteStoragePath)
            logfile.write('Success: file '+absoluteDataPath+' copied\n')
        except:
            logfile.write('Error: file '+absoluteDataPath+' wasn\'t copied\n')
    
    logfile.close()

@duration_decorator    
def removeFilesFromStorage(storagePath, dataPath, listOfFiles, logFilePathRem):
    '''Removes changes from Storage and writes Logfile'''

    logfile = open(logFilePathRem, 'w', encoding='utf-8')

    storagePath = storagePath.replace('/', '\\')
    
    for file in listOfFiles:
        absoluteStoragePath = storagePath+file[1]+'\\'+file[0]
        try:
            os.remove(absoluteStoragePath)
            logfile.write('Success: file '+absoluteStoragePath+' removed\n')
        except:
            logfile.write('Error: file '+absoluteStoragePath+' wasn\'t removed\n')
    
    logfile.close()   

@duration_decorator       
def replaceFilesInStorage(storagePath, dataPath, listOfFiles, logFilePathRepl):
    '''Replaces files in Storage if they are newer in Data
    and writes Logfile'''

    logfile = open(logFilePathRepl, 'w', encoding='utf-8')

    storagePath = storagePath.replace('/', '\\')
    dataPath = dataPath.replace('/', '\\')
    
    for file in listOfFiles:
        absoluteDataPath = dataPath+file[1]+'\\'+file[0]
        absoluteStoragePath = storagePath+file[1]+'\\'+file[0]
        try:
            shutil.copy(absoluteDataPath, absoluteStoragePath)
            logfile.write('Success: file '+absoluteStoragePath+ 
                        ' replaced with the newest one\n')
        except:
            logfile.write('Error: file '+absoluteStoragePath+ 
                        ' wasn\'t replaced with the newest one\n')
    
    logfile.close()
    
def openfile(filepath):
    '''Opens a file if exists'''
    
    if Path(filepath).exists():
        os.startfile(filepath)