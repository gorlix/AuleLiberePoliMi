"""
This class is used to build all the custom keyboards
"""
import pytz
from datetime import datetime , timedelta
from search.find_classrooms import MAX_TIME , MIN_TIME
import logging

class KeyboadBuilder:

    def __init__(self,texts , location_dict):
        """take as input the texts dict and the location dict and stores they in variables"""
        self.texts = texts
        self.location_dict = location_dict

    def initial_keyboard(self , lang):
        return [[self.texts[lang]["keyboards"]["search"]] ,[self.texts[lang]["keyboards"]["now"]] , [self.texts[lang]["keyboards"]["info"] ,self.texts[lang]["keyboards"]["preferences"] ]]

    def location_keyboard(self, lang, campus=None):
        """
        Se campus è None ritorna la lista dei campus.
        Se campus è specificato ritorna la lista delle sotto-sedi di quel campus,
        con un pulsante 'Indietro' per tornare alla lista dei campus.
        """
        cancel = self.texts[lang]["keyboards"]["cancel"]

        if campus is None:
            kb = [[cancel]]
            for c in self.location_dict:
                kb.append([c])
            return kb

        # mostra le sotto-sedi del campus selezionato
        data = self.location_dict.get(campus, {})
        sedi = data.get("sedi", {}) if isinstance(data, dict) else {}
        kb = [[cancel, "Indietro"]]
        if sedi:
            for sede in sedi:
                kb.append([sede])
        return kb

    def day_keyboard(self , lang):
        return [[self.texts[lang]["keyboards"]["cancel"]]] + [[(datetime.now(pytz.timezone('Europe/Rome')) + timedelta(days=x)).strftime("%d/%m/%Y") if x > 1 else (self.texts[lang]["keyboards"]["today"] if x == 0 else self.texts[lang]["keyboards"]["tomorrow"])] for x in range(7)]
        
    def start_time_keyboard(self ,lang):
        return [[self.texts[lang]["keyboards"]["cancel"]]] + [[x] for x in range(MIN_TIME,MAX_TIME)]

    def end_time_keyboard(self, lang , start_time ):
        return [[self.texts[lang]["keyboards"]["cancel"]]] + [[x] for x in range(start_time + 1 , MAX_TIME + 1)]

    def preference_keyboard(self,lang):
        return [[self.texts[lang]["keyboards"]["cancel"]] , [self.texts[lang]["keyboards"]["language"]] , [self.texts[lang]["keyboards"]["campus"]] , [self.texts[lang]["keyboards"]["time"]]]

    def language_keyboard(self,lang):
        return [[self.texts[lang]["keyboards"]["cancel"]]] +[[l] for l in self.texts]

    def time_keyboard(self, lang):
        return [[self.texts[lang]["keyboards"]["cancel"]]] + [[x] for x in range(1 , 9)]


