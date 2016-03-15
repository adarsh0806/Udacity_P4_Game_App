#Udacity Project 4 - Rock, Paper, Scissors Game

## Set-Up Instructions:


##Game Description:
Rock-paper-scissors is a zero-sum hand game usually played between two people,
in which each player simultaneously forms one of three shapes with an outstretched hand.
These shapes are "rock" (a simple fist), "paper" (a flat hand), and "scissors"
(a fist with the index and middle fingers together forming a V). The game has only
three possible outcomes other than a tie: a player who decides to play rock will beat
another player who has chosen scissors ("rock crushes scissors") but will lose to one
who has played paper ("paper covers rock"); a play of paper will lose to a play of scissors
("scissors cut paper"). If both players throw the same shape, the game is considered a draw.


##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
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
    - Parameters: user_name, min, max, attempts
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Min must be less than
    max. Also adds a task to a task queue to update the average moves remaining
    for active games.


##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)
 - **StringMessage**
    - General purpose String container.