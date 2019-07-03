import cv2
import os
import time
import multiprocessing
import datetime
import tkinter
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import *

"""
this file allows users to select one or more videos at a time
the selected videos will be resized into size (480,480)  
the user can selected the format they want the resized videos to be saved as
as well as the folder they want the resized videos to be saved into
for each selected video, all the frames will be captured and resized and saved
both the resized frames and videos will be saved in a folder named as "vid_instance + v"
four demo videos of different format are put in the same folder of the .py files
"""
# waiting time between processes
global M
M = 1
# process number
global P
P = 8

def dirCapture(parameter, path):
    """
    this function create folder for the captured frames and videos
    :param parameter: is the number of the video which will be used as the created folder name
    :param path:is the directory will the folder will be create under
    :return: this function will return the created folder path (cpath) and N is the video number
    """
    # N should be argument of instances NO.
    N = parameter
    # set path for the captured frames
    cpath = path + '%d' % N + '/'
    # create directory if not exist
    while (os.path.exists(cpath)):
        # print('instance N%d' % N + ' exists')
        N = N + 1
        cpath = path + '%d' % N + '/'

        dir = os.path.dirname(cpath)
        # print('create folder'+cpath)
    os.makedirs(cpath)
    return N, cpath

def printInfo(totaltime, vid, cpath):
    """
    this function save resizer performence info to .txt file
    :param totaltime: is the total time the program spend on finish the resizing
    :param vid: is the video tthat all the info about
    :param cpath: is the folder where all the info.txt is saved
    :return: a information string is returned
    """
    infotxt = open(cpath + 'Resize Info' + '.txt', 'a')
    info = str('executeTime: %f' % totaltime + '\n')
    converageRate = totaltime / (vid.get(7))
    info += str('average converage rate is: %f' % converageRate + 'f/s' + '\n')
    frameNum = vid.get(7)
    info += str('frame number is %d' % frameNum + '\n')
    fps = vid.get(5)
    info += str('frame rate is %f' % fps + '\n')

    infotxt.write(info)
    infotxt.close()

    # print(info)
    vid.release()
    return info

def resizeVideo(n, format, vpath, cpath):
    """
    this function resize the recived video to size(480,480) and captured resized frames during the process
    :param n: the number of the video (if more than one videos are resized, used for creating folder name automatically)
    :param format: the format the user want the video to be resized and saved as into
    :param vpath: refer to the path of video need to be resized
    :param cpath: refer to the path where to save the captured frames as well as the resized video
    :return: the total execute time of the resizing is returned
    """
    start_time = time.time()
    t = time.process_time()
    vidcap = cv2.VideoCapture(vpath)
    success, image = vidcap.read()
    cv2.namedWindow('image')
    cv2.imshow('image', image)
    cv2.waitKey(1)
    count = 0

    CODE = 'XVID'
    # default save to avi

    CODE1 = 'XVID'
    format1 = '.avi'
    CODE2 = 'WMV1'  # OR WMV2
    format2 = '.wmv'
    CODE3 = 'FLV1'
    format3 = '.flv'
    CODE4 = 'MPEG'
    format4 = '.mp4'

    if (format == format1):
        CODE = CODE1
    if (format == format2):
        CODE = CODE2
    if (format == format3):
        CODE = CODE3
    if (format == format4):
        CODE = CODE4
    if format == '':
        CODE = CODE1
        format = '.avi'
        print("default save the resized video to .avi")

    # fourcc used for saving videos
    fourcc = cv2.VideoWriter_fourcc(*CODE)
    # video saved to the same path as the capatured frame
    out = cv2.VideoWriter((str(cpath) + 'ResizedVideo%d' % n + format), fourcc, vidcap.get(5), (480, 480))
    infotxt = open(cpath + 'Resize Info' + '.txt', 'w')
    infotxt.write(vpath + '\n')
    print("Resizing...")

    while success:
        if success:
            resize = cv2.resize(image, (480, 480), interpolation=cv2.INTER_LINEAR)
            # frame name save as Frame%5d.jpg
            cv2.imwrite((str(cpath) + "Frame%05d.jpg" % count), resize)

            # write resized frame to saved video
            out.write(resize)

            cv2.imshow('image', resize)

            # print converage rate of the frame
            end_time = time.time()
            executeTime = end_time - start_time
            converageRate = executeTime / (count + 1)
            infotxt.write('converage rate is: %f' % converageRate + 'f/s' + '\n')

            cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # check whether capture finished

        success, image = vidcap.read()
        count += 1
    infotxt.write('Resizing Completed')
    print("Resizing Completed")

    end_time = time.time()
    executeTime = end_time - start_time
    infotxt.close()
    printInfo.printInfo(executeTime, vidcap, cpath)

    cv2.destroyAllWindows()
    return executeTime

def resizeButton(format,vpath,cpath):
    """
    this function is action for the resize buttons to use, mainly call the resizeVideo methods
    :param format:the format the user want the video to be resized and saved as into
    :param vpath: refer to the path of video need to be resized
    :param cpath: refer to the path where to save the captured frames as well as the resized video
    :return: no return value
    """
    if os.path.exists(cpath):
        cPath=cpath+'/vid-instance'
    if os.path.exists(vpath):
        vPath=vpath
        N, cPath = dirCapture(1, cPath)
        resizeVideo(N, format, vPath, cPath)

def multicore(format, filenames, cpath):
    """
    this function manage a multiprocessing resize through keeping all the process in the pool
    :param format: the format the user want the video to be resized and saved as into
    :param filenames: a list contains all the videos to be resized
    :param cpath: the directory where all the folders (to save the resized videos and frames)are created
    :return: the total execute time used is returned
    """
    start = time.time()
    po = multiprocessing.Pool(P)
    file = str(filenames).split(',')
    for file in filenames:
        print(file)
        po.apply_async(func=resizeButton, args=(format, file, cpath))
        time.sleep(M)
    print("Done")
    po.close()
    po.join()
    end = time.time()
    total = end - start
    return total

