
# Using Discord as cloud storage
Discord is a popular social media application that gives users the ability to share files with other users. There is a file limit of 25MB for users who aren't subscribed to the service's subscription tier, dubbed Nitro. This program shows how a user can leverage Discord's file sharing abilities to turn a private server into a cloud storage provider with ease, complete with the ability to split files under the 25MB limit and stitch them back together again.

This is a proof of concept and should not be used as a legitimate replacement for Google Drive. Users should also not use this to store sensitive files.


## Deployment

To deploy this project you'll need to install the dependencies included in the requirements.txt file. Navigate to the folder in a terminal and run the following command.

```bash
  pip install -r requirements.txt
```

Replace the client token and the channel ID in app.py with your client token and your channel ID. If you don't have a Discord bot made and invited to a server already, you will need to do so.

Following that, run

```bash
  flask run
```

and navigate to the address in your web browser shown in the terminal. You can now upload files and they will appear in the private Discord server your bot has been invited to.
## Documentation
This program was written for an article on XDA-Developers by Adam Conway, Lead Technical Editor of the site.

[XDA-Developers article](https://www.xda-developers.com/discord-google-drive-cloud-storage/)

