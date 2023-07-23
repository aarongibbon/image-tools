import hashlib
import os
import sys

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

files = [os.path.abspath(os.path.join(dirpath, f)) for dirpath,_,files in os.walk(sys.argv[1]) for f in files]

substringsToExclude=['unorganized/', '2015/']
processedFiles = {}
numOfFiles = str(len(files))
count=0
excluded=0
for f in files:
    if any(substring in f for substring in substringsToExclude):
        excluded += 1
    else:
        md5hash=str(md5(f))
        if md5hash in processedFiles:
            processedFiles[md5hash].append(f)
        else:
            processedFiles[md5hash] = [f]
    print("Processed {}/{}, {} excluded.".format(str(count), numOfFiles, str(excluded)), end='\r')
    count+=1

#Processed " + str(count) + "/" + numOfFiles + ", , end='\r')

cwd = os.getcwd()
with open(cwd+"/"+sys.argv[2], "w") as duplicateFileOutput:
    duplicateFileOutput.write("{} files found, {} unique files identified\n\n".format(numOfFiles, len(processedFiles.keys())))

    for md5hash in processedFiles:
        filesByPathLength = sorted(processedFiles[md5hash], key=lambda path: path.count("/"), reverse=True)
        numOfFilesWithSameHash = len(filesByPathLength)
        if numOfFilesWithSameHash > 1:
            duplicateFileOutput.write("{} , Count: {}\n".format(md5hash, numOfFilesWithSameHash))
            duplicateFileOutput.write(filesByPathLength[0]+"\n") 
            for filePath in filesByPathLength[1:]:
                renamedFile=filePath+".TODELETE"
#                os.rename(filePath, renamedFile)
                duplicateFileOutput.write(renamedFile+"\n")
            duplicateFileOutput.write("\n")
            

#os.path.dirname(os.path.realpath(__file__)))

#print(len(files))
#print(len(processedFiles.keys()))
