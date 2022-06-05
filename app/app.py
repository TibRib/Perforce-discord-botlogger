import subprocess
import time
import random
from os.path import abspath, dirname, join
import configparser
import json

from discord_webhooks import DiscordWebhooks

last_change_path = join(dirname(abspath(__file__)), "last_change.ini")
config_path = join(dirname(abspath(__file__)), "config.ini")
sig_path = join(dirname(abspath(__file__)), "bot_signatures.json")

signatures = json.load( open(sig_path, 'r', encoding='utf-8') )

def get_funny_signature():
  return signatures[random.randint(0,len(signatures)-1)]

class Change():
  def __init__(self, change_header, content):
    split = change_header.split(" ")
    self.num = split[1]
    self.date = split[3]
    self.time = split[4]
    self.user = split[6]
    self.content = content

class PerforceLogger():
    def __init__(self, webhook_url, repository):
      self.webhook_url = webhook_url
      self.repository = repository

    def p4_fetch(self, max):
      """ Fetches the changes  """
      p4_changes = subprocess.Popen(f'p4 changes -t -m {max} -s submitted -e {self.read_num()+1} -l {self.repository}', stdout=subprocess.PIPE, shell=True)
      #Get the result from the p4 command
      return p4_changes.stdout.read().decode('ISO-8859-1')

    def regroup_changes(self, output):
      """ Makes a list with all the changes """
      changes = [] #Contains the change strings (one string per change)
      
      #If there are changes the string is not empty
      if(len(output) > 0):
        print("New changes detected")
        last_num_str = "" #this string will hold the first change number
        lines = output.splitlines() #split the strings by new line
        str_header = ""
        str_content_buffer = [] # this temporary buffer will contain each line of a change
        for l in lines:
          if(l.startswith('Change')): #If we see the word change (caracteristic of p4 changes), we close and open the buffer
            if(len(str_content_buffer) > 0): #Append the changes array with the last registered strings (closing change)
              changes.append(Change(str_header, ''.join(str_content_buffer)))
            else: # Only happens on first occurence: save the first change number as it is the most recent
              last_num_str = l.split(" ")[1]
            str_header = l
            str_content_buffer = [] # Start with a fresh buffer
          else: #Applies to other lines (content)
            str_content_buffer.append(l+"\n") #Add the current line
        # --- end of for loop ---

        #Last line closing
        changes.append(Change(str_header, ''.join(str_content_buffer)))

        # Also affect the last num
        if(last_num_str != ""): # Affect the last change number to the config file
          last_num = int(last_num_str)
          self.save_num(last_num)
      
      return changes

    def save_num(self,number):
      """Write the integer corresponding to the latest change in the dedicated file"""
      with open(last_change_path, 'w') as f:
        f.write('%d' % number)
        print("Latest change number overriden.")

    def read_num(self): #This function will return 0 in case the file is not readable
      """Read the integer corresponding to the latest change from the dedicated file"""
      try:
        with open(last_change_path, 'r') as f:
          num_str = f.read()
          return int(num_str)
      except:
        return 0

    def check_post_changes(self, signature=False):
      """ Posts each changes to the Discord server using the provided webhook. """
      changes_as_str = self.p4_fetch(max=7)
      changes = self.regroup_changes(changes_as_str)
      for payload in reversed(changes):
        if(payload != ''):
          user = payload.user.split("@")[0]
          message = DiscordWebhooks(self.webhook_url)
          message.set_author(name=f"@{user} : new submit" )
          message.set_content(color=0x51D1EC, description= f"`#{payload.num}`  - {payload.time} {payload.date} \n```fix\n{payload.content.lstrip()}``` ")
          if(signature):
            signature = get_funny_signature()
            message.set_footer(text=f"{signature}", ts=True)
          message.send()
          print("Sent payload")
        time.sleep(1) #sleep 1 second to avoid sending too much messages at once

if __name__ == "__main__":
  """ Read config parameters and perform the checks """
  config = configparser.ConfigParser()
  config.read(config_path)

  #Read config
  DISCORD_WEBHOOK_URL = config['Discord']['webhook']
  P4_TARGET = config['Perforce']['target']

  MAX_CHANGES = config.getint('ApplicationSettings','max_changes')
  ALLOW_SIGNATURE = config.getboolean('ApplicationSettings', 'enable_signature')

  #Init logger
  logger = PerforceLogger(DISCORD_WEBHOOK_URL, repository=P4_TARGET)

  #Perform checks - this line can be looped with a time.sleep(SECONDS) in case you don't use a scheduler
  logger.check_post_changes(signature=ALLOW_SIGNATURE)