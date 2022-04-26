from random import randint
from time import strftime
from flask import Flask, render_template, flash, request

DEBUG = True
app = Flask(__name__)
app.secret_key = b'_5#y2Ljfaj^&T(fas)#(FAj;asfjpp180s.fas"F4Q8z\n\xec]/'

import urllib.request
import json
import textwrap

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
#Authorize the API
scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
    ]
file_name = '/key/client-key.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
client = gspread.authorize(creds)

sheets = {
    # "sheet_picture_books": client.open('Maddie\'s Classroom Library').worksheet("testsheet"), # the test sheet,
    # "sheet_chapter_books": client.open('Maddie\'s Chapter Books').worksheet("testsheet") # the test sheet
    "sheet_picture_books": client.open('Maddie\'s Classroom Library').worksheet("Sheet1"), # the actual sheet,
    "sheet_chapter_books": client.open('Maddie\'s Chapter Books').worksheet("Sheet1") # the actual sheet
}


def add_to_sheets(data: [], sheet):
    if data is not None:
        sheet.append_row(data)

def sort_sheet(sheet):
    sheet.sort((1, 'asc'), range="A3:C{}".format(sheet.row_count))
    print("sorting sheet...")


def lookup_from_isbn(user_input):

    base_api_link = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
    # user_input = input("Enter ISBN or press CTRL-C to exit: ").strip()

    with urllib.request.urlopen(base_api_link + user_input) as f:
        text = f.read()

    decoded_text = text.decode("utf-8")
    print(decoded_text)
    obj = json.loads(decoded_text) # deserializes decoded_text to a Python object
    if obj["totalItems"] == 0:
        print("No book found for that ISBN!")
        return None
    volume_info = obj["items"][0]
    authors = obj["items"][0]["volumeInfo"]["authors"]

    # displays title, summary, author, domain, page count and language
    print("\nTitle:", volume_info["volumeInfo"]["title"])
    print("\nSummary:\n")
    print(textwrap.fill(volume_info["searchInfo"]["textSnippet"], width=65))
    print("\nAuthor(s):", ",".join(authors))
    # print("\nPublic Domain:", volume_info["accessInfo"]["publicDomain"])
    # print("\nPage count:", volume_info["volumeInfo"]["pageCount"])
    # print("\nLanguage:", volume_info["volumeInfo"]["language"])
    print("\n***")
    return [volume_info["volumeInfo"]["title"]] + obj["items"][0]["volumeInfo"]["authors"]


@app.route("/", methods=['GET', 'POST'])
def main():
    picture_books_selected = "selected=\"selected\""
    chapter_books_selected = ""


    if request.method == 'POST':
        isbn_in=request.form.get("isbn-in")
        this_sheet = sheets[request.form.get("sheet_selected")]
        print(request.form.get("sheet_selected"))

        if request.form.get("sheet_selected") == "sheet_picture_books":
            picture_books_selected = "selected=\"selected\""
            chapter_books_selected = ""
        else:
            picture_books_selected = ""
            chapter_books_selected = "selected=\"selected\""

        if request.form.get("submit_button") is None or request.form.get("submit_button") == "Submit":
            if len(isbn_in) == 0:
                flash("No ISBN given")
                print("No ISBN given")
            else:
                isbn_result = lookup_from_isbn(isbn_in)
                if isbn_result is None:
                    flash("No book found for that ISBN!")
                else:
                    add_to_sheets(isbn_result, this_sheet)
                    flash("Added book {} to sheet {}".format(isbn_result, request.form.get("sheet_selected")))
        else:
            sort_sheet(this_sheet)
            flash("Sorted sheet {}".format(request.form.get("sheet_selected")))



    return render_template('home.html', picture_books_selected=picture_books_selected, chapter_books_selected=chapter_books_selected)


if __name__ == "__main__":
    app.run(host="0.0.0.0")