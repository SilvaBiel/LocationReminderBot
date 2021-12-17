# LocationReminderBot

LocationReminderBot - is a task manager type of bot, where you can specify the location in which task must be done
and location radius of this task. Bot works with PostgreSQL and SQLAlchemy as ORM to store data. 
Then user start live location sharing with the bot and after entering into this location address in a specified radius, 
the user will receive notification, that in this place there is a task.

# Usage
To start working with a bot, press /start in chat, the bot will welcome you and return the available commands message.
This commands also awailable with /help:

<p align="center">
  <img src="https://raw.githubusercontent.com/golubevcg/LocationReminderBot/master/readmeImages/bot_start_and_help.png"/>
</p>

# Task adding
For sake of example let's add some simple tasks, by entering /add_task command. 
You need to enter task header and body:

<p align="center">
  <img src="https://raw.githubusercontent.com/golubevcg/LocationReminderBot/master/readmeImages/add_task_0.png"/>
</p>

After this, you can either enter task location or skip this part, if you will skip it -> task will be immediately saved.
We will add a location for our task by entering /location in chat.

There are two ways to add location - by location name or coordinates. Both ways will result in the bot asking you
to confirm the location which he founded by the user given address (if you will press /no you can again enter location):

<p align="center">
  <img src="https://raw.githubusercontent.com/golubevcg/LocationReminderBot/master/readmeImages/add_task_1.png"/>
</p>

By default task radius will be 1000 meters,if you need to edit this value, you can do this by editing the task.
We going to stick with a default value.

Great! Task has been successfully added. Now we can start the location sharing period.
After entering location area, bot will notify us,that in place we entered there is a task for us to do:

<p align="center">
  <img src="https://raw.githubusercontent.com/golubevcg/LocationReminderBot/master/readmeImages/entered_task_area.png"/>
</p>

Unfortunately, for the date of creation telegram bot does not supports always location sharing. 
So maximum location sharing period currently is 8 hours. Bot inside have notificator, 
which notify user, if live location period is over:

<p align="center">
  <img src="https://raw.githubusercontent.com/golubevcg/LocationReminderBot/master/readmeImages/live_location_over.png"/>
</p>

with /get_active_tasks command you can retrieve all active tasks.
It will return a single message for each active task you have:

<p align="center">
  <img src="https://raw.githubusercontent.com/golubevcg/LocationReminderBot/master/readmeImages/get_active_tasks.png"/>
</p>

If you need to edit or delete your tasks, you can do this with /edit_task id command or /delete_task id, 
where #id is the id of a task, which you can see with /get_active_task command

<p align="center">
  <img src="https://raw.githubusercontent.com/golubevcg/LocationReminderBot/master/readmeImages/task_deleting.png"/>
</p>

to see all awailable commands, you can enter /help command, will show possible options:

<p align="center">
  <img src="https://raw.githubusercontent.com/golubevcg/LocationReminderBot/master/readmeImages/help.png"/>
</p>
