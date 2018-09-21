################################
##         thunder.py         ##
##   (A remake of racistlib)  ##
################################

__Developer__ = "Thunder"
__Version__ = 0.1
__Date__ = "September 12, 2018"
__Description__ = "A futuristic simplistic stable chatango library"

import socket
import time
import re
import select
import threading
import random
import requests
import queue

#imports of thunder dependencies
import pm
import chat
import connections
import utility
  
class Object(object):
    def __init__(self, **stuff):
       for x in stuff:
              setattr(self, x, stuff[x])
       self.ret()

    def ret(self): 
        return self
      
class Thunder:
      def __init__(self, user, password):
        self.connections = dict()
        self.chats = []
        self.thunderific = Thunderific(self)
        self.user = user
        self.password = password
        self.tasks = list()
        self.uid = str(int(random.randrange(10 ** 15, (10 ** 16) - 1)))
        self.connected = True
        #self.pm = pm.PM(user, password, access = self)

      def getConnections(self):
        return [x for x in self.connections.values()]

      def getChat(self, chat):
        chats = [x for x in self.getConnections()]
        return [x for x in chats if x.name == chat][0]

      def Start(self, prefix, chats = None):
          for x in chats:
              if x not in self.connections.keys():
                 self.connections[x] = chat.Chat(x, prefix, self)
                 self.chats.append(x)
          self.myHomies()

      def Timer(self, seconds, function, *var):
           event = threading.Event()
           def decorator(*var):
               while not event.wait(seconds): function(*var)
           thread = threading.Thread(target = decorator, args = (var))
           thread.daemon = True
           thread.start()
           self.tasks.append(event)
           return event

      def Ping(self, t):
          try:
             t.Send('')
          except:
              t.Reconnect()

      def Init(self): pass

      def myHomies(self):
            self.Init()
            self.true = True
            while self.true:
                    con = self.getConnections()
                    rs = [x.racist_websock for x in con]
                    ws = [x.racist_websock for x in con if x.wbyte != b'']
                    r, w, e = select.select(rs, ws, [], 0.1)
                    for i in r:
                         chat = [x for x in con if x.racist_websock == i][0]
                         self.thunderific.thunding(i.recv(5000), chat)
                    for i in w:
                         chat = [x for x in con if x.racist_websock == i][0]
                         i.Send(chat.wbyte)
                         chat.wbyte = b''
                         
      def Stop(self, chat):
        chat.connected = False
        self.connected = False
        [x.Disconnect() for x in self.getConnections()]
        return True

      def Join(self, chat, prefix):
          if chat not in self.connections.keys():
             self.connections[chat] = chat.Chat(chat, prefix, self)
             self.chats.append(chat)
             return True
          else:
             return False

      def Leave(self, chat):
          if chat in self.connections.keys():
             self.getChat(chat).Disconnect()
             self.chats.remove(chat)
             return True
          else:
             return False

      def Clear(self, post):
          try:
             nColor = re.search("<n(.*?)/>", post)
             fTag = re.search("<f x(.*?)>", post).group(1)
             fSize = fTag[:2]
             fFace = re.search("(.*?)=\"(.*?)\"", fTag).group(2)
             fColor = re.search(fSize+"(.*?)=\""+fFace+"\"", fTag).group(1)
          except:
                 fSize = ''
                 fColor = ''
                 fFace = ''
          return Object(**{"nColor": 000 if nColor == None else nColor, "fSize": fSize, "fColor": fColor, "fFace": fFace})

      def call(self, event, *args, **keys):
        event = "thunderific_"+event
        if hasattr(self, event):
            getattr(self, event)(*args, **keys)
            
