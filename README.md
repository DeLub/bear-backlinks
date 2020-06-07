# bear-backlinks

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
