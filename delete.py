import os

def deleteMp4(folderPath, originFile):
    files = os.listdir(folderPath)
    for file in files:
        if file.endswith('.mp4') and file != originFile:
            os.remove(os.path.join(folderPath, file))


def deleteM3u8(folderPath):
    files = os.listdir(folderPath)
    for file in files:
        if file.endswith('.m3u8'):
            os.remove(os.path.join(folderPath, file))
