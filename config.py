env_vars = {
  # Get From my.telegram.org
  "API_HASH": "4e81464b29d79c58d0ad8a0c55ece4a5",
  # Get From my.telegram.org
  "API_ID": "20718334",
  #Get For @BotFather
  "BOT_TOKEN": "7403693425:AAHaGlkp-zNNPvNeO62xWqwmsRI5apY0Dcs",
  # Get For tembo.io
  "DATABASE_URL_PRIMARY": "",
  # Logs Channel Username Without @
  "CACHE_CHANNEL": "https://t.me/+BTzjufUdN7ZmZGI1",
  # Force Subs Channel username without @
  "CHANNEL": "animes_sub_society",
  # {chap_num}: Chapter Number
  # {chap_name} : Manga Name
  # Ex : Chapter {chap_num} {chap_name} @Manhwa_Arena
  "FNAME": "[AS] [C{chap_num}] @manga_x_society",
  # Put Thumb Link 
  "THUMB": "https://telegra.ph/file/4fa0c335758032891ce65-345c9eeefd08a74374.jpg"
}

dbname = env_vars.get('DATABASE_URL_PRIMARY') or env_vars.get('DATABASE_URL') or 'sqlite:///test.db'

if dbname.startswith('postgres://'):
    dbname = dbname.replace('postgres://', 'postgresql://', 1)
