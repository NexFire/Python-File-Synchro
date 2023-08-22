import sys,os,getopt
import time
import shutil
import hashlib
import datetime
def report(path,file,action,destinationPath="",):
    actions={0:"Creating",1:"Copying",2:"Removing",3:""}
    if(action==1):
        file.write(actions[action]+" "+path+" to "+destinationPath+"\n")
    elif(action==3):
        file.write(path+"\n")
    else:
        file.write(actions[action]+" "+path+"\n")

def main(argv):
    interval=3600 #the default synchro intrval is 1 hour
    sourceFiles=[]
    replicaFiles=[]
    folderExists=False
    includeViewFiles=False
    opts,args=getopt.getopt(argv,"hs:r:l:i:",["help","sourceFolder","replicaFolder","logFile","synchInterval"])
    for opt,arg in opts:
        if opt in ("-h","--help"):
            print("file-synchro.py -s <sourceFolder> -r <replicaFolder> -l <logFile> -i <synchInterval>")
        elif opt in ("-s","--sourceFile"):
            sourceFolder=arg
        elif opt in ("-r","--replicaFolder"):
            replicaFolder=arg
        elif opt in ("-l","--logFile"):
            logFilePath=arg
        elif opt in ("-i","--synchInterval"):
            interval=int(arg)
    includeViewFiles=False
    savePrevious=False #in next version there would be possibility to save the files just in case but it wasnt in the assignment requirements. But it wouldn't be problem. We could just call this program recursively with different arguments
    savePreviousPath="" #path where we want to have backup
    skip=False
    sourceHash=0
    replicaHash=0
    if(sourceFolder==replicaFolder):
        print("Source folder and Replica Folder are the same. Not synchronizing")
        return
    while(True):
        logFile=open(logFilePath,"a")
        timeNow=datetime.datetime.now()
        report((str(timeNow)+" Synchro").strip(),logFile,3)
        folderExists=os.path.isdir(replicaFolder)
        if(not folderExists):
            try:
                os.mkdir(replicaFolder)
                report(replicaFolder,logFile,0)
            except OSError as error:
                print(error) #optional
                report(error,logFile,3)
        sourceFiles=list(os.walk(sourceFolder))
        for index in range(len(sourceFiles)):
            folderRelPath=os.path.relpath(sourceFiles[index][0],sourceFolder)
            if (len(sourceFiles[index][1])!=0):
                for dirs in sourceFiles[index][1]:
                    path=os.path.join(replicaFolder,folderRelPath,dirs)
                    if(not os.path.isdir(path)):
                        report(path,logFile,0)
                        try:
                            os.mkdir(path)
                        except OSError as error:
                            print(error) #optional
                            report(error,logFile,3)
            if(len(sourceFiles[index][2])>0):
                for file in sourceFiles[index][2]:
                    if(includeViewFiles==False and (file==".DS_Store" or file=="thumbs.db" or file=="desktop.ini") ):
                        skip=True
                    else:
                        skip=False
                    if(not skip):
                        path=os.path.join(replicaFolder,folderRelPath,file)
                        sourcePath=os.path.join(sourceFiles[index][0],file)
                        if(not os.path.isfile(path)):
                            try:
                                report(sourcePath,logFile,1,path)
                                shutil.copy2(sourcePath,path)
                            except PermissionError:
                                print("Permission denied")
                        else:
                            with open(sourcePath,"rb") as sourceFile:
                                sourceHash=hashlib.md5(sourceFile.read())
                            with open(path,"rb") as replicaFile:
                                replicaHash=hashlib.md5(replicaFile.read())
                            if(sourceHash.digest()!=replicaHash.digest()):
                                report(path,logFile,2)
                                try:
                                    os.remove(path)
                                except OSError as error:
                                    print(error) #optional
                                    report(error,logFile,3)
                                try:
                                    report(sourcePath,logFile,1,path)
                                    shutil.copy2(sourcePath,path)
                                except PermissionError:
                                    print("Permission denied")
        replicaFiles=list(os.walk(replicaFolder)) # we need this to cross check the files if some of them have changed or not
        for index in range(len(replicaFiles)-1,-1,-1):
            folderRelPath=os.path.relpath(replicaFiles[index][0],replicaFolder)
            if(len(replicaFiles[index][2])>0):
                for file in replicaFiles[index][2]:
                    path=os.path.join(replicaFiles[index][0],file)
                    sourcePath=os.path.join(sourceFolder,folderRelPath,file)
                    if(not os.path.exists(sourcePath)):
                        report(path,logFile,2)
                        try:
                            os.remove(path)
                        except OSError as error:
                            print(error) #optional
                            report(error,logFile,3)
            if (len(replicaFiles[index][1])!=0):
                for dir in replicaFiles[index][1]:
                    path=os.path.join(replicaFiles[index][0],dir)
                    sourcePath=os.path.join(sourceFolder,folderRelPath,dir)
                    if(not os.path.exists(sourcePath)):
                        report(path,logFile,2)
                        try:
                            os.removedirs(path)
                        except OSError as error:
                            print(error) #optional
                            report(error,logFile,3)

        report("Next Synchro: "+str(datetime.datetime.now()+datetime.timedelta(seconds=interval)),logFile,3)
        print("Next Synchro: "+str(datetime.datetime.now()+datetime.timedelta(seconds=interval))) #can be removed if we want no command line response
        logFile.close()
        time.sleep(interval)

if __name__ == "__main__":
    main(sys.argv[1:])

