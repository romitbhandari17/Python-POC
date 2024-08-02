import json
import os
from prompts import assistant_instructions


def create_assistant(client):
  assistant_file_path = 'assistant.json'

  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    # Folder containing the files
    folder_path = 'files'

    # List all files in the folder (assuming all entities in the folder are files)
    file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

    # Create and upload files, storing their IDs
    file_ids = []
    for path in file_paths:
        print(f"Processing file: {path}")
        file = client.files.create(file=open(path, "rb"), purpose='assistants')
        file_ids.append(file.id)

    # Now use the file IDs in creating the assistant
    assistant = client.beta.assistants.create(
        instructions=assistant_instructions,
        model="gpt-4-1106-preview",
        tools=[{
            "type": "retrieval"  # This adds the knowledge base as a tool
        }],
        file_ids=file_ids)  # Use the list of file IDs here

    # Create a new assistant.json file to load on future runs
    with open(assistant_file_path, 'w') as file:
        json.dump({'assistant_id': assistant.id}, file)
        print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id


def search_university_info(university_name):

  file_path_2023 = 'json-files/World University Rankings Rankings 2023.json'
  file_path_2024 = 'json-files/World University Rankings Rankings 2024.json'
  """
    Search for a university in the 2023 and 2024 datasets and return its overall score, rank,
    and the scores and ranks for each indicator in a JSON format.
    """
  # Load the JSON files
  with open(file_path_2023, 'r') as file_2023:
    data_2023 = json.load(file_2023)
  with open(file_path_2024, 'r') as file_2024:
    data_2024 = json.load(file_2024)

  result = {"2023": {}, "2024": {}}

  # Process each dataset
  for year, data in zip(['2023', '2024'], [data_2023, data_2024], strict=True):
    for university in data['score_nodes']:
      if university_name.lower() in university['university_name'].lower():
        indicators_result = {}
        for indicator in university['scores']:
          indicator_name = indicator['indicator_name']
          indicators_result[indicator_name] = {
              'rank': indicator['rank'],
              'score': indicator['score']
          }
        result[year] = {
            "name": university['university_name'],
            "rank": university['rank'],
            "overall_score": university['score'],
            "indicators": indicators_result
        }

  return result
