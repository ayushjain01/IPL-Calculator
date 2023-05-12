team_list_1 = ['RCB', 'CSK', 'DC','RCB']
team_list_2 = ['GT', 'MI', 'PBKS', 'DC']
possible_winners = []

for i in range(2**len(team_list_1)):
    winner = []
    for j in range(len(team_list_1)):
        if i & (1<<j):
            winner.append(team_list_2[j])
        else:
            winner.append(team_list_1[j])
    possible_winners.append(winner)

print("Possible winners:", possible_winners)
