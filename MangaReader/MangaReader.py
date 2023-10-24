import requests
from bs4 import BeautifulSoup
#import hyper
import urllib3
#from hyper.contrib import HTTP20Adapter
import shutil
#import cfscrape
import psutil
import os
import json
import math
import subprocess
saveAnim = {
    "name":"",
    "info-link":"",
    "last-chapter": 1,
    "next-chapter": 2
}

#saves a manga
def saveManga():
    result = False;
    count = 0;
    for manga in data["anime-history"]:
        if str(manga["name"]) == str(saveAnim["name"]):
            data["anime-history"][0] = saveAnim;
            print("Is the case!")
            result = True;
        count+=1;
    if result == False:
        #adds the anime from anime history into a saveAnim list if its not found in the saveAnim list
        data["anime-history"].append(saveAnim);
    with open("history.json","w") as f:
        json.dump(data,f);
def startReader(links):
    subprocess.Popen([r"MangaReader.exe",saveAnim["name"]+" Chapter: "+str(saveAnim["last-chapter"])])
    running = True;
    while running == True:
        if checkIfProcessRunning("MangaReader.exe") == False:
            folder = 'Manga'
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e));
            running = False;
            ask = input("Do you want to read next chapter? \n 1.Yes \n 2.No search Again \n 3.Go to Recent mangas! \n Type number corresponding to answer.\n");
            # number coresponds to the user input
            if int(ask) == 1:
                # sends user to next ch
                nextChapter(links);
            elif int(ask) == 2:
                ask = input("Would you like to save this manga to your favorites? \n 1.Yes \n 2.No\n");
                if int(ask) == 1:
                    saveManga();
                    search();
                elif int(ask) == 2:
                    search();
            elif int(ask) == 3:
                recent();
def nextChapter(links):
    chapter = links;
    ask = saveAnim["next-chapter"];
    try:
        if(int(ask) > len(links) or int(ask) < 0):
            print('There is nothing corresponding to this number!');
            start();
        saveAnim["last-chapter"] = int(ask);
        saveAnim["next-chapter"] = int(ask)+1;
        page = requests.get(links[len(links)-int(ask)].get('href'));
        soup = BeautifulSoup(page.content, 'html.parser');
    except:
        print("Next Chapter Isn't Out Yet: " + str(ask));
        search();
    results = soup.find(class_='container-chapter-reader');
    links = results.select('img');
    count = 0;
    for i in links:
        download(i.get("src"),str(count));
        count+=1;
    startReader(chapter);
def readChapter(links):
    chapter = links;
    count = len(links);
    for i in links:
        print(str(count) +"."+ i.text);
        count-=1;
    ask = input("Pick the number corresponding to the Manga/Manwha chapter to read or press enter to search again \n");
    if not ask:
        start();
    else:
        try:
            if(int(ask) > len(links) or int(ask) < 0):
                print('There is nothing corresponding to this number!');
                search();
            saveAnim["last-chapter"] = int(ask);
            saveAnim["next-chapter"] = int(ask)+1;
            page = requests.get(links[len(links)-int(ask)].get('href'));
            soup = BeautifulSoup(page.content, 'html.parser');
        except:
            print("Not a VALID number please try again!");
            search();
    results = soup.find(class_='container-chapter-reader');
    links = results.select('img');
    count = 0;
    for i in links:
        download(i.get("src"),str(count));
        count+=1;
    startReader(chapter);
def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;
def download(url,pathname):
    request = requests.get(url,headers={'accept':'image/avif,image/webp,image/apng,image/*,*/*;q=0.8','referer':'https://chap.manganelo.com/','sec-fetch-dest':'image','sec-fetch-mode':'no-cors','sec-fetch-site':'cross-site','user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'},stream = True);
    pathnameEx = url.split('.')[-1]; 
    if request.status_code == 200:
        request.raw.decode_content = True;
        with open('Manga/'+pathname+'.'+pathnameEx,'wb') as f:
            shutil.copyfileobj(request.raw,f);
        print('Image Success!');
    else:
        print('Image Failed '+str(request.status_code));
        search();

