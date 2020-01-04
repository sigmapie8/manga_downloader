import os
import requests
import json
import img2pdf
from bs4 import BeautifulSoup as BS
from io import BytesIO

download_dir = ""
info_file_path = "info.json"

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0'}

def download_chapter(manga_name, chapters_to_download):
    updated = False
    for chap_name in chapters_to_download:
        chap_location = download_dir+"/"+manga_name+"/"
        
        #checking if location exist, if not create it
        if(not os.path.exists(chap_location)):
            os.mkdir(chap_location)
        
        target_file = open(chap_location+chap_name, "wb")
    
        
        image_data = []

        soup = BS(requests.get(chapters_to_download[chap_name], headers=headers).text, "html.parser")
        for img in soup.find_all("img"):
            
            if(("chapter" in img['src'].lower()) or ("chap" in img['src'].lower())):
                updated = True
                image_data.append(BytesIO(requests.get(img['src'], headers=headers).content))
        
        try:
            if(len(image_data) == 0):
                raise ValueError("no image data")
                
            target_file.write(img2pdf.convert(image_data))
            print("downloaded", manga_name, "chapter", chap_name)
            
        except Exception as e:
            updated = False
            os.remove(chap_location+chap_name)
            print("unable to download", manga_name, "chapter", chap_name)
            print(e)
        
        target_file.close()
    return updated
    
def populate_chapters_to_download(manga_name, url, lchap):
        chapters_to_download = dict()
        manga_homepage = BS(requests.get(url, headers=headers).text, "html.parser")
        
        for atag in manga_homepage.find_all('a'):
            try:
                if(manga_name.lower() in atag['title'].lower()):
                    if(lchap.lower() == atag['href'].split("/")[-1].lower()):
                        return chapters_to_download
                        
                    chap_name = atag['href'].split("/")[-1] + ".pdf"
                    chapters_to_download[chap_name] = atag['href']
            except KeyError:
                pass
        
        return chapters_to_download
    
#Checking info file
if(not os.path.exists(info_file_path)):
    print("Manga records empty")
else:
    info_file = json.loads(open("info.json", "r", encoding="utf-8").read())
    

for manga_name in info_file:
    chapter_dictionary = populate_chapters_to_download(manga_name, info_file[manga_name]['url'], info_file[manga_name]["last_chapter"])
    
    last_chapter_name = sorted(chapter_dictionary)[-1] if len(chapter_dictionary) > 0 else print("No new chapters for", manga_name)
    download_succesful = download_chapter(manga_name, chapter_dictionary)
    
    if(download_succesful):
        info_file[manga_name]['last_chapter'] = ".".join(last_chapter_name.split(".")[:-1])
        os.remove(info_file_path)
        with open(info_file_path, "w") as new_info_file:
            json.dump(info_file, new_info_file)
