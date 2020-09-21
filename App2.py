import  pandas as pd
import  re
import  regex
import  emoji
import  numpy as np



def startsWithDateAndTime(s):
    # regex pattern for date.(Works only for android. IOS Whatsapp export format is different. Will update the code soon
    pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9][0-9]), ([0-9]+):([0-9][0-9]) (AM|PM) -'
    result = re.match(pattern, s)
    if result:
        return True
    return False





# Finds username of any given format.
def FindAuthor(s):
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




def getDataPoint(line):
    splitLine = line.split(' - ')
    dateTime = splitLine[0]
    date, time = dateTime.split(', ')
    message = ' '.join(splitLine[1:])

    if FindAuthor(message):
        splitMessage = message.split(': ')
        author = splitMessage[0]
        message = ' '.join(splitMessage[1:])

    else:
        author = None
    return date, time, author, message



parsedData = []  # List to keep track of data so it can be used by a Pandas dataframe
# Upload your file here
conversationPath = ''  # Name of the chat file
with open(conversationPath, encoding="utf-8") as fp:
   fp.readline()  # Skipping first line of the file because contains information related to something about end-to-end encryption
   messageBuffer = []
   date, time, author = None, None, None
   while True:
       line = fp.readline()
       if not line:
           break
       line = line.strip()
       if startsWithDateAndTime(line):
           if len(messageBuffer) > 0:
               parsedData.append([date, time, author, ' '.join(messageBuffer)])
           messageBuffer.clear()
           date, time, author, message = getDataPoint(line)
           messageBuffer.append(message)

       else:
           messageBuffer.append(line)

df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'Author', 'Message'])  # Initialising a pandas Dataframe.

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


# Creates a list of unique Authors - ['Manikanta', 'Teja Kura', .........]
l = messages_df.Author.unique()

for i in range(len(l)):
  # Filtering out messages of particular user
  req_df= messages_df[messages_df["Author"] == l[i]]
  # req_df will contain messages of only one particular user
  print(f'Stats of {l[i]} -')
  # shape will print number of rows which indirectly means the number of messages
  print('Messages Sent', req_df.shape[0])
  #Word_Count contains of total words in one message. Sum of all words/ Total Messages will yield words per message
  words_per_message = (np.sum(req_df['Word_Count']))/req_df.shape[0]
  print('Words per message', words_per_message)
  #media conists of media messages
  media = media_messages_df[media_messages_df['Author'] == l[i]].shape[0]
  print('Media Messages Sent', media)
  # emojis conists of total emojis
  emojis = sum(req_df['emoji'].str.len())
  print('Emojis Sent', emojis)
  #links consist of total links
  links = sum(req_df["urlcount"])
  print('Links Sent', links)
  print()


