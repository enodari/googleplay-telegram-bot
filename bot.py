import telepot
import time

from googleplay.api import GooglePlayAPI

TELEGRAM_TOKEN = ""

ANDROID_ID = ""
GOOGLE_USER = ""
GOOGLE_PWD = ""
GOOGLE_TOKEN = None


def sizeof_fmt(size):
    """
    Get human readable version of file size
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f%s" % (size, x)
        size /= 1024.0


class GooglePlayBot(telepot.Bot):
    def handle(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type == 'text':
            text = msg['text']

            if text.startswith('/download'):
                try:
                    command, package = text.split(' ')
                    filename = "{}.apk".format(package)
                except ValueError:
                    msg = "Package name malformed or missing"
                    return self.sendMessage(chat_id, msg)

                # Init API and log in
                api = GooglePlayAPI(ANDROID_ID)
                logged = api.login(GOOGLE_USER, GOOGLE_PWD, GOOGLE_TOKEN)
                if not logged:
                    msg = "Login error, check your credentials"
                    return self.sendMessage(chat_id, msg)

                # Get version code and offer type from the app details
                doc = api.details(package).docV2
                version = doc.details.appDetails.versionCode
                if not doc.offer:
                    msg = "Package not found, check for typos"
                    return self.sendMessage(chat_id, msg)

                offer = doc.offer[0].offerType

                try:
                    # Download
                    size = sizeof_fmt(doc.details.appDetails.installationSize)
                    msg = "Downloading: {}\nSize: {}".format(doc.title, size)
                    self.sendMessage(chat_id, msg)

                    # Upload
                    data = api.download(package, version, offer)
                    open(filename, "wb").write(data)
                    self.sendMessage(chat_id, "Done, sending..")
                    self.sendDocument(chat_id, open(filename, 'rb'))

                except Exception:
                    self.sendMessage(chat_id, "Error, retry")


bot = GooglePlayBot(TELEGRAM_TOKEN)
bot.message_loop()

# Keep the bot running.
while 1:
    time.sleep(10)
