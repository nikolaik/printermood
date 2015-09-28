import indicoio
from settings import INDICO_API_KEY

indicoio.config.api_key = INDICO_API_KEY
filepath = 'not_nice_n.png'
print(indicoio.fer(filepath))
