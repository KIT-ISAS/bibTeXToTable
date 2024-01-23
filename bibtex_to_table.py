# -*- coding: utf-8 -*-
# Author contact: Florian Pfaff pfaff@kit.edu

import argparse
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import codecs


def load_bibtex_file(input_file):
    with open(input_file, encoding='utf-8') as bibtex_file:
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
    return bib_database


def verify_name_in_authors(full_name, authors, title):
    last_name = full_name.split()[-1]  # Extract the last name from the full name
    if last_name in authors and full_name not in authors:
        raise NameError(f"Name {last_name} faulty in entry {title}")


def write_entry(entry, output_file, full_name_to_verify):
    if "author" in entry.keys():
        authors = entry["author"]
    elif "editor" in entry.keys():
        # Use editor instead of author if is no author is available
        authors = entry["editor"] + " (Eds.)"
    else:  # Entry has neither author nor editor, this must not happen
        raise ValueError("Entry has neither author nor editor: " + entry["title"])

    title = entry["title"]

    if full_name_to_verify:
        verify_name_in_authors(full_name_to_verify, authors, title)

    if "booktitle" not in entry.keys():
        if "journal" not in entry.keys():
            booktitle = "none"
        else:
            booktitle = entry["journal"]
    else:
        booktitle = entry["booktitle"]

    tmpwriter = BibTexWriter()
    tmpDatabase = BibDatabase()
    tmpDatabase.entries.append(entry)
    bibtex = tmpwriter.write(tmpDatabase)

    submission_type = entry["ENTRYTYPE"]
    pubid = entry["ID"]

    # Properly set en and em dashes
    title = title.replace("---", "\u2014")
    title = title.replace("--", "\u2013")
    title = title.replace("~", " ")
    booktitle = booktitle.replace("---", "\u2014")
    booktitle = booktitle.replace("--", "\u2013")
    booktitle = booktitle.replace("~", " ")

    supported_for_balken = [
        "preprint",
        "article",
        "inproceedings",
        "inbook",
        "incollection",
        "book",
        "proceedings",
        "phdthesis",
    ]
    authors = authors.replace(" and ", ", ")
    if submission_type not in supported_for_balken:
        submission_type = "other"
    elif "arXiv" in booktitle:
        submission_type = "preprint"
    output_file.write(
        '<tr id="'
        + pubid
        + '" class="entry">\n<td><div class="balken-'
        + submission_type
        + '"></div>\n</td>\n'
    )
    output_file.write("<td> <i>" + authors + "</i>,</br> <b>" + title + "</b>,</br>")
    if not booktitle == "none":
        output_file.write(booktitle + ", ")
    if (
        "pages" in entry.keys()
        and "volume" in entry.keys()
        and "number" in entry.keys()
    ):
        output_file.write(
            entry["volume"]
            + "("
            + entry["number"]
            + "):"
            + (entry["pages"].replace("--", "\u2013")).replace("-", "\u2013")
            + ", "
        )
    elif "pages" in entry.keys() and "volume" in entry.keys():
        output_file.write(
            entry["volume"]
            + ":"
            + (entry["pages"].replace("--", "\u2013")).replace("-", "\u2013")
            + ", "
        )
    elif "pages" in entry.keys():
        output_file.write(
            "pp. "
            + (entry["pages"].replace("--", "\u2013")).replace("-", "\u2013")
            + ", "
        )

    if "publisher" in entry.keys():
        output_file.write(entry["publisher"] + ", ")
    if "address" in entry.keys():
        output_file.write(entry["address"] + ", ")

    if "series" in entry.keys():
        output_file.write(entry["series"] + ", ")

    if "month" in entry.keys():
        output_file.write(entry["month"] + ", ")
    output_file.write(str(entry["year"]))
    output_file.write(".\n")
    output_file.write(
        '<p class="infolinks"> <a href="javascript:toggleInfo(\''
        + pubid
        + '\',\'bibtex\')"><img src="https://isas.iar.kit.edu/img/BibTeX.png" alt="BibTeX" /></a>'
    )
    if "pdf" in entry.keys():
        output_file.write(
            ' <a href="https://isas.iar.kit.edu/pdf/'
            + entry["pdf"]
            + '" target="_blank"><img src="https://isas.iar.kit.edu/img/PDF.png" alt="PDF" /></a>'
        )
    if "url" in entry.keys():
        output_file.write(' <a href="' + entry["url"] + '" target="_blank">URL</a>')
    if "annote" in entry.keys():
        output_file.write(' <font color="red">' + entry["annote"] + "</font>")
    output_file.write("</p>\n</td>\n</tr>\n")
    output_file.write(
        '<tr id="bib_'
        + pubid
        + '" class="bibtex noshow"><td></td>\n<td><b>BibTeX</b>:\n<pre>\n'
    )
    output_file.write(bibtex)
    output_file.write("\n</pre>\n</td>\n</tr>\n\n")


def write_output(bib_database, output_filename, full_name_to_verify=None):
    output_file = codecs.open(output_filename, "w", "utf-8")
    allMonths = ["none", "December", "November", "October", "September", "August",
                 "July", "June", "May", "April", "March", "February", "January"]
    output_file.write('<table id="qs_table" border="1"><tbody>\n')
    
    # Determine relevant years
    allYears = {entry["year"] for entry in bib_database.entries}
    for year in sorted(
        list(allYears), reverse=True
    ):  # Iterate over years in ascending order
        output_file.write(
            '<tr class="year"><td></td><td><a name="'
            + str(year)
            + '"></a>'
            + str(year)
            + "</td></tr>\n"
        )

        entries_of_year = [
            entry for entry in bib_database.entries if entry["year"] == str(year)
        ]

        for month in allMonths:
            for entry in entries_of_year:
                if "month" not in entry.keys():
                    month_of_entry = "none"  # Ones without month are printed first. To change this, change allMonths above
                else:
                    month_of_entry = entry["month"]
                if not month_of_entry == month:
                    continue  # Entry currently irrelevant
                write_entry(entry, output_file, full_name_to_verify)

    output_file.write("</tbody></table>")
    output_file.close()


def main(input_file, output_file, full_name_to_verify=None):
    bib_database = load_bibtex_file(input_file)
    write_output(bib_database, output_file, full_name_to_verify)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process BibTeX files.")
    parser.add_argument("input_file", type=str, help="Path to the input BibTeX file.")
    parser.add_argument("output_file", type=str, help="Path to the output HTML table file.")
    parser.add_argument("--verify-name", type=str, help="Full name to verify in the authors list.", default=None)
    args = parser.parse_args()
    
    main(args.input_file, args.output_file, args.verify_name)
