import os
from time import sleep
from packaging import version
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
from dotenv import load_dotenv
import requests
import csv

# Load the .env file
load_dotenv()

# Check OpenAI version is correct
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
OPENAI_API_KEY =  os.getenv('OPENAI_API_KEY')
if current_version < required_version:
  raise ValueError(f"Error: OpenAI version {openai.__version__}"
                   " is less than the required version 1.1.1")
else:
  print("OpenAI version is compatible.")

# Start Flask app
app = Flask(__name__)

# Init client
client = OpenAI(
    api_key=OPENAI_API_KEY)  # should use env variable OPENAI_API_KEY in secrets (bottom left corner)

# Generate response
@app.route('/createCSVFromRankings', methods=['GET'])
def createCSVFromRankings():

  print("Inside createCSVFromRankings function")
  # URL of the API endpoint
  url = 'https://topuniversities.com/rankings/endpoint?nid=3937573&page=0&items_per_page=500&tab=indicators'
  print("calling GET url=",url)

  # Make the GET request to the API
  response = requests.get(url)
  if response.status_code == 200:
      # Parse the JSON response
      data = response.json()
      
      # Identify all unique indicators
      indicators = set()
      for node in data['score_nodes']:
          for score in node['scores']:
              indicators.add(score['indicator_name'])

      # Create header columns
      columns = ['University Name', 'Path', 'Region', 'Country','City',	'logo',	'Overall Score',	'Overall Rank',	'stars', 'dagger',	'redact'

] + [f"{indicator} Rank" for indicator in indicators] + [f"{indicator} Score" for indicator in indicators]

      # Prepare data rows
      rows = []
      for node in data['score_nodes']:
          row = {
              'University Name': node['title'],
              'Path': node['path'],
              'Region': node['region'],
              'Country': node['country'],
              'City': node['city'],
              'logo': node['logo'],
              'Overall Score': node['overall_score'],	
              'Overall Rank': node['rank'],	
              'stars': node['stars'], 
              'dagger': node['dagger'],	
              'redact': node['redact']
          }
          
          # Initialize ranks and scores with empty values
          for indicator in indicators:
              row[f"{indicator} Rank"] = None
              row[f"{indicator} Score"] = None
          
          # Fill in rank and score values for each indicator
          for score in node['scores']:
              indicator_name = score['indicator_name']
              row[f"{indicator_name} Rank"] = score['rank']
              row[f"{indicator_name} Score"] = score['score']
          
          rows.append(row)

      # Write to CSV file
      csv_file = 'rankings-files/QS-Sustainability-rankings-2024-1-500.csv'
      with open(csv_file, 'w', newline='', encoding='utf-8') as file:
          writer = csv.DictWriter(file, fieldnames=columns)
          writer.writeheader()
          writer.writerows(rows)

      print(f"CSV file '{csv_file}' created successfully.")
      return jsonify({"response": "CSV file created successfully"})
  else:
      print("Failed to retrieve data. Status code:", response.status_code)
      return jsonify({"response": "Failed to retrieve data. Status code:"+ response.status_code})


# Run server
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
