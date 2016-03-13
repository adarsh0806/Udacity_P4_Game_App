"""api.py - Create and configure the "Rock, Paper, Scissors" API exposing the resources.  This file includes all of the game’s logic."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, ScoreForms, NewGameForm, GameForm
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_WEAPON_WIN_LOSS = 'WEAPON_WIN_LOSS'

@endpoints.api(name='rock_paper_scissors', version='v1')
class RockPaperScissorsApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key, request.weapon)
        except ValueError:
            raise endpoints.BadRequestException('Maximum must be greater '
                                                'than minimum!')

        # Use a task queue to update the user wins.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_user_wins')
        return game.to_form('Good luck playing Rock, Paper, Scissors!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_games',
                      http_method='GET')
    def get_games(self, request):
        """Return the most-recent game results."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            # Should not get here as winner is decided within a new game (i.e. hand throw-down).
            return game.to_form('Time to play!')
        else:
            raise endpoints.NotFoundException('Game not found!')
        return GameForm(items=[game.to_form() for game in Game.query()])

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_games(self, request):
        """Return all games"""
        return GameForms(items=[game.to_form() for game in Game.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_WEAPON_WIN_LOSS) or '')

    @staticmethod
    def _cache_user_wins():
        """Populates memcache with the number of wins per user"""
        #count = len(games)
        #total_attempts_remaining = sum([game.attempts_remaining
        #                            for game in games])
        #average = float(total_attempts_remaining)/count
        memcache.set(MEMCACHE_WEAPON_WIN_LOSS,
                    'The number of win is *TODO*')


api = endpoints.api_server([RockPaperScissorsApi])