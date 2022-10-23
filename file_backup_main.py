from tkinter import END, LEFT, TOP, BOTTOM, Entry, \
        Label, LabelFrame, Tk, RIGHT, BOTH, RAISED, \
        filedialog, StringVar, Text
import tkinter
from tkinter.ttk import Frame, Button, Style
import models


class Browse_button(Frame):
    '''Class for browse buttons'''
    
    def __init__(self, frame, text, entry):
        super().__init__()
        self.frame = frame
        self.text = text
        self.initBrowseButton(self.frame, self.text)
        self.path = 'Введите путь'
        self.entry = entry

    def initBrowseButton(self, frame, text):
        '''Initialize a button and place it to the window'''
        
        browseButton = Button(
            self.frame, text=self.text, command=self.browseButton)
        browseButton.pack(side=RIGHT, padx=5, pady=5)

    def browseButton(self):
        '''Defines command for the button:
        opens file dialog and saves the path
        to its property'''
        
        self.entry.setText('')
        self.path = filedialog.askdirectory()
        self.entry.setText(self.path)

class Compare_button(Frame):
    '''Class for compare button'''
    
    def __init__(self, frame, text, entryStorage, entryBackup):
        super().__init__()
        self.frame = frame
        self.text = text
        self.initCompareButton(self.frame, self.text)
        self.path = 'Enter a path'
        self.entryStorage = entryStorage
        self.entryBackup = entryBackup

    def initCompareButton(self, frame, text):
        '''Initializes a button and place it to the window'''
        
        compareButton = Button(self.frame, text=self.text,
                               command=self.compare, width=400)
        compareButton.pack(side=TOP, padx=5, pady=5)

    def compare(self):
        '''Export list of files in Data folder,
        export list of files in Storage folder,
        export changed files to a file'''
        
        models.writeListOfFiles(self.entryStorage.text, r'listStorage.json')
        models.writeListOfFiles(self.entryBackup.text, r'listBackup.json')
        models.compareJSONs(r'listStorage.json', r'listBackup.json',
                            r'Delta.json', r'Changes.txt')
        
class OpenFile_button(Frame):
    '''Class for button which put list of changed files to the window'''
    
    def __init__(self, frame, text, changedFilesText, 
                newFilesText, removedFilesText):
        super().__init__()
        self.frame = frame
        self.text = text
        self.changedFilesText = changedFilesText
        self.newFilesText = newFilesText
        self.removedFilesText = removedFilesText
        self.initOpenFileButton(self.frame, self.text)

    def initOpenFileButton(self, frame, text):
        '''Initialize the button and place it to the window'''
        
        openFileButton = Button(self.frame, text=self.text,
                               command=self.openfile, width=400)
        openFileButton.pack(side=BOTTOM, padx=5, pady=5)
        
    def openfile(self):
        '''Import lists of changed files to Text fields from
        Delta.json file'''
        
        # Clears Text fields
        self.changedFilesText.delete('1.0',END)
        self.newFilesText.delete('1.0',END)
        self.removedFilesText.delete('1.0',END)
        
        # Fills in Text fileds with content of Delta.json file
        changed, new, removed = models.getDeltaFiles(r'Delta.json')
        for item in changed:
            self.changedFilesText.insert(END, str(item)+'\n')
        for item in new:
            self.newFilesText.insert(END, str(item)+'\n')
        for item in removed:
            self.removedFilesText.insert(END, str(item)+'\n')
            
        # Number of files in each Text field
        self.changedFilesText.insert(END, 'Всего: '+str(len(changed))+' файлов\n')
        self.newFilesText.insert(END, 'Всего: '+str(len(new))+' файлов\n')
        self.removedFilesText.insert(END, 'Всего: '+str(len(removed))+' файлов\n')


class Action_Button(Frame):
    '''Class for Button objects for Removing, 
    Changing and Adding files to the Storage'''
    
    def __init__(self, frame, text, entryStorage, entryBackup, 
                changedFilesText, newFilesText, removedFilesText):
        super().__init__()
        self.frame = frame
        self.text = text
        self.initActionButton(self.frame, self.text)
        self.entryStorage = entryStorage
        self.entryBackup = entryBackup
        self.changedFilesText = changedFilesText
        self.newFilesText = newFilesText
        self.removedFilesText = removedFilesText

    def initActionButton(self, frame, text):
        '''Initializes the button and place it to the window'''
        
        actionButton = Button(self.frame, text=self.text,
                               command=self.action, width=400)
        actionButton.pack(side=TOP, padx=5, pady=5)   
        
    def action(self):
        '''Calls function to actually remove, add or replace the files,
        depending on pressed Button name, creates Log of processed actions
        and open it on completion'''
        
        # Import changed files from Delta.json file
        changed, new, removed = models.getDeltaFiles(r'Delta.json')
        
        # Log files
        logFilePathNew = r'ИзмененияДобавленные.txt'
        logFilePathRem = r'ИзмененияУдаленные.txt'
        logFilePathRepl = r'ИзмененияЗамененные.txt'
        
        # For "Заменить в Хранилище" Button it calls function
        # to replace the files in the Storage with latest ones
        # from the Data
        if self.text == "Заменить в Хранилище":
            dur = models.replaceFilesInStorage(self.entryStorage.text, 
                   self.entryBackup.text, changed, logFilePathRepl)
            self.changedFilesText.delete('1.0', END)
            self.changedFilesText.insert('1.0',
            "Готово! Список замененных файлов находится в файле ИзмененияЗамененные.txt")
            self.changedFilesText.insert('1.0', f"Время выполнения: %.3f секунд(ы)\n" % dur)
 
            # Opens log file in default OS text editor       
            models.openfile(logFilePathRepl)
               
        # For "Добавить в Хранилище" Button it calls function
        # to add the files to the Storage with new ones
        # from the Data
        elif self.text == "Добавить в Хранилище":
            dur = models.copyFilesToStorage(self.entryStorage.text, 
                self.entryBackup.text, new, logFilePathNew)
            self.newFilesText.delete('1.0', END)
            self.newFilesText.insert('1.0',
            "Готово! Список добавленных файлов находится в файле ИзмененияДобавленные.txt")
            self.newFilesText.insert('1.0', f"Время выполнения: %.3f секунд(ы)\n" % dur)

            # Opens log file in default OS text editor       
            models.openfile(logFilePathNew)
               
        # For "Удалить из Хранилища" Button it calls function
        # to remove the files from the Storage which absent
        # in the Data
        elif self.text == "Удалить из Хранилища":
            dur = models.removeFilesFromStorage(self.entryStorage.text, 
                self.entryBackup.text, removed, logFilePathRem)
            self.removedFilesText.delete('1.0', END)
            self.removedFilesText.insert('1.0',
            "Готово! Список удаленных файлов находится в файле ИзмененияУдаленные.txt")  
            self.removedFilesText.insert('1.0', f"Время выполнения: %.3f секунд(ы)\n" % dur)
        
            # Opens log file in default OS text editor       
            models.openfile(logFilePathRem)
            
