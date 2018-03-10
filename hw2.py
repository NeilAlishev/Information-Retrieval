import re
import json
from lxml import html
import urllib.request

from search_course.porter_stemmer import Porter
from pymystem3 import Mystem

URL_BASE = "http://www.mathnet.ru"

URL = "http://www.mathnet.ru/php/archive.phtml?jrnid=uzku&wshow=issue&bshow=contents&series=0&year=2016&volume=158" \
      "&issue=1&option_lang=rus&bookID=1621"

MYSTEM_INSTANCE = Mystem()


def _stem_each_porter(text):
    # remove all non-letter characters
    text = re.sub(r'\W+', ' ', text)

    text = list(filter(None, re.split(" ", text)))

    stemmed_words = []
    for word in text:
        try:
            stemmed_words.append(Porter.stem(word))
        except AttributeError:
            stemmed_words.append(word)

    return str.join(" ", stemmed_words)


def _mystem(text):
    return re.sub('[^\w ]+', '', ''.join(MYSTEM_INSTANCE.lemmatize(text)).strip())


def main():
    main_page = html.fromstring(urllib.request.urlopen(URL).read())

    result = {}
    links = list(filter(lambda x: x.text is not None, main_page.xpath("//td//td//td//a[@class='SLink']")))
    for link in links:
        article_page = html.fromstring(urllib.request.urlopen(URL_BASE + link.get("href")).read())

        annotation = str.join('', article_page.xpath("//b[contains(text(), 'Аннотация')]/following-sibling::text()["
                                                     "not(preceding-sibling::b[contains(text(), 'Ключевые')])]"))
        keywords = re.split(", ", article_page.xpath("//b[contains(text(), 'Ключевые')]/following-sibling::i")[0].text)

        annotation = annotation.strip()
        result[link.text] = [
            {'stemmedTitle': [{'porter': _stem_each_porter(link.text)}, {'mystem': _mystem(link.text)}]},
            {'link': URL_BASE + link.get("href")},
            {'annotation': [{'original': annotation}, {'porter': _stem_each_porter(annotation)},
                            {'mystem': _mystem(annotation)}]}, {'keywords': keywords}]

    with open('result2.json', 'w') as outfile:
        json.dump(result, outfile, ensure_ascii=False)


main()
