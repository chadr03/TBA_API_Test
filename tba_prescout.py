#This scrip pulls data for prescouting at the 2019 events
import requests
import json
import fnmatch
import pygal
from pygal.style import LightColorizedStyle as LCS, LightenStyle as LS

#Base TBA api url.  This will be used in all of the API calls
READ_URL_PRE = 'https://www.thebluealliance.com/api/v3/'

#This is the event that you are prescouting it determines the team list to be scouted
event_prescouting='2019ftcmp'
#This is a list of all events that you will be pulling the prescouting data from
previous_events=['2019txaus', '2019txelp', '2019txama', '2019txsan', '2019txcha', '2019txpla', '2019txgre', '2019txdel', '2019txpas', '2019txdls', '2019ftcmp']

#sets up some empty lists to be populated later in the program
previous_events_teams=[]
previous_events_matches=[]
event_prescouting_teams=[]
scout_data={}

#sets up the API request session
session = requests.Session()
#sets up the API authorization key --- this is unique for an individual and you can sign on the TBA to get one
session.headers.update({'X-TBA-Auth-Key': 'cRUNcqozsuYyku3CJYaC5rE1QAPvGWrdkknZ4UPPwc3euDq6qg8pxpKpjIhKDLWL'})

#Get team list for all teams in FIT district from TBA API
# url = 'district/2019tx/teams/keys'
# fit_teams = session.get(READ_URL_PRE + url).json()

#Gets team list for the event that is being prescouted from TBA API
url = 'event/' + event_prescouting + '/teams/keys'
event_prescouting_teams = session.get(READ_URL_PRE + url).json()


#Gets team list for each of the previous events in the previous_events list from TBA API
for event in previous_events:
    url = 'event/' + event + '/teams/keys'
    teams = session.get(READ_URL_PRE + url).json()
    previous_events_teams.append(teams)
#create dictionary of {'event': [list of teams]} for each event
previous_events_teams_dict = dict(zip(previous_events, previous_events_teams))
#print(prevoius_events_teams_dict)


#gets match data for each of the previus events in the previous_events list from TBA API
for event in previous_events:
    url = 'event/' + event + '/matches'
    matches = session.get(READ_URL_PRE + url).json()
    previous_events_matches.append(matches)
#create dictionary of {'event': [list of match information]} for each event
previous_events_matches_dict = dict(zip(previous_events, previous_events_matches))
#print(previous_events_matches_dict)

#figure out what previous events teams in current prescouting event participated and place it in dictionry called scout_data {'team_number': {'previous_events': [list of events]}}
for current_team in event_prescouting_teams:
    previous_events=[]    
    for event in previous_events_teams_dict:
        for team in previous_events_teams_dict[event]:
            if current_team == team:
                previous_events.append(event)

    scout_data[current_team] = {'previous_events': previous_events}

#print(scout_data['frc2582'])

#pull out data for each team from prevous matches
for current_team in event_prescouting_teams:
    no_qual_matches = 0
    no_hab3 = 0
    no_hab2 = 0
    no_hab1 = 0
    for event in previous_events_matches_dict:
        for match in previous_events_matches_dict[event]:
            is_in_match = False #initally assumes current_team not in current match 
            #Sets up a loop to go through all 3 teams in each alliance
            for i in range(3):
                #Determine if current_team was on blue alliance in current match
                #and determine what position
                if match['alliances']['blue']['team_keys'][i] == current_team:
                    #print(event)
                    #print(current_team)
                    #print('blue'+str(i+1))
                    alliance_color = 'blue'
                    position = i+1
                    is_in_match = True
                #Determine if current_team is in red alliance on current match
                #and determine what position
                if match['alliances']['red']['team_keys'][i] == current_team:
                    #print(event)
                    #print(current_team)
                    #print('red'+str(i+1))
                    alliance_color = 'red'
                    position = i+1
                    is_in_match = True
            #Checks to see if the current_team is in the match and it is a qualification match
            if match['comp_level'] == 'qm' and is_in_match:
                no_qual_matches = no_qual_matches + 1
                #Determines end game position
                endgame_pos = match['score_breakdown'][alliance_color]['endgameRobot'+str(position)]
                if endgame_pos == 'HabLevel3':
                    no_hab3 = no_hab3 + 1
                if endgame_pos == 'HabLevel2':
                    no_hab2 = no_hab2 + 1
                if endgame_pos == 'HabLevel1':
                    no_hab1 = no_hab1 + 1
    #Write data out to scout_data datastructure
    scout_data[current_team].update({'no_qual_matches': no_qual_matches})
    scout_data[current_team].update({'hab_end_location': [no_hab1, no_hab2, no_hab3]})
    
#print(scout_data['frc2582'])

#Create Visualizations

chart = pygal.Bar(x_label_rotation=45, show_legend=True, spacing=20, width=1500)
chart.title = 'Normalized Successful Hab Climbs in Texas Events For Compared to State Championship Teams'
chart.x_labels = event_prescouting_teams

hab3=[]
hab2=[]
hab1=[]
for team in scout_data:
    hab3.append(scout_data[team]['hab_end_location'][2]/scout_data[team]['no_qual_matches'])
    hab2.append(scout_data[team]['hab_end_location'][1]/scout_data[team]['no_qual_matches'])
    hab1.append(scout_data[team]['hab_end_location'][0]/scout_data[team]['no_qual_matches'])

chart.add('Hab 3', hab3)
chart.add('Hab 2', hab2)
chart.add('Hab 1', hab1)
chart.render_to_file('StateChampionshipHab.svg')





