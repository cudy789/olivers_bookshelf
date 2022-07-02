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
# file_name = '/key/client-key.json'
file_name = './key/client-key.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
client = gspread.authorize(creds)

sheets = {
    # "sheet_picture_books": client.open('Maddie\'s Classroom Library').worksheet("testsheet"), # the test sheet,
    # "sheet_chapter_books": client.open('Maddie\'s Chapter Books').worksheet("testsheet") # the test sheet
    "sheet_picture_books": client.open('Maddie\'s Classroom Library').worksheet("Sheet1"), # the actual sheet,
    "sheet_chapter_books": client.open('Maddie\'s Chapter Books').worksheet("Sheet1") # the actual sheet
}

print("Running app.py...")

def add_to_sheets(data: [], sheet):
    if data is not None:
        index = sheet_contains(data[-1], sheet)
        if index != False:
            print("found {} copies, adding 1".format(index))
            copies = int(sheet.cell(index, 5).value)
            sheet.update_cell(index, 5, copies + 1)
            return copies + 1
        else:
            data = data[:-1] + [""] + [data[-1]] + ["1"]
            print("did not find existing copies, going to append this row: {}".format(data))
            sheet.append_row(data)
            return 1

def sheet_contains(isbn, sheet):
    isbns = sheet.col_values(4)
    try:
        return isbns.index(isbn) + 1 # google sheets is 1 indexed
    except ValueError:
        return False


def sort_sheet(sheet):
    sheet.sort((1, 'asc'), range="A3:E{}".format(sheet.row_count))

    print("sorting sheet...")


def lookup_from_title_author(sheet):
    base_api_link = "https://www.googleapis.com/books/v1/volumes?q="

    title = sheet.col_values(1)[2:]
    author = sheet.col_values(2)[2:]

    # isbn_list = []

    count = 126

    for m_title, m_author in zip(title[123:], author[123]):
        request = base_api_link + m_title.replace(" ","-") + "+inauthor:" + m_author.replace(" ","-")
        print("looking for {} by {}".format(m_title, m_author))
        print("request: {}".format(request))
        with urllib.request.urlopen(request) as f:
            text = f.read()
        decoded_text = text.decode("utf-8")

        obj = json.loads(decoded_text) # deserializes decoded_text to a Python object
        if obj["totalItems"] == 0:
            # isbn_list.append("")
            print("no books found for {} by {}".format(m_title, m_author))
        else:
            volume_info = obj["items"][0]
            this_isbn = volume_info["volumeInfo"]["industryIdentifiers"][0]["identifier"]
            try:
                this_title = volume_info["volumeInfo"]["title"]
                print("title: {}".format(this_title))
                this_author = volume_info["volumeInfo"]["authors"][0]
                print("author: {}".format(this_author))
            except KeyError as e:
                print(e)

            print("ISBN: {}".format(this_isbn))
            sheet.update_cell(count, 4, this_isbn)
        print(count)
        count += 1

        # displays title, summary, author, domain, page count and language
        # print("\nTitle:", volume_info["volumeInfo"]["title"])

    # for index, this_isbn in enumerate(isbn_list):
    #     sheet.update_cell(index + 1, 4, this_isbn)


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
    lookup_only_selected = ""


    if request.method == 'POST':
        isbn_in=request.form.get("isbn-in")
        lookup_only = request.form.get("lookup_only")
        this_sheet = sheets[request.form.get("sheet_selected")]
        print(request.form.get("sheet_selected"))

        if request.form.get("sheet_selected") == "sheet_picture_books":
            picture_books_selected = "selected=\"selected\""
            chapter_books_selected = ""
        else:
            picture_books_selected = ""
            chapter_books_selected = "selected=\"selected\""
        if lookup_only == "on":
            print("Only performing lookup!")
            lookup_only_selected = "checked=\"checked\""
        else:
            lookup_only_selected = ""

        if request.form.get("submit_button") is None or request.form.get("submit_button") == "Submit":
            isbn_in = isbn_in.strip()
            if len(isbn_in) == 0:
                flash("No ISBN given")
                print("No ISBN given")
            else:
                if lookup_only == "on":
                    index = sheet_contains(isbn_in, this_sheet)
                    if index is not False:
                        flash("Found {} copies of {} in sheet {}".format(this_sheet.cell(index, 5).value, this_sheet.cell(index, 1).value, request.form.get("sheet_selected")))
                    else:
                        flash("No book found in sheet {}".format(request.form.get("sheet_selected")))
                else:
                    isbn_result = lookup_from_isbn(isbn_in)
                    if isbn_result is None:
                        flash("No book found for that ISBN!")
                    else:
                        copies = add_to_sheets(isbn_result + [isbn_in], this_sheet)
                        flash("Added book {}, you now have {} copies in {}".format(isbn_result[0], copies, request.form.get("sheet_selected")))
        elif request.form.get("submit_button") == "Sort Sheet":
            sort_sheet(this_sheet)
            flash("Sorted sheet {}".format(request.form.get("sheet_selected")))
        else:
            lookup_from_title_author(this_sheet)
            flash("Generated ISBNs for selected sheet")


    return render_template('home.html', picture_books_selected=picture_books_selected, chapter_books_selected=chapter_books_selected, lookup_only_selected=lookup_only_selected)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
