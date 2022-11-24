from tkinter import END, LEFT, TOP, BOTTOM, Entry, LabelFrame, RIGHT, BOTH, \
    filedialog, StringVar, Text
import asyncio
import time
from tkinter.ttk import Frame, Button, Style, Progressbar

import functions


# needed to store all instances of all buttons
class ButtonClass():
    '''Parent class for all Buttons'''
    all_buttons = []

    def __init__(self) -> None:
        self.all_buttons.append(self)

    def packButton(self, side):
        '''Packs button'''

        self.btn.pack(side=side, padx=5, pady=5)


class Browse_button(ButtonClass):
    '''Class for browse buttons'''

    def __init__(self, frame, text, entry):
        super().__init__()
        self.frame = frame
        self.text = text
        self.path = ''
        self.entry = entry
        self.btn = Button(self.frame, text=self.text,
                          command=self.browseButton)
        self.packButton(RIGHT)

    def browseButton(self):
        '''Defines command for the button:
        opens file dialog and saves the path
        to its property'''

        self.entry.setText('')
        self.path = filedialog.askdirectory()
        self.entry.setText(self.path)


class Compare_button(ButtonClass):
    '''Class for compare button'''

    def __init__(self, frame, text, entryStorage, entryBackup):
        super().__init__()
        self.frame = frame
        self.text = text
        self.path = 'Enter a path'
        self.entryStorage = entryStorage
        self.entryBackup = entryBackup
        self.btn = Button(self.frame, text=self.text,
                          command=self.compare, width=400)
        self.packButton(TOP)

    def compare(self):
        '''Export list of files in Data folder,
        export list of files in Storage folder,
        export changed files to a file'''

        functions.writeListOfFiles(self.entryStorage.text, r'listStorage.json')
        functions.writeListOfFiles(self.entryBackup.text, r'listBackup.json')
        functions.compareJSONs(r'listStorage.json', r'listBackup.json',
                               r'Delta.json', r'Changes.txt')


class OpenFile_button(ButtonClass):
    '''Class for button which put list of changed files to the window'''

    def __init__(self, frame, text, changedFilesText,
                 newFilesText, removedFilesText):
        super().__init__()
        self.frame = frame
        self.text = text
        self.changedFilesText = changedFilesText
        self.newFilesText = newFilesText
        self.removedFilesText = removedFilesText
        self.btn = Button(self.frame, text=self.text,
                          command=self.openfile, width=400)
        self.packButton(BOTTOM)

    def openfile(self):
        '''Import lists of changed files to Text fields from
        Delta.json file'''

        # Clears Text fields
        self.changedFilesText.delete('1.0', END)
        self.newFilesText.delete('1.0', END)
        self.removedFilesText.delete('1.0', END)

        # Fills in Text fileds with content of Delta.json file
        changed, new, removed = functions.getDeltaFiles(r'Delta.json')
        for item in changed:
            self.changedFilesText.insert(END, str(item)+'\n')
        for item in new:
            self.newFilesText.insert(END, str(item)+'\n')
        for item in removed:
            self.removedFilesText.insert(END, str(item)+'\n')

        # Number of files in each Text field
        self.changedFilesText.insert(
            END, 'Всего: '+str(len(changed))+' файлов\n')
        self.newFilesText.insert(END, 'Всего: '+str(len(new))+' файлов\n')
        self.removedFilesText.insert(
            END, 'Всего: '+str(len(removed))+' файлов\n')


class Action_Button(ButtonClass):
    '''Parent class for Action Button objects'''

    def __init__(self, frame, text, entryStorage, entryBackup):
        super().__init__()
        self.frame = frame
        self.text = text
        self.entryStorage = entryStorage
        self.entryBackup = entryBackup
        self.pressed = False
        self.handled_files = 0
        self.all_files_count = 1

    async def action(self):
        '''Individual for every Action Button'''
        pass

    async def sub_action(self, logFilePath, list_number, text_field):
        '''Handling list of files.
        list_number - number of list in Delta.json file,
        text_field - gui text field for displaying output,
        logFilePath - path to file to write result of handling of each file
        of the list
        '''

        # block all buttons on GUI
        for button in ButtonClass.all_buttons:
            button.btn.configure(state="disabled")

        self.pressed = True
        self.handled_files = 1

        # Import changed/removed/new files from Delta.json file
        # for changed list_number = 0, removed =1, new = 2
        files_to_handle = functions.getDeltaFiles(r'Delta.json')[list_number]
        self.all_files_count = len(files_to_handle)

        # start timer
        time_start = time.perf_counter()

        for file in files_to_handle:
            await functions.replaceFileInStorage(
                self.entryStorage.text, self.entryBackup.text, file, logFilePath)
            text_field.delete('1.0', END)
            text_field.insert('1.0', file)
            self.handled_files += 1

        # stop timer
        time_end = time.perf_counter()
        dur = time_end - time_start

        text_field.delete('1.0', END)
        text_field.insert('1.0',
                          "Готово! Список замененных файлов находится в файле " +
                          logFilePath)
        text_field.insert(
            '1.0', f"{'Время выполнения: %.3f секунд(ы)'}\n" % dur)

        self.pressed = False

        # unblock all buttons on GUI
        for button in ButtonClass.all_buttons:
            button.btn.configure(state="normal")

        # Opens log file in default OS text editor
        functions.openfile(logFilePath)