class Resizer(ttk.Frame):
    """
    Resizer is the GUI class in this project
    """
    # XVID MJPG FLV WMV1
    formatTypes = (".avi", ".mp4", ".flv", ".wmv")

    def __init__(self, parent, *args, **kwargs):
        """
        create the window
        """
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui()

    def getCapturePath(self):
        """
        this function is called when the saveButton is clicked
        :return: a directory where the folder are created under is returned
        """
        global cpath
        cpath = askdirectory()

    def getVideosPath(self):
        """
        this function is called when the openButton is clicked
        :return: a list contains all the selected videos path is returned
        """
        videoTypes = [
            ('MP4 files', '*.mp4'),
            ('3GP files', '*.3gp'),
            ('WMV files', '*.wmv'),
            ('FLV files', '*.flv'),
            ('AVI files', '*.avi'),
        ]
        global filenames
        filenames = askopenfilenames(title="Select video files", multiple=True, )

    def startResizing(self):
        """
        this function is called when startButton is called
        and will use resizeButton() function to resize videos sequentially
        :return: no return value
        """
        # total running times
        global totaltime
        start = time.time()
        try:
            str(cpath)
            try:
                file = str(filenames).split(',')[0].strip("('")
                if os.path.exists(file):
                    print(file)
                    try:
                        resizeButton(Format, file, cpath)
                        end = time.time()
                        totaltime = end - start
                        self.resultLabel['text'] = self.Results()
                    except NameError:
                        messagebox.showerror('ERROR', 'No Format selected')
            except NameError:
                messagebox.showerror('ERROR', 'No video selected')
        except NameError:
            messagebox.showerror('ERROR', 'No saving folder selected')

    def startMultiResizing(self):
        """
        this function is called when multiStartButton is called
        and will use multicore() function to resize videos in parallel
        :return: no return value
        """
        global totaltime
        try:
            str(cpath)
            try:
                str(filenames)
                try:
                    print(filenames)
                    totaltime = multicore(Format, filenames, cpath)
                    self.resultLabel['text'] = self.Results()
                except NameError:
                    messagebox.showerror('ERROR', 'no format selected')
            except NameError:
                messagebox.showerror('ERROR', 'No saving folder selected')
        except NameError:
            messagebox.showerror('ERROR', 'No video selected')

    def Results(self):
        """
        this function will create information string used to display in the resultLabel
        :return: the information string will be returned
        """
        try:
            numOfFiles = 0
            file = str(filenames).split(',')
            for file in filenames:
                if os.path.exists(file):
                    numOfFiles += 1
                    print('%d' % numOfFiles + ' videos resized!')
            info = 'totaltime: ' + str(datetime.timedelta(seconds=totaltime))
            print(info)
        except NameError:
            info = ''
            print('no totaltime passed')
        return info

    def init_gui(self):
        """
        this function build the GUI
        :return: no return value
        """
        self.root.title('Video Resizer')
        self.root.option_add('*tearOff', 'FALSE')
        self.grid(column=0, row=0, sticky='nsew')

        # Buttons getvideos, save videos, start resize
        self.openButton = ttk.Button(self, width=8, text="Browse", command=self.getVideosPath)
        self.openButton.grid(column=1, row=2)
        self.saveButton = ttk.Button(self, width=8, text="Browse", command=self.getCapturePath)
        self.saveButton.grid(column=3, row=2)
        self.startButton = ttk.Button(self, text='Start to Resize', command=self.startResizing)
        self.startButton.grid(column=0, row=5)
        self.multiStartButton = ttk.Button(self, text='Start to multi Resize', command=self.startMultiResizing)
        self.multiStartButton.grid(column=2, row=5)

        # listbox to choose what video type to save
        # add a label for the combobox
        ttk.Label(self, text="Select Video Type to Save").grid(column=0, row=4)

        def clickMe():
            """
            button clicked to select video type
            called when action is clicked
            :return:
            """
            global Format
            Format = typeToChoose.get()
            print(Format)
            action.configure(text='selected ' + Format)  # show the selected item after clicked
            action.configure(state='disabled')  # button disabled after clicked

        # Button
        action = ttk.Button(self, text="Select ", command=clickMe)
        action.grid(column=2, row=4)

        # Combobox
        typeToChoose = StringVar()
        # value in combobox is formatType
        numberChosen = ttk.Combobox(self, width=12, textvariable=typeToChoose, values=self.formatTypes)
        numberChosen.grid(column=1, row=4)
        numberChosen.current(0)

        # Frame show info related to the resizing process
        self.resultFrame = ttk.LabelFrame(self, text='Result', height=100)
        self.resultFrame.grid(column=0, row=6, columnspan=4, sticky='nesw')
        self.resultLabel = ttk.Label(self.resultFrame, text='')
        self.resultLabel.grid(column=0, row=0)

        # Labels that remain constant throughout execution.
        ttk.Label(self, text='Video Resizer').grid(column=0, row=0, columnspan=4)
        ttk.Label(self, text='Select videos').grid(column=0, row=2, sticky='w')
        ttk.Label(self, text='Saving folder').grid(column=2, row=2, sticky='w')
        ttk.Separator(self, orient='horizontal').grid(column=0, row=1, columnspan=4, sticky='ew')

        # configure for the window grid
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)


if __name__ == '__main__':
    """
    main method
    """
    root = tkinter.Tk()
    Resizer(root)
    root.mainloop()