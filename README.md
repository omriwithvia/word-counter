# word-counter

To be run with Python 2.7, after you did `pip install -r requirements.txt`.
Assuming you have mysql server running, and you ran `create_db.sql` before running the app.

To run the app just run `python main.py`.

Assuming counts are not case sensitive.<br/>
Assuming words are <200 characters in length.<br/>
Assuming if MySQL won't do with performance I could switch to something else. I have AeroSpike in mind but others would do too, I guess.

API doc:

<b>/counter</b><br/>
Request:<br/>
{"sentence": "some words appear here"}<br/>
{"filename": "/home/omri/Documents/www.txt"}<br/>
{"url": "http://www.lemonade.com/textfile.txt"}<br/>

Response:
{"success": true}

<b>/stats</b><br/>
Request:<br/>
{"word_value": "someword"}

Response:<br/>
{"count": 1235}