class Thunderific:
    def __init__(self, thunder):
        self.thunder = thunder

    def thunding(self, data, chat):
        data = data.split(b"\x00")
        for x in data:
            if x:
               self.call(x, chat)

    def call(self, raw, chat):
        byt = raw.decode("latin-1").rstrip("\r\n").split(":")
        event = "thunderific_"+byt[0]
        if hasattr(self, event):
            getattr(self, event)(byt[1:], chat)

    def thunderific_bw(self, data, chat):
          bw = data[0].replace('%2C', ', ')
          chat.Actions['bw'] = bw

    def thunderific_updateprofile(self, data, chat): pass

    def thunderific_unblocklist(self, data, chat): pass

    def thunderific_mods(self, data, chat):
        mods = dict()
        for x in data[0].split(';'):
              if x != '':
                 mods[x.split(',')[0]] = x.split(',')[1]
        new = mods
        old = chat.Users['mods'] 
        for x in new:
              if x not in old:
                 self.thunder.call('new_mod', chat, x)
              else:
                 if new[x] != old[x]:
                    self.thunder.call('perms_changed', chat, x, new[x])
                 else:
                    pass
      
    def thunderific_updgroupinfo(self, data, chat):
        title = data[0].replace('%20', ' ')
        message = data[1].replace('%20', ' ')
        print('<b>%s</b> info was updated:<br/>Title: <b>%s</b><br/>Owner Message: <b>%s</b>' % (chat, title, message))

    def thunderific_u(self, data, chat): pass

    def thunderific_n(self, data, chat):
        chat.Users['count'] = int(data[0], 16)

    def thunderific_i(self, data, chat): pass

    def thunderific_delete(self, data, chat): pass
      
    def thunderific_deleteall(self, data, chat):
        pass

    def thunderific_ratelimitset(self, data, chat):
        num = ' '.join(data)
        if num == '0':
           print('Slow Mode has been turned off<br/>glhf or gtfo')
        else:
           print('Users can now post once per <b>'+num+'</b> second(s).')

    def thunderific_annc(self, data, chat):
        name = data[1]
        ann = data[2]
        chat.Say('%s: %s' % (name, ann))

    def thunderific_g_participants(self, data, ch):
        print(data)
        d = ":".join(data[1:]).split(";")
        for i in d:
            y = []
            i = i.split(':')[:-1]
            if i[-2] != "None" and i[-1] == "None":
               y.append(chat.User(i[-2]))
               ch.users.append(i[-2].lower())
               ch.Users['users'] = [x.name for x in y]

    def thunderific_participant(self, data, chat):
        d = data[0]
        if d == '0':
           if data[3].lower() in chat.users:
              chat.users.remove(data[3].lower())
              self.thunder.call('bye', chat, data[3])
        elif d == '1':
           if data[3].lower() not in chat.users:
              chat.users.append(data[3].lower())
              self.thunder.call('yo', chat, data[3])
        test = set(chat.users)
        chat.users = [x for x in test]
        chat.Users['users'] = [x for x in test]

    def thunderific_modactions(self, data, chat): pass

    def thunderific_denied(self, data, chat):
        print("unable to connect to "+chat)
        chat.Disconnect()

    def thunderific_inited(self, data, chat):
        print('[INITCON] connecting to </'+chat.name+"["+chat.server+"]>")
        chat.Send('g_participants', 'start')
        chat.Send("getmodactions", "prev", "0", "50")
        chat.Send("blocklist", "block", "", "next", "500")
        chat.Send("getbannedwords")
        chat.Send("getratelimit")
        self.thunder.call('connected', chat)
 
    def thunderific_ok(self, data, chat):
        chat.Actions['silent'] = False
        mods = dict()
        chat.Users['owner'] = data[0]
        for x in data[6].split(';'):
              if x != '':
                 mods[x.split(',')[0]] = x.split(',')[1]
        chat.Users['mods'] = mods

    def thunderific_b(self, data, chat):
        if data[1]:
                user = data[1]
        elif data[2]:
                user = "#"+data[2]
        else:
                user = "!anon"+utility.Utils().anParse(re.search("<n(.*?)/>", ":".join(data[9:])).group(1), data[3])
        saying = chat.Saying(
                 user = chat.User(user),
                 chat = chat,
                 #time = float(data[0]),
                 uid = data[3],
                 ip = data[6],
                 unid = data[4],
                 pid = data[5],
                 formats = self.thunder.cleanSaying(':'.join(data[9:])), 
                 rawContents = ':'.join(data),
                 contents = re.sub("<(.*?)>", "", ':'.join(data[9:])).replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"").replace("&apos;", "'").replace("&#39;", "'").replace("&amp;", "&")
        )
        chat.User[user.lower()] = saying
        chat.History[data[5]] = {'time': data[0], 'uid': data[3], 'unid': data[4], 'user': user, 'ip': data[6], 'saying': re.sub("<(.*?)>", "", ':'.join(data[9:])).replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"").replace("&apos;", "'").replace("&#39;", "'").replace("&amp;", "&")}
        self.thunder.call('sayings', chat.User(user), chat, saying)



