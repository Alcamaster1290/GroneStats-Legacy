import LanusStats as ls
def main():
    # Create an instance of the LanusStats class
    sofascore = ls.SofaScore()

    # Define the league and base path
    match_data = sofascore.get_match_data('https://www.sofascore.com/alianza-lima-cienciano/bWslW#id:12596037')

    if match_data is None:
        print("No match data found.")
        return

    print("Match Data:")
    for key, value in match_data.items():
                print(f"{key}: {value}")
        
if __name__ == "__main__":
    main()