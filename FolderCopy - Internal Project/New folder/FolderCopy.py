import os
import shutil
import datetime
import sys
import pyfastcopy
import itertools
import threading
import time
import subprocess

done = False
errors = []
FileNotFoundList=[]
FileNotFoundCopy={}
total_size = 0

#here is the animation
def animate():
    for c in itertools.cycle(['C', 'Co', 'Cop', 'Copy', 'Copyi', 'Copyin', 'Copying...']):
        if done:
            break
        sys.stdout.write('\rPlease Wait - ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')


def write_log(log_path,log_report):
    """ function will write log report on given path"""
    ctime = datetime.datetime.now()
    with open(log_path, 'a+') as wfile:
        wfile.write("\n"+str(ctime)+" \t "+str(log_report))

def convert_bytes(num):
    """ function will convert bytes to MB.... GB... etc """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def get_size(start_path):
    """ function provides total file or folder size"""
    global total_size
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                if(os.path.getsize(fp) is None):
                    gsize  = 0
                else:
                    gsize = os.path.getsize(fp)
                total_size += gsize
            except FileNotFoundError as fnfe:
                #print("FileNotFoundError "+ str(fnfe))
                #errors.append(str(fnfe))
                FileNotFoundList.append(fp)
                pass
    #return total_size


def get_size_mount(commpath='',mountpath=''):
    global total_size
    global FileNotFoundList
    FileNotFound=FileNotFoundList.copy()

    for FNFD in FileNotFound:
        Dup_FNFD = FNFD.replace(mountpath, commpath)
        try:
            if (os.path.getsize(Dup_FNFD) is None):
                gsize = 0
            else:
                gsize = os.path.getsize(Dup_FNFD)
            FileNotFoundList.remove(FNFD)
            #print(gsize)
            total_size += gsize
        except FileNotFoundError as fnfe:
            print("FileNotFoundError " + str(fnfe))
            # errors.append(str(fnfe))
            FileNotFoundList.append(FNFD)
            pass

def commonprefix(args=[], sep='\\'):
    return os.path.commonprefix(args).rpartition(sep)[0]

def FileNotFoundMountTempDrive(commonprefix_path,calling_func,drvName):
    global total_size
    try:
        #print("\n\n FILETempDrive :"+drvName+" <===> "+calling_func+" <===> "+commonprefix_path)
        print("\n Try to mount :"+drvName)
        #subprocess.call(['Subst', drvName, '/d'])
        MountResult = subprocess.call(['Subst', drvName, commonprefix_path])
        if (MountResult == 0):
            print("Successfully mount new "+drvName+" path for : " + commonprefix_path)
            write_log(lpath, "\n\nSuccessfully mount new "+drvName+" path for : " + commonprefix_path)
            if(calling_func=='get_size'):
                print('Calling get_mount_size')
                get_size_mount(drvName, commonprefix_path)
                print("TOTAL SIZE : "+str(total_size))
                if(subprocess.call(['Subst', drvName, '/d'])==0):
                    print("Successfully unmount new " + drvName + " path for : " + commonprefix_path)
            elif(calling_func=='copy_tree'):
                print('Calling NotFoundCopyTree..')
                NotFoundCopyTree(drvName, commonprefix_path)
            else:
                print('otherfunc')
            #UnmountResult = subprocess.call(['Subst', drvName, '/d'])
            UnmountResult = 1
            if (UnmountResult == 0):
                write_log(lpath, "\n\nSuccessfully unmount new "+drvName+" path for : " + commonprefix_path)
                print("Successfully unmount new "+drvName+" path for : " + commonprefix_path)
        else:
            print("Cannot Mount Drive..")
    except:
        pass

def NotFoundCopyTree(mountdrv,commonprefix_spath):
    #print("\n\n FILE :"+mountdrv)
    global FileNotFoundCopy
    FileNotFoundCopy_dup = FileNotFoundCopy.copy()
    #print("\nMMMMMM" + mountdrv)
    if(mountdrv=='R:'): #SourcePath Modification
        print("R:------------->\n")
        for srckey, destVal in FileNotFoundCopy_dup.items():
            modified_src = srckey.replace(commonprefix_spath, mountdrv)
            print(modified_src+' === > '+ destVal)
            copytree(modified_src,destVal)
            del FileNotFoundCopy[srckey]
    elif(mountdrv=='Y:'): #Destination path modification
        print("Y:------------->\n")
        for srckey, destVal in FileNotFoundCopy_dup.items():
            modified_dest = destVal.replace(commonprefix_spath, mountdrv)
            print(srckey+' === > '+ modified_dest)
            copytree(srckey,modified_dest)
            del FileNotFoundCopy[srckey]
    #print("\n Remaining...")
    #print(FileNotFoundCopy)
    if(len(FileNotFoundCopy)==0):
        print("Going to unmount R: and Y:")
        subprocess.call(['Subst', 'R:', '/d'])
        subprocess.call(['Subst', 'Y:', '/d'])
        print("Successfully unmount Drive. ")


