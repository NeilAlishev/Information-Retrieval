import re
import json
from lxml import html
import urllib.request

URL_BASE = "http://www.mathnet.ru"

URL = "http://www.mathnet.ru/php/archive.phtml?jrnid=uzku&wshow=issue&bshow=contents&series=0&year=2016&volume=158" \
      "&issue=1&option_lang=rus&bookID=1621"


def main():
    main_page = html.fromstring(urllib.request.urlopen(URL).read())

    result = {}
    links = list(filter(lambda x: x.text is not None, main_page.xpath("//td//td//td//a[@class='SLink']")))
    for link in links:
        article_page = html.fromstring(urllib.request.urlopen(URL_BASE + link.get("href")).read())

        annotation = str.join('', article_page.xpath("//b[contains(text(), 'Аннотация')]/following-sibling::text()["
                                                     "not(preceding-sibling::b[contains(text(), 'Ключевые')])]"))
        keywords = re.split(", ", article_page.xpath("//b[contains(text(), 'Ключевые')]/following-sibling::i")[0].text)

        result[link.text] = [{'link': link.get("href")}, {'annotation': annotation}, {'keywords': keywords}]

    with open('result1.json', 'w') as outfile:
        json.dump(result, outfile, ensure_ascii=False)


main()
