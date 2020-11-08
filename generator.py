import sys
import requests
from lxml import html
from PIL import Image

cols = 5
searchEngine = "yahoo"
query = input("What are you looking for? \r\n")
ideal_width = int(input("Width? \r\n"))
ideal_height = int(input("Height? \r\n"))


def buildSearchUrl(query):
    if searchEngine == "google":
        searchQueryUrl = "https://www.google.com/search?q=%s&tbm=isch" % (
            query)
    elif searchEngine == "yandex":
        searchQueryUrl = "https://yandex.com/images/search?from=tabbar&text=%s" % (
            query)
    elif searchEngine == "yahoo":
        searchQueryUrl = "https://images.search.yahoo.com/search/images?p=%s" % (
            query)
    return searchQueryUrl


def fetchPageContents(url):
    page = requests.get(url)
    f = open("composition.source.html", "wb")
    f.write(page.content)
    f.close()
    return page


def extractImageUrls(content):
    tree = html.fromstring(content)
    if searchEngine == "google":
        images = tree.xpath("//tr//img")
    elif searchEngine == "yandex":
        images = tree.xpath("//img[contains(@class, 'serp-item__thumb')]")
    elif searchEngine == "yahoo":
        images = tree.xpath("//*[@id='results']//img")

    urls = []
    for img in images:
        if searchEngine == "google" or searchEngine == 'yahoo':
            imgSrc = img.get("src")
        elif searchEngine == "yandex":
            imgSrc = 'https:' + img.get("src")

        if not imgSrc:
            continue

        urls.append(imgSrc)

    return urls


def downloadImages(imageUrls):
    imgIds = []
    for i in range(0, cols):
        row = []
        for j in range(0, cols):
            index = cols * i + j
            if index >= len(imageUrls):
                break

            row.append(0)
            imgSrc = imageUrls[index]

            result = requests.get(imgSrc)

            print("%s : %s" % (index, imgSrc))

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
    return imgIds


def createImageComposition(imgIds):
    blankImage = Image.new(
        "RGBA", (cols * ideal_width, cols * ideal_height), "BLACK")

    for i in range(0, cols):
        for j in range(0, cols):
            index = cols * i + j

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


def main():
    url = buildSearchUrl(query)
    page = fetchPageContents(url)
    print('Searching trough the web')

    print('Extracting Images')
    imageUrls = extractImageUrls(page.content)

    print('Downloading...')
    imgIds = downloadImages(imageUrls)

    print('Final Step! Creating the composition...')
    createImageComposition(imgIds)

    if len(imageUrls) < 1:
        print("Could not find anything")
        sys.exit()


if __name__ == "__main__":
    main()
    pass
