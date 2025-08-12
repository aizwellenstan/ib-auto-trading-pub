import pandas as pd
import requests
from io import StringIO

# Define the URL of the CSV file
url = "https://cdn.cboe.com/resources/options/volume_and_call_put_ratios/totalpc.csv"

# Download the CSV file content
response = requests.get(url)
content = StringIO(response.text)

# Read the CSV content into a DataFrame
df = pd.read_csv(content)

# Display the DataFrame
npArr = df.to_numpy()
print(npArr)
