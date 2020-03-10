import hashlib
import sys
import os
# import zipfile

from prettytable import PrettyTable


start = []
end = []
pdfStartMN = "25504446"
pdfEndMN = "454f46"
pngStartMN = "89504e470d0a1a0a"
pngEndMN = "49454e44ae426082"
# oleStartMN = "d0cf11e0a1b11ae1" # Didnt implement because DOC XLS doesnt have a trailer
ooxmlStartMN = "504b030414000600"
ooxmlEndMN = "504b0506"
table = PrettyTable(["Filename","Hash","Start","End","Size","Type"])


outputDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Output")


def convertHexToString(input):
    return ''.join(format(x, '02x') for x in input)


def writeFile(fileName, contentData):
    file = open(outputDir + "/" + fileName, 'wb')
    file.write(contentData)
    file.close()


def createTempDir():
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)


def createFiles(filetype, startArray, endArray):
    for i in startArray:
        for j in endArray:
            if i < j:
                filename = filetype + "_" + str(i) + "_" + str(j) + "." + filetype
                writeFile(filename, contents[i:j])
    clearArray()


def checkForPDF(contents):
    for index, value in enumerate(contents):
        # PDF
        if value == 37:
            input = contents[index:index + 4]
            if convertHexToString(input) == pdfStartMN:
                start.append(index)
        elif value == 69:
            input = contents[index:index + 3]
            if convertHexToString(input) == pdfEndMN:
                endIndex = 0
                if contents[index + 4] == 10:
                    endIndex = index + 5
                elif contents[index + 4] == 13:
                    if contents[index + 5] == 10:
                        endIndex = index + 6
                    else:
                        endIndex = index + 5
                else:
                    endIndex = index + 4
                end.append(endIndex)
                if len(start) == 1 and len(end) == 1:
                    createFiles("pdf",start,end)
    createFiles("pdf", start, end)


def checkForPNG(contents):
    for index, value in enumerate(contents):
        # PDF
        if value == 137:
            input = contents[index:index + 8]
            if convertHexToString(input) == pngStartMN:
                start.append(index)
        elif value == 73:
            input = contents[index:index + 8]
            if convertHexToString(input) == pngEndMN:
                end.append(index+9)
                if len(start) == 1 and len(end) == 1:
                    createFiles("png",start,end)
    createFiles("png", start, end)


# def checkForOLE(contents):
#     for index, value in enumerate(contents):
#         # DOC,XLS,PPT,etc.
#         if value == 208:
#             input = contents[index:index + 8]
#             if convertHexToString(input) == oleStartMN:
#                 start.append(index)


def checkForOOXML(contents):
    for index, value in enumerate(contents):
        # DOC,XLS,PPT,etc.
        if value == 80:
            input = contents[index:index+8]
            input2 = contents[index:index+4]
            if convertHexToString(input) == ooxmlStartMN:
                start.append(index)
            elif convertHexToString(input2) == ooxmlEndMN:
                end.append(index+4+18)
                if len(start) == 1 and len(end) == 1:
                    createFiles("docx",start,end)
    createFiles("docx",start,end)


def checkForJPG(contents):
    for index,value in enumerate(contents):
        if value == 255:
            if contents[index + 1] == 216 and contents[index + 2] == 255:
                start.append(index)
            elif contents[index + 1] == 217:
                end.append(index + 2)
                if len(start) == 1 and len(end) == 1:
                    createFiles("jpg",start,end)
    # Produces a lot of files because there are a lot of matches for the JPG file signatures.
    createFiles("jpg",start,end)


def clearArray():
    global start,end
    start = []
    end = []

# Uncomment this code to check whether the files are corrupt or not.
# Note: Install PIL and zipfile libraries to check them and import these libraries.
# def checkFiles():
#     for i in os.listdir(outputDir):
#         if i.endswith(".docx"):
#             file = outputDir + "/" + i
#             try:
#                 if isValidDocx(file):
#                     print(file)
#             except:
#                 print("Exception",file)
#                 os.remove(file)
#         if i.endswith(".jpg") or i.endswith(".png"):
#             file = outputDir + "/" + i
#             try:
#                 img = Image.open(file)  # open the image file
#                 img.verify()  # verify that it is, in fact an image
#             except (IOError, SyntaxError) as e:
#                 os.remove(file)
#
# def isdir(z, name):
#     return any(x.startswith("%s/" % name.rstrip("/")) for x in z.namelist())
#
#
# def isValidDocx(filename):
#     f = zipfile.ZipFile(filename, "r")
#     return isdir(f, "word") and isdir(f, "docProps") and isdir(f, "_rels")


def hashFiles():
    for filename in os.listdir(outputDir):
        file = outputDir + "/" + filename
        hash = hashlib.md5(open(file, 'rb').read()).hexdigest()
        fileComponents = file.split(".")
        filetype = fileComponents[1]
        fileComponents = fileComponents[0].split("_")
        filestart = int(fileComponents[1])
        fileend = int(fileComponents[2])
        table.add_row([filename, hash, filestart,fileend,fileend-filestart, filetype])
    print(table)
    with open("output.txt", "w") as f:
        f.write(str(table))


if __name__ == "__main__":
    createTempDir()
    if(len(sys.argv) > 1):
        with open(sys.argv[1], "rb") as f:
            contents = f.read()
            checkForPDF(contents)
            checkForPNG(contents)
            checkForOOXML(contents)
            checkForJPG(contents)
            # checkFiles()
            hashFiles()

    else:
        print("Usage: python3 datacarver.py <file_to_be_carved>")