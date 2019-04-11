import os
import shutil
import datetime
import sys

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
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def destination_validate(source_path,dest_path):
    # log file creation in destination
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
        shutil.copystat(source_path, dest_path)
        lpath = dest_path + "/log.txt"
        errlpath = dest_path + "/errorlog.txt"
    else:
        lpath = dest_path + "/log.txt"
        errlpath = dest_path + "/errorlog.txt"
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
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)

    if(os.path.isfile(src)):
        try:

            shutil.copy2(src, dst)
            file_counter += 1
            file_info = os.stat(src)
            after_copy_fsize = after_copy_fsize + int(file_info.st_size)
            filesize = convert_bytes(file_info.st_size)
            print("Copied : " + src + " => [ " + filesize + " ]")
            write_log(lpath, "Copied : " + src + " => [ " + filesize + " ]")
        except (IOError, os.error) as why:
            errors.append((src, dst, str(why)))

    else:
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
                try:
                    print(source + "---->" + destination)
                    if (os.path.isfile(destination) and os.path.exists(destination)):
                        print("This is file .***************** Already exist")
                        head, tail = os.path.split(destination)
                        filenm= tail.split('.')
                        i=1
                        while os.path.exists(head+'/'+filenm[0]+str(i)+"."+filenm[1]):
                            i = int(i)+1
                            print('EXIST : '+filenm[0]+str(i)+"."+filenm[1]+' ====> i Value = '+str(i))
                        newfname = filenm[0]+str(i)+"."+filenm[1]
                        destination = head+'/'+newfname
                        print("New Name = "+newfname)
                        print("New Path = "+destination)
                    shutil.copy2(source, destination)
                    file_counter += 1
                    file_info = os.stat(source)
                    after_copy_fsize = after_copy_fsize + int(file_info.st_size)
                    filesize=convert_bytes(file_info.st_size)
                    print("Copied : "+source+" => [ "+ filesize +" ]")
                    write_log(lpath, "Copied : "+source+" => [ "+ filesize +" ]")
                except (IOError, os.error) as why:
                    errors.append((source, destination, str(why)))

print("############## Folders & Files Moving #############\n")
#source_path = input("Please Enter Source Folder Path \n (Ex: C:/SourceFolder) :").replace('\\', '/').strip()
#dest_path = input("Please Enter Destination Folder Path \n (Ex: C:/DestinationFolder) :").replace('\\', '/').strip()
wlog = "log file created successfully.."

dest_path = '//192.168.3.2/industrialization/RD_Core/DP/Dest'
source_path = 'C:/Users/1582/Desktop/src'

if(source_path == dest_path):
    print("Cant be give same sourse and destination folder.")
    sys.exit()

while(not os.path.exists(source_path)):
    source_path = input("Please Enter Valid Source Path or Enter exit:").replace('\\', '/').strip()
    if(source_path=='exit'):
        print("Program stopped.")
        sys.exit()

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
before_copy_fsize = get_size(source_path)
write_log(lpath, "Pre-Check File Size : " + str(convert_bytes(before_copy_fsize)))

for dfolder, sfolders in folder_dict.items():
    for dubfolder in sfolders:
        copytree(source_path+'/'+dubfolder, dest_path+'/'+dfolder)

for others in copy_of_src_directories:
    spt1 = others.split('.')
    if (len(spt1) > 1):
        copytree(source_path + '/' +others, dest_path+'/OTHERS')
    else:
        copytree(source_path+'/'+others, dest_path +'/'+others)

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
print("\n############## END #############")
write_log(lpath, "End \n ======================================")
