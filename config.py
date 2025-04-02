env_vars = {
  # Get From my.telegram.org
  "API_HASH", "4e81464b29d79c58d0ad8a0c55ece4a5",
  # Get From my.telegram.org
  "API_ID", "20718334",
  #Get For @BotFather
  "BOT_TOKEN", "7403693425:AAHaGlkp-zNNPvNeO62xWqwmsRI5apY0Dcs",
  # Get For tembo.io
  "DATABASE_URL_PRIMARY": "",
  # Logs Channel Username Without @
  "CACHE_CHANNEL": "+BTzjufUdN7ZmZGI1",
  # Force Subs Channel username without @
  "CHANNEL", "+BTzjufUdN7ZmZGI1",
  # {chap_num}: Chapter Number
  # {chap_name} : Manga Name
  # Ex : Chapter {chap_num} {chap_name} @Manhwa_Arena
  "FNAME", "[AS] {chap_num} {chap_name} @Manga_x_society"
  # Put Thumb Link 
  "THUMB", "https://envs.sh/jlx.png"
}

dbname = env_vars.get('DATABASE_URL_PRIMARY') or env_vars.get('DATABASE_URL') or 'sqlite:///test.db'

if dbname.startswith('postgres://'):
    dbname = dbname.replace('postgres://', 'postgresql://', 1)
    
