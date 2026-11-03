# Required libraries
import os
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from moviepy.editor import AudioFileClip
from pytubefix import YouTube

DEFAULT_WORKERS = 4

def printBanner():
    """
    Function to print the banner at the start of the program.
    """
    # Define banner as a multi-line string
    banner = """
    _  _    ____    _  _      ___      ____       ____    ____         __  __      ___    ____   
   FJ  L]  /_  _\  FJ  L]    F _ ",   F ___J     /_  _\  F __ ]       F  \/  ]    F _ ", F___ J  
  J |  | L [J  L] J |  | L  J `-'(|  J |___:     [J  L] J |--| L     J |\__/| L  J `-' | `-__| L 
  | |  | |  |  |  | |  | |  | ,--.\  | _____|     |  |  | |  | |     | |`--'| |  |  __/F  |__  ( 
  F L__J J  F  J  F L__J J  F L__J \ F L____:     F  J  F L__J J     F L    J J  F |__/.-____] J 
 J\______/FJ____LJ\______/FJ_______JJ________L   J____LJ\______/F   J__L    J__LJ__|   J\______/F
  J______F |____| J______F |_______F|________|   |____| J______F    |__L    J__||__L    J______F 
                                                                                                 
    Devilware                                                                                                                 
    """
    # Print the banner
    print(banner)

def printMenu():
    """
    Function to print the menu options for the user.
    """
    # Print the menu options
    print("Please choose an option:")
    print("1. Start")
    print("2. Exit")

def sanitize(name):
    """
    Remove characters that are invalid in file names.
    """
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip() or "audio"

def uniquePath(directory, name):
    """
    Return a non-existing mp3 path inside directory.
    """
    path = os.path.join(directory, f"{name}.mp3")
    i = 1
    while os.path.exists(path):
        path = os.path.join(directory, f"{name} ({i}).mp3")
        i += 1
    return path

def convertOne(url, outputDir):
    """
    Download a single YouTube URL and convert it to mp3.
    Returns (url, output path). Raises on failure.
    """
    with tempfile.TemporaryDirectory() as tmp:
        youtube = YouTube(url)
        stream = youtube.streams.get_audio_only() or youtube.streams.first()
        downloadedFile = stream.download(output_path=tmp)
        outputPath = uniquePath(outputDir, sanitize(youtube.title))
        clip = AudioFileClip(downloadedFile)
        try:
            clip.write_audiofile(outputPath, logger=None)
        finally:
            clip.close()
    return url, outputPath

def readUrls():
    """
    Read several URLs (separated by spaces, commas or new lines).
    An empty line finishes the input.
    """
    print("Enter YouTube URLs (several per line allowed). Empty line to finish:")
    urls = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        urls.extend(u for u in re.split(r"[\s,]+", line) if u)
    return urls

def startConversion():
    """
    Convert several YouTube videos into mp3 files, in parallel.
    """
    urls = readUrls()
    if not urls:
        print("No URLs given.")
        return

    outputDir = input("Output folder [current folder]: ").strip() or "."
    workersInput = input(f"Parallel downloads [{DEFAULT_WORKERS}]: ").strip()
    workers = int(workersInput) if workersInput.isdigit() and int(workersInput) > 0 else DEFAULT_WORKERS
    os.makedirs(outputDir, exist_ok=True)

    ok, failed = 0, 0
    print(f"Processing {len(urls)} link(s) with {min(workers, len(urls))} worker(s)...")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(convertOne, u, outputDir): u for u in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                _, path = future.result()
                ok += 1
                print(f"[OK]   {url} -> {path}")
            except Exception as e:
                failed += 1
                print(f"[FAIL] {url}: {e}")
    print(f"Done: {ok} succeeded, {failed} failed.")

def main():
    """
    The main function that runs the program.
    """
    while True:
        # Print the banner and menu
        printBanner()
        printMenu()

        # Get the user's choice
        choice = input("Your choice: ")

        if choice == '1':
            # If the user chooses '1', start the conversion process
            startConversion()
        elif choice == '2':
            # If the user chooses '2', break the loop to end the program
            print("Exiting...")
            break
        else:
            # If the user doesn't choose '1' or '2', print an error message
            print("Invalid option. Please try again.\n")

# If this file is the main script, run the main function
if __name__ == "__main__":
    main()
