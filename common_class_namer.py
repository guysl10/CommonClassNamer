# Author: Guy Salomon

import requests
from typing import List, Dict

import re
from bs4 import BeautifulSoup
import xmltodict
from loguru import logger
import asyncio

CLASS_NAMER = "https://www.classnamer.org/"


def _safe_get_request(url: str = CLASS_NAMER):
    """Send get request and print warning log if response is not 200."""
    response = requests.get(url)
    if response.status_code != 200:
        logger.warning(f"{response.status_code} - {response.content}")
    return response


def _extract_html_data(response, tag_type: str, id_name: str):
    """
    Extract tag data from http request response.

    :param response: Get response variable.
    :param tag_type: Name of the tag.
    :param id_name: ID name to extract from the tag.
    """
    data_response = response.content.decode("utf-8")
    parser = BeautifulSoup(data_response, "html.parser")
    return parser.find(tag_type, {"id": id_name})


def request_new_class_name() -> List[str]:
    """Get new class name from specific ClassNamer website."""
    response = _safe_get_request(CLASS_NAMER)
    class_name = _extract_html_data(response, "p", "classname")

    # Extract just the class name content from the <p> tag.
    class_name_data = xmltodict.parse(str(class_name))["p"]["#text"]
    # Split words by capital letters.
    class_name_words = re.sub(r"([A-Z])", r" \1", class_name_data).split()

    return class_name_words


def get_words_occurrence_count(repeated_words: List[List[str]]
                               ) -> Dict[str, int]:
    """
    Count the occurrence of each word.

    :return: Dictionary of all words occurrence.
    """
    flat_list_of_words = [item for word in repeated_words for item in word]
    words_occurrence_count = {}
    for word in flat_list_of_words:
        if word in words_occurrence_count:
            words_occurrence_count[word] += 1
        else:
            words_occurrence_count[word] = 1

    return words_occurrence_count


async def get_n_class_names(n: int) -> List[List[str]]:
    """Get asynchronously n new class names."""
    tasks = []
    loop = asyncio.get_event_loop()

    for i in range(n):
        tasks.append(loop.run_in_executor(None, request_new_class_name))

    words = await asyncio.gather(*tasks, return_exceptions=True)
    return words


async def print_occurrence_of_n_class_names(n: int = 10):
    """Print the occurrence of n class names."""
    words = await get_n_class_names(n)
    n_class_names = get_words_occurrence_count(words)
    print(n_class_names)


def main():
    asyncio.run(print_occurrence_of_n_class_names())


if __name__ == '__main__':
    main()
