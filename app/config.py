import os


token = os.getenv('SUPABASE_KEY')
url = os.getenv('SUPABASE_URL')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'sua-chave-secreta')
    SUPABASE_URL = url
    SUPABASE_KEY = token