from openai import OpenAI
OPENAI_API_KEY = os.eviron.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def ask_weather_question(user_question, weather_info):
    prompt = f"""
Your job is to assist users with answering any weather related questions

Be certain that the users are only using questions within weather data below
make sure that the questions are simple adn easy to understand and answer
do NOT make up any information that is not in the weather data

User question:
{user_question}

Weather data:
Location: {weather_info['Location']}
Current Temperature: {weather_info['Current Temperature']}
Feels like: {weather_info['Feels like']}
Condition: {weather_info['Condition']}
Windspeed: {weather_info['Windspeed']}
