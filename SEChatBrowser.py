#from mechanize import *
import json
from BeautifulSoup import *
import requests
import sys
import re
import websocket
import threading



class SEChatBrowser:
  def __init__(self):
    #self.b=Browser()
    #self.b.set_handle_robots(False)
    #self.b.set_proxies({})
    self.session=requests.Session()
    self.chatfkey=""
    self.chatroot="http://chat.stackexchange.com"
    self.sockets={'false':'true'}
  def loginSEOpenID(self,user,password):
    fkey=self.getSoup("https://openid.stackexchange.com/account/login").find('input',{"name":"fkey"})['value'] 
    logindata={"email":user,"password":password,"fkey":fkey}
    return self.session.post("https://openid.stackexchange.com/account/login/submit",data=logindata,allow_redirects=True)
  
  def loginSECOM(self):
    fkey=self.getSoup("http://stackexchange.com/users/login?returnurl=%2f").find('input',{"name":"fkey"})['value']
    data={"fkey":fkey,"oauth_version":"","oauth_server":"","openid_identifier":"https://openid.stackexchange.com/"}
    return self.session.post("http://stackexchange.com/users/authenticate",data=data,allow_redirects=True)
  def loginMSO(self):
    fkey=self.getSoup("http://meta.stackoverflow.com/users/login?returnurl=%2f").find('input',{"name":"fkey"})['value']
    data={"fkey":fkey,"oauth_version":"","oauth_server":"","openid_identifier":"https://openid.stackexchange.com/"}
    self.session.post("http://meta.stackoverflow.com/users/authenticate",data=data,allow_redirects=True)  
    self.chatroot="http://chat.meta.stackoverflow.com"
    self.updateFkey()
  def loginSO(self):
    fkey=self.getSoup("http://stackoverflow.com/users/login?returnurl=%2f").find('input',{"name":"fkey"})['value']
    data={"fkey":fkey,"oauth_version":"","oauth_server":"","openid_identifier":"https://openid.stackexchange.com/"}
    self.session.post("http://stackoverflow.com/users/authenticate",data=data,allow_redirects=True)  
    self.chatroot="http://chat.stackoverflow.com"
    self.updateFkey()
  def loginChatSE(self):
    chatlogin=self.getSoup("http://stackexchange.com/users/chat-login")
    authToken=chatlogin.find('input',{"name":"authToken"})['value']
    nonce=chatlogin.find('input',{"name":"nonce"})['value']
    data={"authToken":authToken,"nonce":nonce}
    rdata=self.session.post("http://chat.stackexchange.com/login/global-fallback",data=data,allow_redirects=True,headers={"Referer":"http://stackexchange.com/users/chat-login"}).content
    fkey=BeautifulSoup(rdata).find('input',{"name":"fkey"})['value']
    self.chatfkey=fkey
    self.chatroot="http://chat.stackexchange.com"
    return rdata
  
  def updateFkey(self):
    try:
      fkey=self.getSoup(self.getURL("chats/join/favorite")).find('input',{"name":"fkey"})['value']
      if(fkey!=None and fkey!=""):
        self.chatfkey=fkey
        return True
    except Exception as e:
        print "Error updating fkey"
    return False
  
  def postSomething(self,relurl,data):
    data['fkey']=self.chatfkey
    return self.post(self.getURL(relurl),data).content
  def getSomething(self,relurl):
    return self.session.get(self.getURL(relurl)).content
  
  def getSoup(self,url):
    return BeautifulSoup(self.session.get(url).content)
  def initSocket(self,roomno,func):
    eventtime=json.loads(self.postSomething("/chats/"+str(roomno)+"/events",{"since":0,"mode":"Messages","msgCount":100}))['time']
    print eventtime
    wsurl=json.loads(self.postSomething("/ws-auth",{"roomid":roomno}))['url']+"?l="+str(eventtime)
    print wsurl
    self.sockets[roomno]={"url":wsurl}
    return
    self.sockets[roomno]['ws']=websocket.create_connection(wsurl)
    def runner():
        #look at wsdump.py later to handle opcodes
        while (True):
            a=ws.recv()
            if(a != None and a!=""):
                func(a)
    print "ready"
    self.sockets[roomno]['thread']=threading.Thread(target=runner)
    self.sockets[roomno]['thread'].start()
    print "r2"
  def post(self,url,data):
    return self.session.post(url,data)
  def getURL(self,rel):
    if(rel[0]!="/"):
      rel="/"+rel
    return self.chatroot+rel
