# In[0]:
from bs4 import BeautifulSoup
from selenium import webdriver


def movieLinks(url):
  links = []

  options = webdriver.ChromeOptions()
  options.binary_location = "chrome-win32/chrome.exe"
  options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
  )

  dr = webdriver.Chrome(options=options)

  print("getting url:", url)

  dr.get(url)

  bs = BeautifulSoup(dr.page_source,"html.parser")
  a_tags = bs.select('div.img-box>a')
  print(a_tags)
  for a_tag in a_tags:
    links.append(a_tag['href'])
  print('获取到 {0} 個影片'.format(len(links)))
  print(links)
  return links

# %%
