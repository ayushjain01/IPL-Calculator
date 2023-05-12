sort_values(table)
        top4 = table[:4]
        for team in top4:
            if team[0] == "RCB":            # printing all tables where RCB qualifies
                print_table(table)
                exit(0)