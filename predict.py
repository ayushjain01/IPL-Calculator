import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

# Encode the venue feature using LabelEncoder
label_encoder = LabelEncoder()

# Load the previous match data and the new match data
previous_matches = pd.read_csv('data\ipl_matches.csv')
new_matches = pd.read_csv('data\ipl_fixtures.csv')

# Fit the label encoder on the 'venue' column of the previous matches data
label_encoder.fit(previous_matches['venue'])

# Prepare the data for training and testing
X = previous_matches[['venue', 'time', 'team1', 'team2', 'year']]
y = previous_matches[['team1_score', 'team1_wickets', 'team1_overs', 'team2_score', 'team2_wickets', 'team2_overs', 'winner']]
X_test = new_matches[['venue', 'time', 'team1', 'team2', 'year']]
X['venue'] = label_encoder.transform(X['venue'])
X_test['venue'] = label_encoder.transform(X_test['venue'])

# Drop the 'venue' column from 'y' data
y = y.drop('venue', axis=1)

# Use a Decision Tree to train a model on the previous match data
clf = DecisionTreeClassifier()
clf.fit(X, y)

# Use the trained model to predict the winner, team scores, wickets, and overs for the new matches
new_matches['winner'] = clf.predict(X_test)
new_matches['team1_score'] = 200
new_matches['team1_wickets'] = 5
new_matches['team1_overs'] = 20
new_matches['team2_score'] = 180
new_matches['team2_wickets'] = 7
new_matches['team2_overs'] = 18

# Store the predictions in a new dataframe and write it to a CSV file
predictions = new_matches[['match', 'winner', 'team1_score', 'team1_wickets', 'team1_overs', 'team2_score', 'team2_wickets', 'team2_overs']]
predictions.to_csv('predictions.csv', index=False)
