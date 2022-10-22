from tkinter import END, LEFT, TOP, BOTTOM, Entry, Label, LabelFrame, Tk, RIGHT, BOTH, RAISED, filedialog, StringVar, Text
import tkinter
from tkinter.ttk import Frame, Button, Style
import models


class Browse_button(Frame):
    def __init__(self, frame, text, entry):
        super().__init__()
        self.frame = frame
        self.text = text
        self.initBrowseButton(self.frame, self.text)
        self.path = 'Enter a path'
        self.entry = entry

    def initBrowseButton(self, frame, text):
        storageBrowseButton = Button(
            self.frame, text=self.text, command=self.browseButton)
        storageBrowseButton.pack(side=RIGHT, padx=5, pady=5)

    def browseButton(self):
        self.entry.setText('')
        self.path = filedialog.askdirectory()
        self.entry.setText(self.path)

class Compare_button(Frame):
    def __init__(self, frame, text, entryStorage, entryBackup):
        super().__init__()
        self.frame = frame
        self.text = text
        self.initCompareButton(self.frame, self.text)
        self.path = 'Enter a path'
        self.entryStorage = entryStorage
        self.entryBackup = entryBackup

    def initCompareButton(self, frame, text):
        compareButton = Button(self.frame, text=self.text,
                               command=self.compare, width=400)
        compareButton.pack(side=TOP, padx=5, pady=5)

    def compare(self):
        models.writeListOfFiles(self.entryStorage.text, r'C:\Users\im\Desktop\listStorage.json')
        models.writeListOfFiles(self.entryBackup.text, r'C:\Users\im\Desktop\listBackup.json')
        models.compareJSONs(r'C:\Users\im\Desktop\listStorage.json', r'C:\Users\im\Desktop\listBackup.json', r'C:\Users\im\Desktop\Delta.json', r'C:\Users\im\Desktop\Changes.txt')
        
class OpenFile_button(Frame):
    def __init__(self, frame, text, changedFilesText, newFilesText, removedFilesText):
        super().__init__()
        self.frame = frame
        self.text = text
        self.changedFilesText = changedFilesText
        self.newFilesText = newFilesText
        self.removedFilesText = removedFilesText
        self.initOpenFileButton(self.frame, self.text)

    def initOpenFileButton(self, frame, text):
        OpenFileButton = Button(self.frame, text=self.text,
                               command=self.openfile, width=400)
        OpenFileButton.pack(side=BOTTOM, padx=5, pady=5)
        
    def openfile(self):
            #models.openfile(r'C:\Users\im\Desktop\Changes.txt')
            self.changedFilesText.delete('1.0',END)
            self.newFilesText.delete('1.0',END)
            self.removedFilesText.delete('1.0',END)

            # fill in Output Entries with content of Delta.json file
            changed, new, removed = models.getDeltaFiles(r'C:\Users\im\Desktop\Delta.json')
            for item in changed:
                self.changedFilesText.insert(END, str(item)+'\n')

            for item in new:
                self.newFilesText.insert(END, str(item)+'\n')

            for item in removed:
                self.removedFilesText.insert(END, str(item)+'\n')

class Action_Button(Frame):
    def __init__(self, frame, text, entryStorage, entryBackup, changedFilesText, newFilesText, removedFilesText):
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
        actionButton = Button(self.frame, text=self.text,
                               command=self.action, width=400)
        actionButton.pack(side=TOP, padx=5, pady=5)   
        
    def action(self):
        changed, new, removed = models.getDeltaFiles(r'C:\Users\im\Desktop\Delta.json')
        logfile = r'C:\Users\im\Desktop\Log.txt'
        if self.text == "Заменить в Хранилище":
            for item in changed:
                models.replaceFilesInStorage(self.entryStorage.text, self.entryBackup.text, item)
                self.changedFilesText.delete('1.0', END)
                self.changedFilesText.insert('1.0',"Готово! Список замененных файлов находится в файле Изменения.txt")
        elif self.text == "Добавить в Хранилище":
            for item in new:
                models.copyFilesToStorage(self.entryStorage.text, self.entryBackup.text, item)
                self.newFilesText.delete('1.0', END)
                self.newFilesText.insert('1.0',"Готово! Список добавленных файлов находится в файле Изменения.txt")
        elif self.text == "Удалить из Хранилища":
            for item in removed:
                models.removeFilesFromStorage(self.entryStorage.text, self.entryBackup.text, item)
                self.removedFilesText.delete('1.0', END)
                self.removedFilesText.insert('1.0',"Готово! Список удаленных файлов находится в файле Изменения.txt")         
            
