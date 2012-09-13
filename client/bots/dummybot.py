# vim: ts=4 et sw=4 sts=4

from common.bot import SimpleStatusHandler,ExhaustiveSearchBot,Bot

"""Dumbest bot that can play the game"""
class DummyBot(SimpleStatusHandler, ExhaustiveSearchBot, Bot):
    pass
