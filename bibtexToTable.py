# -*- coding: utf-8 -*-
# Author: Florian Pfaff
# Author contact: pfaff@kit.edu

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import codecs

with open('/localhome/isaswebwiki/ISASPublikationen/ISASFused.bib') as bibtex_file:
    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode
    bib_database = bibtexparser.load(bibtex_file, parser=parser)

allMonths=["none","December","November","October","September","August","July","June","May","April","March","February","January"]

outputFile=codecs.open("/localhome/isaswebwiki/isas.iar.kit.edu/publications.table","w", "utf-8")
outputFile.write('<table id="qs_table" border="1"><tbody>\n')

supportedForBalken=["preprint","article","inproceedings","inbook","incollection","book","proceedings","phdthesis"]

def writeEntry(entry):
    if "author" in entry.keys():
        authors=entry["author"]
    elif "editor" in entry.keys(): # Use editor instead of author if is no auther is available
        authors=entry["editor"]+' (Eds.)'
    else: # Entry has neither author nor editor, this must not happen
        raise
    
    title=entry["title"]

    if "Hanebeck" in authors and not "Uwe D. Hanebeck" in authors:
        raise NameError("Name Hanebeck faulty in entry " + title)

    if not "booktitle" in entry.keys():
        if not "journal" in entry.keys():
            booktitle="none"
        else:
            booktitle=entry["journal"]
    else:
        booktitle=entry["booktitle"]
        
    
    tmpwriter=BibTexWriter()
    tmpDatabase=BibDatabase()
    tmpDatabase.entries.append(entry)
    bibtex=tmpwriter.write(tmpDatabase)
    
    submissionType=entry["ENTRYTYPE"]
    pubid=entry["ID"]
    
    # Properly set en and em dashes
    title=title.replace('---',u'\u2014')
    title=title.replace('--',u'\u2013')
    title=title.replace('~',' ')
    booktitle=booktitle.replace('---',u'\u2014')
    booktitle=booktitle.replace('--',u'\u2013')
    booktitle=booktitle.replace('~',' ')
    

    authors=authors.replace(' and ',', ')
    if not submissionType in supportedForBalken:
        submissionType="other"
    elif "arXiv" in booktitle:
        submissionType="preprint"
    outputFile.write('<tr id="'+pubid+'" class="entry">\n<td><div class="balken-'+submissionType+'"></div>\n</td>\n')
    outputFile.write(u'<td> <i>'+authors+u'</i>,</br> <b>'+title+u'</b>,</br>')
    if not booktitle=='none':
        outputFile.write(booktitle+u', ')
    if "pages" in entry.keys() and "volume" in entry.keys() and "number" in entry.keys():
        outputFile.write(entry["volume"]+u'('+entry["number"]+u'):'+(entry["pages"].replace("--",u'\u2013')).replace("-",u'\u2013')+u', ') 
    elif "pages" in entry.keys() and "volume" in entry.keys():
        outputFile.write(entry["volume"]+u':'+(entry["pages"].replace("--",u'\u2013')).replace("-",u'\u2013')+u', ') 
    elif "pages" in entry.keys():
        outputFile.write(u'pp. '+(entry["pages"].replace("--",u'\u2013')).replace("-",u'\u2013')+u', ')
        
    if "publisher" in entry.keys():
        outputFile.write(entry["publisher"]+', ')
    if "address" in entry.keys():
        outputFile.write(entry["address"]+', ')
            
    if not month=='none':
        outputFile.write(month+', ')
    outputFile.write(str(entry["year"])+'.\n')
    outputFile.write('<p class="infolinks"> <a href="javascript:toggleInfo(\''+pubid+'\',\'bibtex\')"><img src="https://isas.iar.kit.edu/img/BibTeX.png" alt="BibTeX" /></a>')
    if "pdf" in entry.keys():
        outputFile.write(' <a href="https://isas.iar.kit.edu/pdf/'+entry["pdf"]+'" target="_blank"><img src="https://isas.iar.kit.edu/img/PDF.png" alt="PDF" /></a>')
    if "url" in entry.keys() and (not "pdf" in entry.keys() or submissionType == "article"):
        outputFile.write(' <a href="'+entry["url"]+'" target="_blank">URL</a>')
    if "annote" in entry.keys():
        outputFile.write(' <font color="red">'+entry["annote"]+'</font>')
    outputFile.write('</p>\n</td>\n</tr>\n')
    outputFile.write('<tr id="bib_'+pubid+'" class="bibtex noshow"><td></td>\n<td><b>BibTeX</b>:\n<pre>\n')
    outputFile.write(bibtex)
    outputFile.write('\n</pre>\n</td>\n</tr>\n\n')

# Determine relevant years
allYears=set([entry["year"] for entry in bib_database.entries])
for year in sorted(list(allYears),reverse=True): # Iterate over years in ascending order
    outputFile.write('<tr class="year"><td></td><td><a name="'+str(year)+'"></a>'+str(year)+'</td></tr>\n')

    entriesOfYear=[entry for entry in bib_database.entries if entry["year"]==str(year)]

    for month in allMonths:
        for entry in entriesOfYear:
            if not "month" in entry.keys():
                monthOfEntry="none" # Ones without month are printed first. To change this, change allMonths above
            else:
                monthOfEntry=entry["month"]
            if not monthOfEntry==month:
                continue # Entry currently irrelevant
            writeEntry(entry)


outputFile.write('</tbody></table>')
outputFile.close()