class pathEntry(Entry):
    def __init__(self, frame):
        super().__init__()
        self.text = 'Введите путь'
        self.frame = frame
        self.initPathEntry(self.frame)

    def initPathEntry(self, frame):
        self.pathEntry = Entry(frame, width=50)
        self.pathEntry.pack(side=LEFT)

    def setText(self, text):
        self.pathEntry.delete(0,END)
        self.text = text
        self.pathEntry.insert(0, text)


class Backup(Frame):

    def __init__(self, root):
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        self.master.title("Резервное копирование")
        self.style = Style()
        self.style.theme_use("default")

        self.pathVar = StringVar()

        mainFrame = Frame(self, relief=RAISED, borderwidth=1)
        mainFrame.pack(fill=BOTH)

        storageframe = Frame(mainFrame)
        storageframe.pack(side=TOP, expand=True, fill=BOTH)

        backupframe = Frame(mainFrame)
        backupframe.pack(side=TOP, expand=True, fill=BOTH)

        compareButtonframe = Frame(mainFrame)
        compareButtonframe.pack(side=TOP, expand=True, fill=BOTH)

        self.pack(fill=BOTH, expand=True)
        
        storagePathEntry = pathEntry(storageframe)
        backupPathEntry = pathEntry(backupframe)
        
        changedFilesOutputframe = Frame(self)
        changedFilesOutputframe.pack(side=TOP, expand=True, fill=BOTH)
        
        changedFilesOutputLabel = LabelFrame(
            changedFilesOutputframe, width=400, height=150, text='Измененные файлы')
        changedFilesOutputLabel.pack(padx=10, pady=10)

        changedFilesText = Text(changedFilesOutputLabel, width=400, height=5)
        changedFilesText.pack(side=TOP,padx=5, pady=5)
        
        
        
        newFilesOutputFrame = Frame(self)
        newFilesOutputFrame.pack(side=TOP, expand=True, fill=BOTH)
        
        newFilesOutputLabel = LabelFrame(
            newFilesOutputFrame, width=400, height=150, text='Новые файлы')
        newFilesOutputLabel.pack(padx=10, pady=10)

        newFilesText = Text(newFilesOutputLabel, width=400, height=5)
        newFilesText.pack(side=TOP,padx=5, pady=5)
            
        removedFilesOutputFrame = Frame(self)
        removedFilesOutputFrame.pack(side=TOP, expand=True, fill=BOTH)
        
        removedFilesOutputLabel = LabelFrame(
            removedFilesOutputFrame, width=400, height=150, text='Удаленные файлы')
        removedFilesOutputLabel.pack(padx=10, pady=10)

        removedFilesText = Text(removedFilesOutputLabel, width=400, height=5)
        removedFilesText.pack(side=TOP,padx=5, pady=5)
        
        removeButton = Action_Button(
            removedFilesOutputLabel, "Удалить из Хранилища", storagePathEntry, backupPathEntry,
            changedFilesText, newFilesText, removedFilesText)

        replaceButton = Action_Button(
            changedFilesOutputLabel, "Заменить в Хранилище", storagePathEntry, backupPathEntry,
            changedFilesText, newFilesText, removedFilesText)

        addButton = Action_Button(
            newFilesOutputLabel, "Добавить в Хранилище", storagePathEntry, backupPathEntry,
            changedFilesText, newFilesText, removedFilesText)

        closeButton = Button(self, text="Закрыть", command=self.root.destroy)
        closeButton.pack(side=BOTTOM, padx=5, pady=5)

        storageBrowseButton = Browse_button(
            storageframe, "Хранилище", storagePathEntry)
        backupBrowseButton = Browse_button(
            backupframe, "Данные", backupPathEntry)

        compareButton = Compare_button(
            compareButtonframe, "Сравнить файлы", storagePathEntry, backupPathEntry)
        
        openFileButton = OpenFile_button(
            compareButtonframe, "Открыть Список Изменений", changedFilesText, newFilesText, removedFilesText)

def main():

    root = Tk()
    root.geometry("600x700")
    Backup(root)
    root.mainloop()


if __name__ == '__main__':
    main()
