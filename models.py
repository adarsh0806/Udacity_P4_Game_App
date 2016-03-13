"""models.py - This file contains the class definitions for the Datastore
entities used by the Rock, Paper, Scissors game."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

weapons = ['rock','paper','scissors']

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    player_weapon = ndb.StringProperty(required=True)
    opponent_weapon = ndb.StringProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user, player_weapon):
        """Creates and returns a new game"""
        x = random.choice(range(0,2))
        opponent_weapon = weapons[x]
        print user
        print player_weapon
        print opponent_weapon
        game = Game(user=user,
                    player_weapon=player_weapon,
                    opponent_weapon=opponent_weapon
                   )
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.player_weapon = self.player_weapon
        form.opponent_weapon = self.opponent_weapon
        form.message = message
        return form


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date))


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    weapon = messages.StringField(2, required=True)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    player_weapon = messages.StringField(2, required=True)
    opponent_weapon = messages.StringField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