class ActionButtonChanged(Action_Button):

    def __init__(self, frame, loop, text, entryStorage, entryBackup,
                 changedFilesText):
        super().__init__(frame, text, entryStorage, entryBackup)
        self.changedFilesText = changedFilesText
        self.loop = loop
        self.btn = Button(self.frame, text=self.text, width=400,
                          command=lambda: self.loop.create_task(self.action()))
        self.packButton(TOP)

    async def action(self):
        '''Calls function to actually replace the files'''

        logFilePathRepl = r'ИзмененияЗамененные.txt'
        list_number = 0

        await self.sub_action(logFilePathRepl, list_number,
                              self.changedFilesText)


class ActionButtonNew(Action_Button):

    def __init__(self, frame, loop, text, entryStorage, entryBackup, newFilesText):
        super().__init__(frame, text, entryStorage, entryBackup)
        self.newFilesText = newFilesText
        self.loop = loop
        self.btn = Button(self.frame, text=self.text, width=400,
                          command=lambda: self.loop.create_task(self.action()))
        self.packButton(TOP)

    async def action(self):
        '''Calls function to add the files'''

        logFilePathNew = r'ИзмененияДобавленные.txt'
        list_number = 1

        await self.sub_action(logFilePathNew, list_number, self.newFilesText)


class ActionButtonRemoved(Action_Button):
    def __init__(self, frame, loop, text, entryStorage, entryBackup, removedFilesText):
        super().__init__(frame, text, entryStorage, entryBackup)
        self.removedFilesText = removedFilesText
        self.loop = loop
        self.btn = Button(self.frame, text=self.text, width=400,
                          command=lambda: self.loop.create_task(self.action()))
        self.packButton(TOP)

    async def action(self):
        '''Calls function to actually remove the files'''

        logFilePathRem = r'ИзмененияУдаленные.txt'
        list_number = 2

        await self.sub_action(logFilePathRem, list_number, self.removedFilesText)


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


class BackupGUI(Frame):
    '''Main class, creates GUI objects'''

    def __init__(self, loop):
        super().__init__()
        self.loop = loop
        self.initUI()

    def initUI(self):
        self.master.geometry("600x700")
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
        self.changedFilesText = Text(
            changedFilesOutputLabel, width=400, height=4)
        self.changedFilesText.pack(side=TOP, padx=5, pady=5)

        self.newFilesText = Text(newFilesOutputLabel, width=400, height=4)
        self.newFilesText.pack(side=TOP, padx=5, pady=5)

        self.removedFilesText = Text(
            removedFilesOutputLabel, width=400, height=4)
        self.removedFilesText.pack(side=TOP, padx=5, pady=5)

        # Entries
        storagePathEntry = pathEntry(storageframe)
        dataPathEntry = pathEntry(dataframe)

        # Buttons
        Browse_button(
            storageframe, "Хранилище", storagePathEntry)
        Browse_button(
            dataframe, "Данные", dataPathEntry)

        Compare_button(
            compareButtonframe, "Сравнить файлы",
            storagePathEntry, dataPathEntry)

        OpenFile_button(
            compareButtonframe, "Открыть Список Изменений",
            self.changedFilesText, self.newFilesText, self.removedFilesText)

        self.replaceButton = ActionButtonChanged(
            changedFilesOutputLabel, self.loop, "Заменить в Хранилище",
            storagePathEntry, dataPathEntry, self.changedFilesText)

        self.addButton = ActionButtonNew(
            newFilesOutputLabel, self.loop, "Добавить в Хранилище",
            storagePathEntry, dataPathEntry, self.newFilesText)

        self.removeButton = ActionButtonRemoved(
            removedFilesOutputLabel, self.loop, "Удалить из Хранилища",
            storagePathEntry, dataPathEntry, self.removedFilesText)

        closeButton = Button(self, text="Закрыть", command=self.master.destroy)
        closeButton.pack(side=BOTTOM, padx=5, pady=5)

        self.progressbar = Progressbar(length=600, value=0)
        self.progressbar.pack(padx=10, pady=10)

    async def show(self):
        while True:
            if self.addButton.pressed:
                self.progressbar["value"] = self.addButton.handled_files * \
                    100 // self.addButton.all_files_count
            if self.replaceButton.pressed:
                self.progressbar["value"] = self.replaceButton.handled_files * \
                    100 // self.replaceButton.all_files_count
            if self.removeButton.pressed:
                self.progressbar["value"] = self.removeButton.handled_files * \
                    100 // self.removeButton.all_files_count
            self.master.update()
            await asyncio.sleep(.1)


async def main():

    window = BackupGUI(asyncio.get_event_loop())
    await window.show()

if __name__ == '__main__':
    asyncio.run(main())
