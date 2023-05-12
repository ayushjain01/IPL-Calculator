# IPL Calculator 

[This](https://github.com/ayushjain01/IPL-Calculator/blob/master/predict_points.py) project (currently) calculates the chances of Royal Challengers Bangalore (RCB) qualifying for the playoffs of the Indian Premier League (IPL) based on various scenarios. It also prints the points table for every scenario. Checkout [output.txt](output.txt) to view a sample output of this script.
 
## 🚀 Getting Started

To run the script, you need to have Python 3.11.x installed. You can download it from [here](https://www.python.org/downloads/).

1. Clone this repository 
```git clone https://github.com/ayushjain01/IPL-Calculator.git```
2. Navigate to the directory 
```cd IPL-Calculator```
3. Install the dependencies
```pip install -r requirements.txt```
4. Run the script
```python predict_points.py```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## 💡 Acknowledgements

This code was developed by [Ayush Jain](https://github.com/ayushjain01)  as part of a personal project. It is not affiliated with any official IPL or cricketing organization. Feel free to use and modify the code as per your requirements.

## 📌 Note

This script manually assigns the net run rate (NRR) value after every game as +- 0.05 which is not accurate. A better approach would be to calculate the actual NRR based on the runs scored and conceded by each team in every match. This will be added in future updates.

## 🔮 Future Plans

Soon, I plan to create a full-fledged web application that will scrape the IPL official website to get details of upcoming matches and store previous match data and automatically predict match winners and provide the results. This webapp will also allow users to predict the winners and compare their results with the actual outcomes💻
