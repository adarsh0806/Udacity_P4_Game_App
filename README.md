#Udacity Project 4 - Rock, Paper, Scissors Game

## Set-Up Instructions:
 - Update the value of application in app.yaml to the application ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
 - Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
 - (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application to the Google cloud Platform and access via APIs Explorer.

##Game Description:
Rock-paper-scissors is a zero-sum hand game usually played between two people,
in which each player simultaneously forms one of three shapes with an outstretched hand.
These shapes are "rock" (a simple fist), "paper" (a flat hand), and "scissors"
(a fist with the index and middle fingers together forming a V). The game has only
three possible outcomes other than a tie: a player who decides to play rock will beat
another player who has chosen scissors ("rock crushes scissors") but will lose to one
who has played paper ("paper covers rock"); a play of paper will lose to a play of scissors
("scissors cut paper"). If both players throw the same shape, the game is considered a draw.

With the Rock, Paper, Scissors API, you play a "virtual" player.  To play a match, follow
these steps:
 - create a new user via the **create_user** endpoint (name and an optional email address).
 - using the **new_game** endpoint, enter a user name and choose your weapon (rock, paper
   or scissors).  The response displays the **game_result**, i.e. a win, loss or draw
   (or unknown if you enter an anything other than rock, paper or scissors).
 - repeat **new_game** with your user name to play more matches against the virtual player.

To retrieve all the user statistics from memcache, execute the **get_user_stats** endpoint.
This returns a message string containing user name and wins/losses/tie-game counts,
and a count of unknown results (where an unknown weapon was passed into new_game).

To retrieve all matches played thus far, execute the **get_all_games** endpoint (no parameters
required).  For each match, the user name, game result, and weapons chosen are returned
in the response.

To retrieve all matches for a particular user, execute the **get_games_by_user** endpoint.
The response shows all matches played by that user and details including user name, game
result, and weapons chosen.

Finally, to retrieve one single match result, execute the **get_game_by_key** using a
urlsafe game key.  The response shows the match details for the selected by key.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, weapon (case-insensitive and either "rock", "paper", or "scissors".
    - Returns: GameForm with results of game.  "game_result" indicates whether user beat or
      lost to the virtual player.  2 other results include a tie (or draw) and unknown which
      indicates an unknown weapon was specified.
    - Description: Creates a new game and result for a rock,paper, scissor match. user_name
    provided must correspond to an existing user - will raise a NotFoundException if not.  Also
    adds a task to a task queue to each user's stats.

 - **get_game_by_key**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: one Gameform with results of requested game.
    - Description: The response shows the match details for the selected by key.

- **get_all_games**
    - Path: 'game/get_all'
    - Method: GET
    - Parameters: none
    - Returns: Gameforms for every game.
    - Description: For each match, the user name, game result, and weapons chosen are
    returned in the response.

- **get_games_by_user**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user name
    - Returns: Gameforms for every game that's been played by the user.
    - Description: For each match, the user name, game result, and weapons chosen are
    returned.

- **get_user_stats**
    - Path: 'games/cache_user_stats'
    - Method: GET
    - Parameters: none
    - Returns: Each user's wins, losses, tie games and unknowns (errors).
    - Description: Returns a string containing each user's current standings.


##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores a unique game match. Associated with User model via KeyProperty.

    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, player_weapon, opponent_weapon
    message, user_name, and game_result).
 - **NewGameForm**
    - Used to create a new game (user_name, user's weapon)
 - **StringMessage**
    - General purpose String container.