class pathEntry(Entry):
    '''Class for entry objects to store 
    Pathes for Storage and Data folders'''
    
    def __init__(self, frame):
        super().__init__()
        self.text = 'Введите путь'
        self.frame = frame
        self.initPathEntry(self.frame)

    def initPathEntry(self, frame):
        '''Create instance of Entry class
        and place it on the window'''
        
        self.pathEntry = Entry(frame, width=80)
        self.pathEntry.pack(side=LEFT)

    def setText(self, text):
        '''Set text for path Entry'''
        
        self.pathEntry.delete(0, END)
        self.text = text
        self.pathEntry.insert(0, text)

class Backup(Frame):
    '''Main class, creates GUI objects'''
    
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        self.master.title("Резервное копирование")
        self.style = Style()
        self.style.theme_use("default")

        self.pathVar = StringVar()
        
        # Places the main frame
        self.pack(fill=BOTH, expand=True)
        
        # Frames
        storageframe = Frame(self)
        storageframe.pack(side=TOP, expand=True, fill=BOTH)

        dataframe = Frame(self)
        dataframe.pack(side=TOP, expand=True, fill=BOTH)

        compareButtonframe = Frame(self)
        compareButtonframe.pack(side=TOP, expand=True, fill=BOTH)        
              
        # LabelFrames  
        changedFilesOutputLabel = LabelFrame(
            self, width=400, height=150, text='Измененные файлы')
        changedFilesOutputLabel.pack(padx=10, pady=10)
                
        newFilesOutputLabel = LabelFrame(
            self, width=400, height=150, text='Новые файлы')
        newFilesOutputLabel.pack(padx=10, pady=10)
                    
        removedFilesOutputLabel = LabelFrame(
            self, width=400, height=150, text='Удаленные файлы')
        removedFilesOutputLabel.pack(padx=10, pady=10)
        
        # Text fields
        changedFilesText = Text(changedFilesOutputLabel, width=400, height=5)
        changedFilesText.pack(side=TOP,padx=5, pady=5)
        
        newFilesText = Text(newFilesOutputLabel, width=400, height=5)
        newFilesText.pack(side=TOP,padx=5, pady=5)
        
        removedFilesText = Text(removedFilesOutputLabel, width=400, height=5)
        removedFilesText.pack(side=TOP,padx=5, pady=5)
        
        # Entries
        storagePathEntry = pathEntry(storageframe)
        dataPathEntry = pathEntry(dataframe)
        
        # Buttons
        storageBrowseButton = Browse_button(
            storageframe, "Хранилище", storagePathEntry)
        backupBrowseButton = Browse_button(
            dataframe, "Данные", dataPathEntry)

        compareButton = Compare_button(
            compareButtonframe, "Сравнить файлы", 
            storagePathEntry, dataPathEntry)
        
        openFileButton = OpenFile_button(
            compareButtonframe, "Открыть Список Изменений", 
            changedFilesText, newFilesText, removedFilesText)
        
        replaceButton = Action_Button(
            changedFilesOutputLabel, "Заменить в Хранилище", 
            storagePathEntry, dataPathEntry, changedFilesText, 
            newFilesText, removedFilesText)

        addButton = Action_Button(
            newFilesOutputLabel, "Добавить в Хранилище", 
            storagePathEntry, dataPathEntry, changedFilesText, 
            newFilesText, removedFilesText)
        
        removeButton = Action_Button(
            removedFilesOutputLabel, "Удалить из Хранилища", 
            storagePathEntry, dataPathEntry, changedFilesText, 
            newFilesText, removedFilesText)
        
        closeButton = Button(self, text="Закрыть", command=self.root.destroy)
        closeButton.pack(side=BOTTOM, padx=5, pady=5)

def main():

    root = Tk()
    root.geometry("600x700")
    Backup(root)
    root.mainloop()


if __name__ == '__main__':
    main()
