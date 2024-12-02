import requests
from bs4 import BeautifulSoup
import json
import os
from postmarker.core import PostmarkClient


def get_html(url):
    response = requests.get(url)
    return response.text


def get_interval_url(html):
    soup = BeautifulSoup(html, "lxml")

    # Find the h2 that contains intervals and return its parent a tag
    title = [
        title for title in soup.find_all("h2") if "intervals" in title.text.lower()
    ]
    # now find the a href parent tag of the title

    if title:
        interval_url = title[0].find_parent("a").get("href")

    return interval_url


def get_interval_data(html):
    soup = BeautifulSoup(html, "lxml")
    session = {}

    # Get the date by finding the first p element that also contains <i> tag
    session["date"] = soup.find("p").get_text()
    session["content"] = soup.find("div", class_="content")

    return session


def send_email(data):
    postmark = PostmarkClient(server_token="d99f61fd-5670-4571-8161-87cfab849886")
    postmark.emails.send(
        From="dave@dwedigital.com",
        To="dave@dwedigital.com",
        Subject="This Week's Interval Session",
        HtmlBody="<p>This week's interval session</p> <p>Date: {date}</p> <p>{content}</p>".format(
            **data
        ),
    )
    print("Email sent")


def write_to_json(data):
    # Extract the text for JSON
    data["content"] = data["content"].get_text()

    # if file exists, load it and append to it
    if os.path.exists("interval_sessions.json"):
        with open("interval_sessions.json", "r") as file:
            old_data = json.load(file)
            if data["date"] not in [d["date"] for d in old_data]:
                old_data.append(data)
        with open("interval_sessions.json", "w") as file:
            json.dump(old_data, file, indent=4)
    else:

        with open("interval_sessions.json", "w") as file:
            json.dump([data], file, indent=4)


# Helper function for local testing
def local_file(path):
    with open(path) as file:
        return file.read()


def format_content(content):
    content.replace("\t", "")
    return content


if __name__ == "__main__":

    interval_url = get_interval_url(get_html("https://www.rocknroadrunners.je/events/"))
    data = get_interval_data(
        get_html("https://www.rocknroadrunners.je{}".format(interval_url))
    )
    send_email(data)
    write_to_json(data)
