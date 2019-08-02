import postmark.config
from postmarker.core import PostmarkClient


POSTMARK_TOKEN = postmark.config.postmark_info["token"]

postmark = PostmarkClient(server_token = POSTMARK_TOKEN)


postmark.emails.send(From='a@precisioncorp.net', To='andrew.sheinberg@gmail.com', Cc = None, Bcc = None, Subject='Test email account', HtmlBody= 'Does it work sending from any user on the domain @precisioncorp.net')