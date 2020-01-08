import os
import requests
import json
import img2pdf
from bs4 import BeautifulSoup as BS
from io import BytesIO

download_dir = ""
info_file_path = "info.json"

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0'}

def download_chapter(manga_name, chap_url, chap_name):
    chap_location = os.path.join(download_dir, manga_name)
    
    if(not os.path.exists(chap_location)):
            os.mkdir(chap_location)
    
    target_file = open(os.path.join(chap_location, chap_name+".pdf"), "wb")
    image_data = []
    downloaded = False
    
    #downloading 
    soup = BS(requests.get(chap_url, headers=headers).text, "html.parser")
    for img in soup.find_all("img"):
            if(("chapter" in img['src'].lower()) or ("chap" in img['src'].lower())):
                image_data.append(BytesIO(requests.get(img['src'], headers=headers).content))
    
    #writing           
    try:
        if(len(image_data) == 0):
            raise ValueError("no image data")
                
        target_file.write(img2pdf.convert(image_data))
        print("downloaded", manga_name, "chapter", chap_name)
        downloaded = True
    
    except Exception as e:
        os.remove(os.path.join(chap_location, chap_name+".pdf"))
        print("unable to download", manga_name, "chapter", chap_name)
        print(e)
        downloaded = False
        
    target_file.close()
    
    #update info.json
    if(downloaded):
        update_info(manga_name, chap_name)
    
    return downloaded
    
def update_info(manga_name, chap_name):
    manga_list[manga_name]['last_chapter'] = chap_name
    
    os.remove(info_file_path)
    
    with open(info_file_path, "w") as new_info_file:
        json.dump(manga_list, new_info_file)
    
def populate_chapters_to_download(manga_name, manga_url, last_chap):
        chapters_to_download = []
        manga_homepage = BS(requests.get(manga_url, headers=headers).text, "html.parser")
        
        for atag in manga_homepage.find_all('a'):
            try:
                if(manga_name.lower() in atag['title'].lower()):
                    if(last_chap.lower() == atag['href'].split("/")[-1].lower()):
                        return chapters_to_download
                        
                    chap_name = atag['href'].split("/")[-1]
                    chapters_to_download.append((chap_name, atag['href']))
            except KeyError:
                pass
        
        return chapters_to_download
    
#Checking info file
if(not os.path.exists(info_file_path)):
    print("Manga records empty, create info.json")
else:
    manga_list = json.loads(open("info.json", "r", encoding="utf-8").read())
    

for manga_name in manga_list:
    chapter_list = populate_chapters_to_download(manga_name, manga_list[manga_name]['url'], manga_list[manga_name]["last_chapter"])
    
    if(len(chapter_list) > 0):
        for chap in sorted(chapter_list, key=lambda x: x[0]):
            download_chapter(manga_name, chap[1], chap[0])
    else:
        print("No new chapters for", manga_name)