def destination_validate(source_path,dest_path):
    # log file creation in destination
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
        shutil.copystat(source_path, dest_path)
        lpath = dest_path + "\\log.txt"
        errlpath = dest_path + "\\errorlog.txt"
    else:
        lpath = dest_path + "\\log.txt"
        errlpath = dest_path + "\\errorlog.txt"
    return [lpath,errlpath]

def remove_others(li1, li2):
    return (list(set(li1) - set(li2)))


errors = []
after_copy_fsize = 0
dir_counter = 0
file_counter = 0
def copytree(src, dst):
    """ function will copy all the folders, subfolders and files """
    global after_copy_fsize, dir_counter, file_counter
    global FileNotFoundCopy
    if not os.path.exists(dst):
        os.makedirs(dst)
        #shutil.copystat(src, dst)

    if(os.path.isfile(src)):
        try:
            shutil.copy2(src, dst)
            shutil.copystat(src, dst)
            file_counter += 1
            file_info = os.stat(src)
            after_copy_fsize = after_copy_fsize + int(file_info.st_size)
            filesize = convert_bytes(file_info.st_size)
            print("Copied : " + src + " => [ " + filesize + " ]")
            write_log(lpath, "Copied : " + src + " => [ " + filesize + " ]")
        except (FileNotFoundError) as FError:
            #errors.append((src, dst, str(FError)))
            FileNotFoundCopy[src]=dst
        except (IOError, os.error) as why:
            errors.append((src, dst, str(why)))
        except:
            print("Unexpected error:", sys.exc_info())
            errors.append((src, dst, str(sys.exc_info())))

    else:
        try:
            lst = os.listdir(src)
            for item in lst:
                source = os.path.join(src, item)
                destination = os.path.join(dst, item)
                if os.path.isdir(source):
                    dir_counter += 1
                    print("\nCopying From :" + source)
                    write_log(lpath, "Copying From :" + source)
                    copytree(source, destination)
                else:
                    if (os.path.isfile(destination) and os.path.exists(destination)):
                        print("This is file .***************** Already exist")
                        head, tail = os.path.split(destination)
                        filenm= tail.split('.')
                        i=1
                        while os.path.exists(head+'/'+filenm[0]+str(i)+"."+filenm[1]):
                            i = int(i)+1
                            #print('EXIST : '+filenm[0]+str(i)+"."+filenm[1]+' ====> i Value = '+str(i))
                        newfname = filenm[0]+str(i)+"."+filenm[1]
                        destination = head+'/'+newfname
                        #print("New Name = "+newfname)
                        #print("New Path = "+destination)
                    shutil.copy2(source, destination)
                    file_counter += 1
                    file_info = os.stat(source)
                    after_copy_fsize = after_copy_fsize + int(file_info.st_size)
                    filesize=convert_bytes(file_info.st_size)
                    print("Copied : "+source+" => [ "+ filesize +" ]")
                    write_log(lpath, "Copied : "+source+" => [ "+ filesize +" ]")
        except (FileNotFoundError) as FError:
            FileNotFoundCopy[src] = dst
            print('first')
            print(src+"---------->"+dst)
            #errors.append((src, dst, str(FError)))
        except (IOError, os.error) as why:
            errors.append((src, dst, str(why)))
            print('second')
        except:
            print("Unexpected error:", sys.exc_info())
            print('third')
            errors.append((src, dst, str(sys.exc_info())))

print("############## Folders & Files Moving #############\n")
#source_path = input("Please Enter Source Folder Path \n (Ex: C:/SourceFolder) :").replace('\\', '/').strip()
#dest_path = input("Please Enter Destination Folder Path \n (Ex: C:/DestinationFolder) :").replace('\\', '/').strip()

source_path = input("Please Enter Source Folder Path \n (Ex: C:/SourceFolder) :").strip()
dest_path = input("Please Enter Destination Folder Path \n (Ex: C:/DestinationFolder) :").strip()
#source_path = r'\\192.168.1.16\Waiting for Archive 21-07-2016\2019\FA2019-0001\08-FEB-19\CONVERSION\Penguin UK General\eBook\257004\04 Files Modified\2018_09_17_V2\9780241352502_AShortHistoryOfEurope\eBook\9780241352533_EPUB\OPS\images'
#dest_path = r'C:\Users\1582\Desktop\src\images'
#dest_path = r'\\192.168.1.2\Archival\EDUCATION\Test\WaitingforArchive\21-07-2016\2019\FA2019-0001\08-FEB-19\CONVERSION\PenguinUKGeneral\eBook\257004\04FilesModified\2018_09_17_V2\9780241352502_AShortHistoryOfEurope\eBook\9780241352533_EPUB\OPS'

