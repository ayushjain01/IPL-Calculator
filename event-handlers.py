
def handle_click():
    for i in range(len(pos)):
        row = row + f"""
    <tr>
        <td>0</td>
        <td>{team[i]}</td>
        <td>{gamesP[i]}</td>
        <td>{gamesW[i]}</td>
        <td>{gamesL[i]}</td>
        <td>{gamesNR[i]}</td>
        <td>{nrr[i]}</td>
        <td>{pts[i]}</td>
    </tr>
    """
    pointsbody = Element("points-table")
    pointsbody.element.innerHTML = row