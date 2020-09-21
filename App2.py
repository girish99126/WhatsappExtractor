import  pandas as pd
import  re
import  regex
import  emoji
import  numpy as np




def FindName(s):
    """
    This function is about to extract the name from a message 
    there are different name in our contacts
    This regular expression from both stackoverflow and  "https://regexr.com/" 
    
    """
    patterns = [
        '([\w]+):',  # First Name
        '([\w]+[\s]+[\w]+):',  # First Name + Last Name
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',  # First Name + Middle Name + Last Name
        '([+]\d{2} \d{5} \d{5}):',  # Mobile Number (India)
        '([+]\d{2} \d{3} \d{3} \d{4}):',  # Mobile Number (US)
        '([\w]+)[\u263a-\U0001f999]+:',  # Name and Emoji
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False


def checkStartDateTime(s):
    """
    This function is about check whether the function is starts with dateTIme
    because if the line is not start with dateTime it means a multiple message

    so this function helps us to find whether this is new line or muliple line message

    we get this pattern from "https://regexr.com/" here you find and easy to visuvalize the
    expressoion
    """

    pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9][0-9]), ([0-9]+):([0-9][0-9]) (AM|PM) -'
    result = re.match(pattern, s)  # this function check the string start with the pattern or not
    if result:
        return True
    return False


def extractData(line):
    """
    This  function is very imp to extract the data and stored in varibles
    Example : "7/20/20, 11:56 PM - Name: Hand position changed"
    First split the string by "-" so we get two parts datetime and namemessage
    like this ["7/20/20, 11:56 PM ","Name: Hand position changed"]
    datetime = splitline[0]
    again split the date and time base on "," 
    now extract the name and messgae from the string
    "Name: Hand position changed" base on ":"
    we can separate the name and message


    """
    
    splitLine = line.split(' - ')
    dateTime = splitLine[0]
    date, time = dateTime.split(', ')
    message = ' '.join(splitLine[1:])

    if FindName(message):
        splitMessage = message.split(': ')
        name = splitMessage[0]
        message = ' '.join(splitMessage[1:])

    else:
        name = None
    return date, time, name, message



parsedData = []
#fie name
chat = 'cse6.txt'  # chat file
with open(chat, encoding="utf-8") as fp:
   fp.readline()  # Skipping first line of the file because contains information related to something about end-to-end encryption
   messageBuffer = []
   date, time, name = None, None, None
   while True:
       line = fp.readline()
       if not line:
           break
       line = line.strip()
       if checkStartDateTime(line):
           if len(messageBuffer) > 0:
               parsedData.append([date, time, name, ' '.join(messageBuffer)])
           messageBuffer.clear()
           date, time, name, message = extractData(line)
           messageBuffer.append(message)

       else:
           messageBuffer.append(line)

df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'name', 'Message'])  # Initialising a pandas Dataframe.

print(df["Date"])
df["Date"] = pd.to_datetime(df["Date"])






def split_count(text):

   emoji_list = []
   data = regex.findall(r'\X', text)
   for word in data:
       if any(char in emoji.UNICODE_EMOJI for char in word):
           emoji_list.append(word)

   return emoji_list

total_messages = df.shape[0]
media_messages = df[df['Message'] == '<Media omitted>'].shape[0]
df["emoji"] = df["Message"].apply(split_count)
emojis = sum(df['emoji'].str.len())
URLPATTERN = r'(https?://\S+)'
df['urlcount'] = df.Message.apply(lambda x: re.findall(URLPATTERN, x)).str.len()
links = np.sum(df.urlcount)


print(total_messages,media_messages,emojis,links)




media_messages_df = df[df['Message'] == '<Media omitted>']
messages_df = df.drop(media_messages_df.index)


messages_df['Letter_Count'] = messages_df['Message'].apply(lambda s : len(s))
messages_df['Word_Count'] = messages_df['Message'].apply(lambda s : len(s.split(' ')))


# Creates a list of unique names - ['Manikanta', 'Teja Kura', .........]
l = messages_df.name.unique()

for i in range(len(l)):
  # Filtering out messages of particular user
  req_df= messages_df[messages_df["name"] == l[i]]
  # req_df will contain messages of only one particular user
  print(f'Stats of {l[i]} -')
  # shape will print number of rows which indirectly means the number of messages
  print('Messages Sent', req_df.shape[0])
  #Word_Count contains of total words in one message. Sum of all words/ Total Messages will yield words per message
  words_per_message = (np.sum(req_df['Word_Count']))/req_df.shape[0]
  print('Words per message', words_per_message)
  #media conists of media messages
  media = media_messages_df[media_messages_df['name'] == l[i]].shape[0]
  print('Media Messages Sent', media)
  # emojis conists of total emojis
  emojis = sum(req_df['emoji'].str.len())
  print('Emojis Sent', emojis)
  #links consist of total links
  links = sum(req_df["urlcount"])
  print('Links Sent', links)
  print()