wlog = "log file created successfully.."

#dest_path = '//192.168.3.2/industrialization/RD_Core/DP/Dest'
#source_path = 'C:/Users/1582/Desktop/src'

if(source_path == dest_path):
    print("Cant be give same sourse and destination folder.")
    sys.exit()

while(not os.path.exists(source_path)):
    source_path = input("\nPlease Enter Valid Source Path or Enter exit:").replace('\\', '/').strip()
    if(source_path=='exit'):
        print("Program stopped.")
        sys.exit()

"""while(not os.path.exists(dest_path)):
    dest_path = input("\nPlease Enter Valid Destination Path or Enter exit:").replace('\\', '/').strip()
    if(dest_path=='exit'):
        print("Program stopped.")
        sys.exit()
"""

dest_directories = [x.upper() for x in os.listdir(dest_path)]
#print(dest_directories)
src_directories = [x.upper() for x in os.listdir(source_path)]
#print(src_directories)

copy_of_src_directories = src_directories
folder_dict = {}
for dest_folder_name in dest_directories:
    matching = list(filter(lambda d: dest_folder_name in d, src_directories))
    folder_dict[dest_folder_name] = matching
    copy_of_src_directories = remove_others(copy_of_src_directories, matching)

logpath = destination_validate(source_path, dest_path)
lpath = logpath[0]
epath = logpath[1]
write_log(lpath, wlog)

#start loader
t = threading.Thread(target=animate)
t.start()

before_copy_fsize = get_size(source_path)

commonprefix_path = commonprefix(FileNotFoundList)
write_log(lpath, "*********>>> Common Path : " + str(commonprefix_path))
print(commonprefix_path)
FileNotFoundMountTempDrive(commonprefix_path,'get_size','R:')
print("Total File Size : "+str(total_size))
before_copy_fsize = total_size

write_log(lpath, "Pre-Check File Size : " + str(convert_bytes(before_copy_fsize)))


for dfolder, sfolders in folder_dict.items():
    for dubfolder in sfolders:
        #print("\n Calling copytree \n"+source_path+'/'+dubfolder+"\n\n Dest = >"+dest_path+'/'+dfolder)
        copytree(source_path+'/'+dubfolder, dest_path+'/'+dfolder)

for others in copy_of_src_directories:
    spt1 = others.split('.')
    if (len(spt1) > 1):
        copytree(source_path + '/' +others, dest_path+'\OTHERS')
    else:
        copytree(source_path+'/'+others, dest_path +'/'+others)


#print("CANT Copy Files :\n ")
#print(FileNotFoundCopy)

FNFC_SourceKey = list(FileNotFoundCopy.keys())
#print("KEYS \n")
#print(FNFC_SourceKey)

commonprefix_path_src = commonprefix(FNFC_SourceKey)
print(commonprefix_path_src)
write_log(lpath, "*********>>> Common Path : " + str(commonprefix_path_src))
FileNotFoundMountTempDrive(commonprefix_path_src,'copy_tree','R:')
print(FileNotFoundCopy)

#sys.exit()
#for destination having lengthy path
if(len(FileNotFoundCopy)>0):
    print('May Destination have long path')
    destValList = list(FileNotFoundCopy.values())
    print(destValList)
    commonprefix_path_src = commonprefix(destValList)
    print(commonprefix_path_src)
    write_log(lpath, "*********>>> Common Path : " + str(commonprefix_path_src))
    FileNotFoundMountTempDrive(commonprefix_path_src, 'copy_tree','Y:')

if(errors):
    print("\nIt has some erros , see on error log file **************"+epath+"*******************")
    print(errors)
    write_log(lpath, "It has some erros , see on error log file **************"+epath+"*******************")
    write_log(epath, errors)

write_log(lpath, "Post-Check File Size :"+str(convert_bytes(after_copy_fsize)))

print("\nPre-Check File Size : " + str(convert_bytes(before_copy_fsize)))
print("Post-Check File Size : "+str(convert_bytes(after_copy_fsize)))

if(before_copy_fsize == after_copy_fsize):
    write_log(lpath,"Successfully Copied All The File(s) & Folder(s)")
    print("Successfully Copied All The File(s) & Folder(s)")
else:
    write_log(lpath, "Wrong! Somewhere Bytes Are Missing.")
    print("Wrong! Somewhere Bytes Are Missing.")

prt="\nTotal Directories and files copied : "+str(dir_counter)+" and "+str(file_counter)
print(prt)
write_log(lpath,prt)
print("\nLog File - Generated @ "+lpath)
done = True
print("\n############## END #############")
write_log(lpath, "End \n ======================================")
