'''
# Bear backlinks

This script loops through all notes in your bear database and checks which
other notes reference it. The notes referencing this note are listed under
`## Backlinks`. Each run replaces all backlinks already present in the note.

I believe looping through all notes is necessary to account for links that have
been removed. I have not tested how well this works on large collections of
notes.

This script does not update the notes directly in the database. It only reads
the notes and the links from your database, and uses Bear's x-callback-url to
update the note text.

Change the `backlinks_header` to the name of the section you want to use.

This script can be used with the standard Python 2.7 on macOS.
'''

backlinks_header = '\n---\n## Backlinks'

import sqlite3
import subprocess
import urllib
import os
import time
import json

HOME = os.getenv('HOME', '')
bear_db = os.path.join(HOME, 'Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite')

def main():
    notes = get_all_notes()

    for note in notes:
        # Split Note text from backlinks
        note_text = note['Text'].split(backlinks_header)[0]
        backlinks = backlinks_header

        # Get notes this note is referenced by
        linked_by_notes = get_notes_linking_to(note['ID'])

        for linked_by_note in linked_by_notes:
            lb_note_text = linked_by_note['Text'].split(backlinks_header)[0]
            if ('[[' + note['Title'] + ']]') in lb_note_text:
                # Add backlink
                backlinks += "\n* [[" + linked_by_note['Title'] + "]]"

        note_text += backlinks
        update_note(note['UID'], note_text)

def get_all_notes():
    with sqlite3.connect(bear_db) as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT TNote.Z_PK              AS ID\
                      , TNote.ZUNIQUEIDENTIFIER AS UID\
                      , TNote.ZTITLE            AS Title\
                      , TNote.ZTEXT             AS Text\
                   FROM ZSFNOTE                 AS TNote\
                  WHERE TNote.ZTRASHED = 0"
        return conn.execute(query)

def get_notes_linking_to(id):
    with sqlite3.connect(bear_db) as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT DISTINCT\
                        SNote.Z_PK              AS ID\
                      , SNote.ZUNIQUEIDENTIFIER AS UID\
                      , SNote.ZTITLE            AS Title\
                      , SNote.ZTEXT             AS Text\
                   FROM Z_7LINKEDNOTES          AS Source\
                      , ZSFNOTE                 AS SNote\
                  WHERE Source.Z_7LINKEDNOTES = %i\
                    AND SNote.Z_PK            = Source.Z_7LINKEDBYNOTES\
                    AND SNote.ZTRASHED        = 0\
               ORDER BY SNote.ZCREATIONDATE ASC" % id
        return conn.execute(query)

def update_note(uid, new_text):
    x_command = 'bear://x-callback-url/add-text?id=' + uid +'&mode=replace_all&open_note=no&exclude_trashed=no&new_window=no&show_window=no&edit=no&timestamp=no'
    x_callback(x_command, new_text)

def x_callback(x_command, md_text):
    x_command_text = x_command + '&text=' + urllib.quote(md_text.encode('utf8'))
    subprocess.call(["open", "-g", x_command_text])
    time.sleep(.2)

if __name__ == '__main__':
    main()
