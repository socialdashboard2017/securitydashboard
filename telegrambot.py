import requests
import datetime
import json

from models import subscriptors

#from dashboard import fetchBlogVulns, fetchSocialVulns

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot" + token + "/"

    def get_updates(self):
        method = 'getUpdates'
        resp = requests.get(self.api_url + method)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text, disable_preview="false"):
        params = {'chat_id': chat_id, 'text': text, 'disable_web_page_preview' : disable_preview }
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = get_result[len(get_result)]
            return last_update

    def push_update(self,message):
        with open("subscriptors.txt", "r") as file:
            for line in file:
                self.send_message(line,message)

    def check_new_subscriptors(self):
        updates = self.get_updates()
        for update in updates:
            chatid=str(update['message']['chat']['id'])
            with open("subscriptors.txt", "r+") as file:
                for line in file:
                    if chatid in line:
                        break
                else: # not found, we are at the eof
                    print (chatid)
                    file.write (chatid+"\n") # append missing data
                    
    def formatMessage(self, vuln):
        message = "Date: " + vuln['date'].strftime('%d, %b %Y') + "\nCVE: " + vuln['cve'] + "\nScore: " +  vuln['score'] + "\nDescription: " + vuln['name'][0] + "\nLink: " + vuln['name'][1]  
        return message
        
        
    def catchHook(self,post,db):
        jsonResponse = json.loads(post.decode('utf-8'))
        message = jsonResponse['message']['text']
        chatid = jsonResponse['message']['chat']['id']
        print (str(chatid) + ":" + message)

        if (message == "/start"):
            self.send_message(chatid,"Hello! I'm SecurityDashboardBot! Please to meet you!\nUse /help command for command list")
        if (message == "/help"):
            self.send_message(chatid,""" 
*** HELP ***
/last: returns last 5 vulnerabilities
/lastblog: returns last 5 vulnerabilities from blogs/forum
/lastsocial: returns last 5 vulnerabilities from socialnetworks
/subscribe: register your ID in order to receive push notification in case of critical vulnerability
/unsubscribe: remove your subscription
************
            """)
        if (message == "/last"):
            from dashboard import fetchallvulns
            vulns=fetchallvulns(db)
            del vulns[5:]
            for vuln in vulns:
                self.send_message(chatid,self.formatMessage(vuln),disable_preview="true")
        if (message == "/lastblog"):
            self.send_message(chatid,"*** Last vulnerabilities from Forums and Blogs ***\n")
            from dashboard import fetchBlogVulns
            vulns=fetchBlogVulns(db,5)
            for vuln in vulns:
                self.send_message(chatid,self.formatMessage(vuln),disable_preview="true")
        if (message == "/lastsocial"):
            self.send_message(chatid,"*** Last vulnerabilities from SocialNetworks***\n")
            from dashboard import fetchSocialVulns
            vulns=fetchSocialVulns(db,5)
            for vuln in vulns:
                self.send_message(chatid,self.formatMessage(vuln),disable_preview="true")
        if (message == "/subscribe"):
            subs_object = subscriptors(name = "Uhmmm", chat_id = chatid, push = True)
            exists = db.session.query(subscriptors).filter_by(chat_id = str(chatid)).first() is not None
            if exists == False:
                db.session.add(subs_object)
                db.session.commit()
            self.send_message(chatid,"You are subscribed!")           
        if (message == "/unsubscribe"):
            self.send_message(chatid,"You are unsubscribed!")            
        return "done"
    def registerHook(self):
        WEBHOOK_URL = 'https://securitydash.herokuapp.com/API/EaSKhyGzXU/telegram-hook'
        result_json = ""
        #remove previous webhook
        method = "deleteWebhook"
        resp = requests.post(self.api_url + method)
        result_json = result_json + resp.json()['description'] + " "
        #set webhook
        method = 'setWebhook'
        params = {'url': WEBHOOK_URL}
        resp = requests.post(self.api_url + method, params)
        result_json = result_json + resp.json()['description']
        
        return result_json
       
