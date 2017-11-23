import requests
import datetime
import json
from dashboard import fetchBlogVulns, fetchSocialVulns

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot" + token + "/"

    def get_updates(self):
        method = 'getUpdates'
        resp = requests.get(self.api_url + method)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
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
                    
    def catchHook(self,post):
        jsonResponse = json.loads(post.decode('utf-8'))
        message = jsonResponse['message']['text']
        chatid = jsonResponse['message']['chat']['id']
        print (str(chatid) + ":" + message)

        if (message == "/start"):
            self.send_message(chatid,"Hello! I'm SecurityDashboardBot! Please to meet you!")
        if (message == "/help"):
            self.send_message(chatid,"*** HELP ***\n/last: returns last 5 vulnerabilities\n/lastblog: returns last 5 vulnerabilities from blogs/forum\n/lastsocial: returns last 5 vulnerabilities from socialnetworks\n")
        if (message == "/last"):
            self.send_message(chatid,"*** Last vulnerabilities ***\nWork in progress!\nYabba dabba fuffa fuffa!\n")
        if (message == "/lastblog"):
            self.send_message(chatid,"*** Last vulnerabilities from sites ***\n")
            vulns=dashboard.fetchBlogVulns(5)
            for vuln in vulns:
                message = "(" + vuln['date'].strftime('%d, %b %Y') + ") " + vuln['name'][0] + " - " + vuln['cve'] + " (Score:" + vuln['score'] +  ") <a href='" +  vuln['name'][1] + "'>View</a>"
        if (message == "/lastsocial"):
            self.send_message(chatid,"*** Last vulnerabilities from socialnetworks***\nWork in progress!\nYabba dabba fuffa fuffa!\n")

        
        return "done"
    def registerHook(self):
        WEBHOOK_URL = 'https://securitydash.herokuapp.com/API/EaSKhyGzXU/telegram-hook'
        result_json = ""
        #remove previous webhook
        method = "deleteWebhook"
        resp = requests.post(self.api_url + method)
        result_json = result_json + resp.json()['description'] + " "
        
        method = 'setWebhook'
        params = {'url': WEBHOOK_URL}
        resp = requests.post(self.api_url + method, params)
        result_json = result_json + resp.json()['description']
        
        return result_json
       
#secbot = BotHandler("351082352:AAHLBZW4ObbsMVHh4lrcwZOVHmvKsfyM59E")
#secbot.check_new_subscriptors()
