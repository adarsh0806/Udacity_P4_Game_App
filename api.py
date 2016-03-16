"""api.py - Create and configure the Rock, Paper, Scissors
API exposing the resources.
This file includes all of the game’s logic."""

import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import User, Game
from models import UNKNOWN, DRAW
from models import StringMessage, NewGameForm, GameForm, GameForms
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1), )
GET_ALL_GAMES_REQUEST = endpoints.ResourceContainer()
GET_GAMES_BY_USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1), )
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_USER_STATS = 'USER_STATS'


@endpoints.api(name='rock_paper_scissors', version='v1')
class RockPaperScissorsApi(remote.Service):
    """Rock, Paper, Scissors Game API"""

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
        """Creates new rock, paper, scissors game and result.
        The player passes in their name and choice of rock,
        paper, or scissors, and the virtual player randomly
        selects a weapon.  The result (win,lose,draw)
        is determined."""
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
        taskqueue.add(url='/tasks/cache_user_stats')

        if game.game_result == DRAW:
            msg = "it's a"
        elif game.game_result == UNKNOWN:
            msg = 'game state is'
        else:
            msg = 'you'
        return game.to_form('You selected {}, your '
                            'opponent selected {} -- '
                            '{} {}'.format(game.player_weapon,
                                           game.opponent_weapon,
                                           msg,
                                           game.game_result))

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game_by_key',
                      http_method='GET')
    def get_game_by_key(self, request):
        """Return one game by urlsafe_game_key."""

        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if not game:
            raise endpoints.NotFoundException('Game not found!')

        # Add a descriptive message to response.
        if game.game_result == 'win':
            msg = "You won!"
        elif game.game_result == 'lose':
            msg = "Sorry, the virtual player won this round."
        elif game.game_result == 'draw':
            msg = "The game was a draw."
        else:
            msg = "Unknown result.  Perhaps you chose a weapon we don't " \
                  "know about."

        u_key = game.user
        user = u_key.get()
        return game.to_form('{} chose {} and the '
                            'virtual player chose '
                            '{}. {}'.format(user.name,
                                            game.player_weapon,
                                            game.opponent_weapon,
                                            msg))

    @endpoints.method(request_message=GET_ALL_GAMES_REQUEST,
                      response_message=GameForms,
                      path='game/get_all',
                      name='get_all_games',
                      http_method='GET')
    def get_all_games(self, request):
        """Return all game results."""
        return GameForms(items=[game.to_form('N/A') for game in Game.query()])

    @endpoints.method(request_message=GET_GAMES_BY_USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_games_by_user',
                      http_method='GET')
    def get_game(self, request):
        """Return a user's game history."""

        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')

        games = Game.query(Game.user == user.key)
        return GameForms(items=[game.to_form('N/A') for game in games])

    @endpoints.method(response_message=StringMessage,
                      path='games/cache_user_stats',
                      name='get_user_stats',
                      http_method='GET')
    def get_user_stats(self, request):
        """Get the cached stats for all users."""
        return StringMessage(message=memcache.get(MEMCACHE_USER_STATS) or
                                     'Nothing found in memcache')

    @staticmethod
    def _cache_user_stats():
        """Populates memcache with each NEW GAME. Stats include wins,
        losses, ties, and unknown (if front-end send a weapon we don't
        know about, this is considered unknown).  Not really an efficient
        use of memcache but this is for project demonstration purposes mainly.
        """

        users = User.query()
        msg = ''
        # Build memcache string that details stats for each player.
        for user in users:
            games = Game.query(Game.user == user.key)
            wins = losses = ties = unknown = 0
            for game in games:
                if game.game_result == 'win':
                    wins += 1
                elif game.game_result == 'lose':
                    losses += 1
                elif game.game_result == 'draw':
                    ties += 1
                else:
                    unknown += 1

            one_player = "{} has {} {}, {} {}, {} {}, " \
                         "and {} " \
                         "unknown {}.  "\
                .format(user.name,
                        wins,
                        "win" if wins == 1 else "wins",
                        losses,
                        "loss" if losses == 1 else "losses",
                        ties,
                        "draw" if ties == 1 else "tie games",
                        unknown,
                        "result" if unknown == 1 else "results"
                        )

            msg += one_player

        memcache.set(MEMCACHE_USER_STATS, msg)

api = endpoints.api_server([RockPaperScissorsApi])