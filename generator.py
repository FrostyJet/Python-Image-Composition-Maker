import requests
from lxml import html
from PIL import Image
import sys

searchEngine = "yahoo"

query = input("What are you looking for? \r\n")

if searchEngine == "google":
    searchQueryUrl = "https://www.google.com/search?q=%s&tbm=isch" % (query)
elif searchEngine == "yandex":
    searchQueryUrl = "https://yandex.com/images/search?from=tabbar&text=%s" % (query)
elif searchEngine == "yahoo":
    searchQueryUrl = "https://images.search.yahoo.com/search/images?p=%s" % (query)

page = requests.get(searchQueryUrl)

f = open("composition.source.html", "wb")
f.write(page.content)
f.close()

tree = html.fromstring(page.content)

if searchEngine == "google":
    images = tree.xpath("//tr//img")
elif searchEngine == "yandex":
    images = tree.xpath("//img[contains(@class, 'serp-item__thumb')]")
elif searchEngine == "yahoo":
    images = tree.xpath("//*[@id='results']//img")

cols = 5
ideal_width = int(input("Width? \r\n"))
ideal_height = int(input("Height? \r\n"))

srcs = []
for img in images:
    if searchEngine == "google" or searchEngine == 'yahoo':
        imgSrc = img.get("src")
    elif searchEngine == "yandex":
        imgSrc = 'https:' + img.get("src")

    if not imgSrc: 
        continue

    print(imgSrc)
    srcs.append(imgSrc)

if len(imgSrc) < 1: 
    print("Could not find anything")
    sys.exit()

imgIds = []
for i in range(0, cols):
    row = []
    for j in range(0, cols):
        index = cols * i + j
        if index >= len(srcs):
            break

        row.append(0)
        imgSrc = srcs[index]

        result = requests.get(imgSrc)

        try:
            file = open("sources/" + str(index) + ".png", "wb")
            file.write(result.content)
            file.close()
        except:
            print("Skipping missing file")
            continue

        pass
    imgIds.append(row)
    pass

blankImage = Image.new(
    "RGBA", (cols * ideal_width, cols * ideal_height), "BLACK")

for i in range(0, cols):
    for j in range(0, cols):
        index = cols * i + j
        if index >= len(images):
            break

        try:
            gridSection = Image.open("sources/" + str(index) + ".png")
        except:
            print("Skipping missing file")
            continue

        x = 0
        y = 0

        if i > 0:
            x = imgIds[i - 1][j]["x"] + imgIds[i - 1][j]["w"]

        if j > 0:
            y = imgIds[i][j - 1]["y"] + imgIds[i][j - 1]["h"]

        aspect = gridSection.width / float(gridSection.height)

        ideal_aspect = ideal_width / float(ideal_height)

        if aspect > ideal_aspect:
            # Then crop the left and right edges:
            new_width = int(ideal_aspect * gridSection.height)
            offset = (gridSection.width - new_width) / 2
            resize = (offset, 0, gridSection.width -
                      offset, gridSection.height)
        else:
            # ... crop the top and bottom:
            new_height = int(gridSection.width / ideal_aspect)
            offset = (gridSection.height - new_height) / 2
            resize = (0, offset, gridSection.width,
                      gridSection.height - offset)

        thumb = gridSection.crop(resize).resize(
            (ideal_width, ideal_height), Image.ANTIALIAS)

        imgIds[i][j] = {
            "x": x,
            "y": y,
            "w": ideal_width,
            "h": ideal_height
        }

        print(imgIds[i][j])

        blankImage.paste(thumb, (x, y))
        pass
    pass

blankImage.save("composition.png", quality=95)
blankImage.show()
