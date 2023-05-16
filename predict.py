import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

# Step 1: Load and preprocess the data
data = pd.read_csv('data/ipl_matches.csv')

# Drop rows with None values
data = data.dropna()

# Extract relevant features and target variables
X_teams = data[['team1', 'team2']]
X_venue = data[['venue']]
y_scores1 = data['team1_score']
y_wickets1 = data['team1_wickets']
y_overs1 = data['team1_overs']
y_scores2 = data['team2_score']
y_wickets2 = data['team2_wickets']
y_overs2 = data['team2_overs']
y_winnerL = data['winner']

# Perform one-hot encoding on team names and venue
encoder_teams = OneHotEncoder(sparse=False, handle_unknown='ignore')
X_teams_encoded = encoder_teams.fit_transform(X_teams)

encoder_venue = OneHotEncoder(sparse=False, handle_unknown='ignore')
X_venue_encoded = encoder_venue.fit_transform(X_venue)

y_winnerL = OneHotEncoder(sparse=False, handle_unknown='ignore')
y_winner = y_winnerL.fit_transform(y_winnerL)
# Concatenate the encoded features
X_encoded = pd.concat([pd.DataFrame(X_teams_encoded), pd.DataFrame(X_venue_encoded)], axis=1)

# Step 2: Train the model for score prediction
model_scores1 = LinearRegression()
model_scores1.fit(X_encoded, y_scores1)

# Step 3: Train the model for wicket prediction
model_wickets1 = LinearRegression()
model_wickets1.fit(X_encoded, y_wickets1)

# Step 4: Train the model for overs prediction
model_overs1 = LinearRegression()
model_overs1.fit(X_encoded, y_overs1)

# Step 5: Train the model for the second team's score prediction
model_scores2 = LinearRegression()
model_scores2.fit(X_encoded, y_scores2)

# Step 6: Train the model for the second team's wicket prediction
model_wickets2 = LinearRegression()
model_wickets2.fit(X_encoded, y_wickets2)

# Step 7: Train the model for the second team's overs prediction
model_overs2 = LinearRegression()
model_overs2.fit(X_encoded, y_overs2)

# Step 8: Train the model for the winner prediction
model_winner = LinearRegression()
model_winner.fit(X_encoded, y_winner)

# Step 9: Predict the values for a new dataset
new_data = pd.read_csv('data/ipl_fixtures.csv')
new_data = new_data.dropna()  # Drop rows with None values from the new dataset
new_X_teams = new_data[['team1', 'team2']]
new_X_venue = new_data[['venue']]

new_X_teams_encoded = encoder_teams.transform(new_X_teams)
new_X_venue_encoded = encoder_venue.transform(new_X_venue)

new_X_encoded = pd.concat([pd.DataFrame(new_X_teams_encoded), pd.DataFrame(new_X_venue_encoded)], axis=1)

predicted_scores1 = model_scores1.predict(new_X_encoded)
predicted_wickets1 = model_wickets1.predict(new_X_encoded)
predicted_overs1 = model_overs1.predict(new_X_encoded)
predicted_scores2 = model_scores2.predict(new_X_encoded)
predicted_wickets2 = model_wickets2.predict(new_X_encoded)
predicted_overs2 = model_overs2.predict(new_X_encoded)
predicted_winner = model_winner.predict(new_X_encoded)

# Convert the predicted values to integers
predicted_scores1 = predicted_scores1.astype(int)
predicted_wickets1 = predicted_wickets1.astype(int)
predicted_overs1 = predicted_overs1.astype(int)
predicted_scores2 = predicted_scores2.astype(int)
predicted_wickets2 = predicted_wickets2.astype(int)
predicted_overs2 = predicted_overs2.astype(int)

# Print the predictions
for i in range(len(new_X)):
    print(f"Match {i+1}:")
    print(f"Team 1: Score: {predicted_scores1[i]}, Wickets: {predicted_wickets1[i]}, Overs: {predicted_overs1[i]}")
    print(f"Team 2: Score: {predicted_scores2[i]}, Wickets: {predicted_wickets2[i]}, Overs: {predicted_overs2[i]}")
    print(f"Predicted winner: {predicted_winner}")