def search():
    searched = input("What is it you want to read?");
    searchString = searched.replace(" ", '_');
    url = 'https://m.manganelo.com/search/story/'+searchString; #Url of the website
    page = requests.get(url);#Returns the html
    soup = BeautifulSoup(page.content, 'html.parser'); #Parses the html
    results = soup.find(class_='panel-search-story');
    links = results.select('div.search-story-item > a.item-img');
    count = 0;
    for i in links:
        print(str(count)+'.'+i.select('img')[0].get('alt'));
        count+=1;
    ask = input("Pick the number corresponding to the Manga/Manwha to read or press enter to try again \n");
    if not ask:
        start();
    else:
        try:
            if(int(ask) > len(links) or int(ask) < 0):
                print('There is nothing corresponding to this number!');
                search();
            saveAnim["name"] = links[int(ask)].select('img')[0].get('alt');
            saveAnim["info-link"] = links[int(ask)].get('href');
            page = requests.get(links[int(ask)].get('href'));
            soup = BeautifulSoup(page.content, 'html.parser');
        except:
            print("Not a VALID number please try again!");
            search();
    results = soup.find(class_="row-content-chapter");
    links = results.select('li.a-h > a');
    readChapter(links);
def recent():
    with open("history.json") as f:
        data = json.load(f);
    count = 0;
    for manga in data["anime-history"]:
        print(str(count)+"."+str(manga["name"]));
        count+=1;
    ask = input("Pick the number corresponding to the Manga/Manwha to read or press enter to try again \n");
    if ask == '':
        recent();
    else:
        try:
            if(int(ask) > len(data["anime-history"]) or int(ask) < 0):
                print('There is nothing corresponding to this number!');
                search();
            saveAnim["name"] = data["anime-history"][int(ask)]["name"];
            saveAnim["info-link"] = data["anime-history"][int(ask)]["info-link"];
            page = requests.get(data["anime-history"][int(ask)]["info-link"]);
            soup = BeautifulSoup(page.content, 'html.parser');
        except:
            print("Not a VALID number please try again!");
            search();
    favorite = ask;
    results = soup.find(class_="row-content-chapter");
    links = results.select('li.a-h > a');
    chapter = links;
    count = len(links);
    for i in links:
        print(str(count) +"."+ i.text);
        count-=1;
    ask = input("Pick the number corresponding to the Manga/Manwha chapter to read or press enter to search again \n");
    if ask == '':
        search();
    else:
        if ask.lower() == "current":
            saveAnim["last-chapter"] = data["anime-history"][int(favorite)]["last-chapter"];
            saveAnim["next-chapter"] = data["anime-history"][int(favorite)]["next-chapter"];
            page = requests.get(links[len(links)-data["anime-history"][int(favorite)]["last-chapter"]].get('href'));
        elif ask.lower() == "next":
            saveAnim["last-chapter"] = data["anime-history"][int(favorite)]["next-chapter"];
            saveAnim["next-chapter"] = data["anime-history"][int(favorite)]["next-chapter"]+1;
            page = requests.get(links[len(links)-data["anime-history"][int(favorite)]["last-chapter"]].get('href'));
        elif ask.isdigit():
            if int(ask) < len(links) or int(ask) > 0:
                saveAnim["last-chapter"] = int(ask);
                saveAnim["next-chapter"] = int(ask)+1;
                page = requests.get(links[len(links)-int(ask)].get('href'));
        soup = BeautifulSoup(page.content, 'html.parser');
    results = soup.find(class_='container-chapter-reader');
    links = results.select('img');
    count = 0;
    for i in links:
        download(i.get("src"),str(count));
        count+=1;
    startReader(chapter);    
def start():
    try:
        begin = input('Type number to corresponding action \n 1.Search \n 2.Read recent manga \n 3.Close app \n');
        if int(begin) == 1:
            search();
        elif int(begin) == 2:
            recent();
        elif int(begin) == 3:
            return 0;
        else:
            print("Not an Option");
            start();
    except:
        print("Only input accepted is 1, 2, or 3!")
        start();
with open("history.json") as f:
    data = json.load(f);
start();


